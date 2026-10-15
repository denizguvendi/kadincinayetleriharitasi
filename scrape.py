import json
import re
from bs4 import BeautifulSoup, Tag
import requests

# 1. Türkiye'nin 81 İl ve Merkez Koordinat Sözlüğü
TURKEY_CITIES = {
    "Adana": {"lat": 37.0000, "lng": 35.3213},
    "Adıyaman": {"lat": 37.7648, "lng": 38.2786},
    "Afyonkarahisar": {"lat": 38.7507, "lng": 30.5567},
    "Ağrı": {"lat": 39.7191, "lng": 43.0503},
    "Amasya": {"lat": 40.6547, "lng": 35.8356},
    "Ankara": {"lat": 39.9208, "lng": 32.8541},
    "Antalya": {"lat": 36.8841, "lng": 30.7056},
    "Artvin": {"lat": 41.1828, "lng": 41.8183},
    "Aydın": {"lat": 37.8444, "lng": 27.8458},
    "Balıkesir": {"lat": 39.6484, "lng": 27.8826},
    "Bilecik": {"lat": 40.1451, "lng": 29.9796},
    "Bingöl": {"lat": 38.8854, "lng": 40.4980},
    "Bitlis": {"lat": 38.4006, "lng": 42.1095},
    "Bolu": {"lat": 40.7350, "lng": 31.6061},
    "Burdur": {"lat": 37.7262, "lng": 30.2910},
    "Bursa": {"lat": 40.1885, "lng": 29.0610},
    "Çanakkale": {"lat": 40.1553, "lng": 26.4142},
    "Çankırı": {"lat": 40.6013, "lng": 33.6134},
    "Çorum": {"lat": 40.5506, "lng": 34.9556},
    "Denizli": {"lat": 37.7765, "lng": 29.0864},
    "Diyarbakır": {"lat": 37.9158, "lng": 40.2189},
    "Edirne": {"lat": 41.6771, "lng": 26.5557},
    "Elazığ": {"lat": 38.6810, "lng": 39.2264},
    "Erzincan": {"lat": 39.7500, "lng": 39.5000},
    "Erzurum": {"lat": 39.9000, "lng": 41.2700},
    "Eskişehir": {"lat": 39.7767, "lng": 30.5206},
    "Gaziantep": {"lat": 37.0594, "lng": 37.3825},
    "Giresun": {"lat": 40.9128, "lng": 38.3895},
    "Gümüşhane": {"lat": 40.4600, "lng": 39.4797},
    "Hakkari": {"lat": 37.5833, "lng": 43.7333},
    "Hatay": {"lat": 36.2021, "lng": 36.1607},
    "Isparta": {"lat": 37.7648, "lng": 30.5566},
    "Mersin": {"lat": 36.8121, "lng": 34.6415},
    "İstanbul": {"lat": 41.0082, "lng": 28.9784},
    "İzmir": {"lat": 38.4192, "lng": 27.1287},
    "Kars": {"lat": 40.6013, "lng": 43.0975},
    "Kastamonu": {"lat": 41.3887, "lng": 33.7827},
    "Kayseri": {"lat": 38.7225, "lng": 35.4875},
    "Kırklareli": {"lat": 41.7333, "lng": 27.2167},
    "Kırşehir": {"lat": 39.1458, "lng": 34.1612},
    "Kocaeli": {"lat": 40.7656, "lng": 29.9408},
    "Konya": {"lat": 37.8744, "lng": 32.4931},
    "Kütahya": {"lat": 39.4238, "lng": 29.9833},
    "Malatya": {"lat": 38.3552, "lng": 38.3095},
    "Manisa": {"lat": 38.6191, "lng": 27.4289},
    "Kahramanmaraş": {"lat": 37.5858, "lng": 36.9371},
    "Mardin": {"lat": 37.3212, "lng": 40.7245},
    "Muğla": {"lat": 37.2153, "lng": 28.3636},
    "Muş": {"lat": 38.7437, "lng": 41.4906},
    "Nevşehir": {"lat": 38.6244, "lng": 34.7231},
    "Niğde": {"lat": 37.9667, "lng": 34.6833},
    "Ordu": {"lat": 40.9839, "lng": 37.8764},
    "Rize": {"lat": 41.0201, "lng": 40.5234},
    "Sakarya": {"lat": 40.7569, "lng": 30.3783},
    "Samsun": {"lat": 41.2800, "lng": 36.3300},
    "Siirt": {"lat": 37.9333, "lng": 41.9500},
    "Sinop": {"lat": 42.0231, "lng": 35.1531},
    "Sivas": {"lat": 39.7477, "lng": 37.0179},
    "Tekirdağ": {"lat": 40.9833, "lng": 27.5167},
    "Tokat": {"lat": 40.3167, "lng": 36.5500},
    "Trabzon": {"lat": 41.0027, "lng": 39.7167},
    "Tunceli": {"lat": 39.1079, "lng": 39.5401},
    "Şanlıurfa": {"lat": 37.1674, "lng": 38.7934},
    "Uşak": {"lat": 38.6823, "lng": 29.4082},
    "Van": {"lat": 38.4891, "lng": 43.4089},
    "Yozgat": {"lat": 39.8181, "lng": 34.8147},
    "Zonguldak": {"lat": 41.4564, "lng": 31.7987},
    "Aksaray": {"lat": 38.3687, "lng": 34.0370},
    "Bayburt": {"lat": 40.2552, "lng": 40.2249},
    "Karaman": {"lat": 37.1759, "lng": 33.2287},
    "Kırıkkale": {"lat": 39.8468, "lng": 33.5153},
    "Batman": {"lat": 37.8812, "lng": 41.1351},
    "Şırnak": {"lat": 37.5193, "lng": 42.4589},
    "Bartın": {"lat": 41.6344, "lng": 32.3375},
    "Ardahan": {"lat": 41.1105, "lng": 42.7022},
    "Iğdır": {"lat": 39.9167, "lng": 44.0333},
    "Yalova": {"lat": 40.6500, "lng": 29.9000},
    "Karabük": {"lat": 41.2061, "lng": 32.6204},
    "Kilis": {"lat": 36.7184, "lng": 37.1212},
    "Osmaniye": {"lat": 37.0742, "lng": 36.2472},
    "Düzce": {"lat": 40.8438, "lng": 31.1565},
}


def detect_city(text):
  for city, coord in TURKEY_CITIES.items():
    if city.lower() in text.lower():
      return city, coord
  return "Türkiye Geneli", {"lat": 39.0, "lng": 35.0}


def extract_clean_motive(full_content, status):
  """Haber metninden ve durumdan anlamsal bahane/gerekçe çıkaran akıllı fonksiyon"""
  txt = full_content.lower()
  if "boşan" in txt or "ayrıl" in txt or "birlikte yaşamak istem" in txt:
    return "Boşanmak / Ayrılmak İsteme"
  if "kıskanç" in txt or "ilişki" in txt or "gönül ilişkisi" in txt:
    return "Kıskançlık / İlişki Tartışması"
  if "para" in txt or "mal paylaşım" in txt or "ekonomik" in txt:
    return "Ekonomik / Mal Paylaşımı"
  if "tartışma" in txt or "kavga" in txt:
    return "Tartışma / Gerekçesiz"
  if "şüpheli" in txt or status == "Şüpheli Ölüm":
    return "Şüpheli Ölüm / Aydınlatılmayı Bekleyen"
  return "Belirtilmemiş / Diğer"


def scrape_tag_page():
  tag_url = "https://www.hurriyet.com.tr/haberleri/kadin-cinayeti"
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
          " like Gecko) Chrome/120.0.0.0 Safari/537.36"
      )
  }

  print(f"Bağlanılıyor: {tag_url}")
  response = requests.get(tag_url, headers=headers)
  if response.status_code != 200:
    print(f"Hata: Sayfaya erişilemedi (Kod: {response.status_code})")
    return

  soup = BeautifulSoup(response.text, "html.parser")
  article_links = set()

  for a in soup.find_all("a"):
    if isinstance(a, Tag):
      href = a.get("href")
      if href and isinstance(href, str):
        if "/gundem/" in href or "/haber/" in href:
          full_url = (
              href
              if href.startswith("http")
              else "https://www.hurriyet.com.tr" + href
          )
          article_links.add(full_url)

  print(f"Bulunan toplam haber bağlantısı: {len(article_links)}")
  dataset = []

  for index, link in enumerate(list(article_links)[:25], start=1):
    try:
      res = requests.get(link, headers=headers, timeout=8)
      if res.status_code != 200:
        continue

      news_soup = BeautifulSoup(res.text, "html.parser")
      title_tag = news_soup.find("h1")
      title = title_tag.get_text(strip=True) if title_tag else "Haber Başlığı"

      p_tags = news_soup.find_all("p")
      body_text = " ".join([p.get_text(strip=True) for p in p_tags[:4]])

      full_content = title + " " + body_text
      city, coords = detect_city(full_content)

      jitter_lat = coords["lat"] + ((index % 5) * 0.015)
      jitter_lng = coords["lng"] + ((index % 5) * 0.015)

      status = (
          "Şüpheli Ölüm" if "şüpheli" in full_content.lower() else "Cinayet"
      )
      motive = extract_clean_motive(full_content, status)

      record = {
          "id": f"hurriyet-auto-{index}",
          "year": 2026,
          "month": "Güncel",
          "city": city,
          "district": "Merkez",
          "lat": jitter_lat,
          "lng": jitter_lng,
          "status": status,
          "motive": motive,
          "victim": f"Haber Kaydı #{index}",
          "color": (
              "#c084fc"
              if status == "Şüpheli Ölüm"
              else "#fb7185"
          ),
          "text": f"{title} — {body_text[:180]}...",
          "source_url": link,
      }
      dataset.append(record)
      print(f"[{index}] İşlendi ({city}) [{motive}]: {title[:40]}...")
    except Exception as e:
      print(f"Haber okunurken hata ({link}): {e}")

  with open("femicide_auto.json", "w", encoding="utf-8") as f:
    json.dump(dataset, f, ensure_ascii=False, indent=4)

  print(
      f"\nBaşarılı! {len(dataset)} vaka taranarak 'femicide_auto.json'"
      " dosyasına kaydedildi."
  )


if __name__ == "__main__":
  scrape_tag_page()