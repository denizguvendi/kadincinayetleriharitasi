import json
import math
import requests


def web_mercator_to_lat_lng(x, y):
  lng = (x / 20037508.34) * 180.0
  lat = (y / 20037508.34) * 180.0
  lat = (
      180
      / math.pi
      * (
          math.atan(math.exp(lat * math.pi / 180.0)) * 2
          - math.pi / 2
      )
  )
  return lat, lng


def fetch_all_arcgis_records():
  base_url = "https://services6.arcgis.com/Ht6KMWZ74NMm1G4G/arcgis/rest/services/FemicideRecords_view/FeatureServer/0/query"

  headers = {
      "accept": "application/json, text/plain, */*",
      "accept-language": "en-US,en;q=0.9,tr;q=0.8",
      "origin": "https://www.arcgis.com",
      "referer": (
          "https://www.arcgis.com/apps/dashboards/b3a5601b2807414c964d4a4089c1c575"
      ),
      "user-agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
          " like Gecko) Chrome/155.0.0.0 Safari/537.36"
      ),
  }

  all_features = []
  offset = 0
  batch_size = 2000  # ArcGIS servisinin tek seferde verdiği maksimum kayıt sınırı

  print("ArcGIS servisinden tüm arşiv taranıyor...")

  while True:
    params = {
        "f": "json",  # JSON formatında veri istiyoruz
        "where": "1=1",  # Tüm kayıtları getir
        "outFields": "*",  # Tüm sütunları ve detayları al
        "returnGeometry": "true",  # Koordinatları dahil et
        "outSR": "4326",  # Doğrudan WGS84 (Lat/Lng) formatı
        "resultOffset": offset,
        "resultRecordCount": batch_size,
    }

    response = requests.get(base_url, headers=headers, params=params)

    if response.status_code != 200:
      print(
          f"Hata: Sunucu yanıt vermedi (Kod: {response.status_code})"
      )
      break

    data = response.json()
    features = data.get("features", [])

    if not features:
      break

    all_features.extend(features)
    print(f"-> {len(all_features)} kayıt çekildi...")

    if len(features) < batch_size:
      break  # Son sayfaya ulaşıldıysa döngüyü bitir
    offset += batch_size

  print(f"\nToplam {len(all_features)} ham kayıt alındı. Dönüştürülüyor...")

  dataset = []
  for index, feat in enumerate(all_features, start=1):
    attrs = feat.get("attributes", {})
    geom = feat.get("geometry", {})

    lat = geom.get("y") or geom.get("latitude")
    lng = geom.get("x") or geom.get("longitude")

    if lat is None or lng is None:
      continue

    # Eğer koordinat Mercator geldiyse düzelt
    if abs(lat) > 90 or abs(lng) > 180:
      lat, lng = web_mercator_to_lat_lng(lng, lat)

    # Tarih / Yıl tespiti
    raw_date = attrs.get("incident_date")
    year = 2026
    if raw_date:
      import datetime

      try:
        dt = datetime.datetime.fromtimestamp(raw_date / 1000.0)
        year = dt.year
      except Exception:
        pass

    # 2021-2026 aralığı filtresi
    if not (2021 <= year <= 2026):
      continue

    record = {
        "id": f"arcgis-all-{attrs.get('FID', index)}",
        "year": year,
        "month": "ArcGIS Arşivi",
        "city": attrs.get("city", "Türkiye Geneli"),
        "district": attrs.get("district", "Merkez"),
        "lat": lat,
        "lng": lng,
        "status": (
            "Şüpheli Ölüm"
            if "şüpheli"
            in str(attrs.get("death_reason", "")).lower()
            else "Cinayet"
        ),
        "motive": attrs.get("death_reason", "ArcGIS Veri Arşivi"),
        "victim": attrs.get("full_name", f"Vaka #{index}"),
        "color": "#c084fc",  # ArcGIS verileri için mor tonu
        "text": attrs.get("details", "Detay bulunmuyor."),
        "source_url": "https://www.arcgis.com/apps/dashboards/b3a5601b2807414c964d4a4089c1c575",
    }
    dataset.append(record)

  with open("femicide_arcgis.json", "w", encoding="utf-8") as f:
    json.dump(dataset, f, ensure_ascii=False, indent=4)

  print(
      f"İşlem tamam! 2021-2026 arası {len(dataset)} vaka 'femicide_arcgis.json'"
      " dosyasına kaydedildi."
  )


if __name__ == "__main__":
  fetch_all_arcgis_records()