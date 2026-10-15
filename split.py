from collections import defaultdict
import json


def merge_and_update_years():
  # 1. Otomasyonla çekilen ham verileri oku
  try:
    with open("femicide_auto.json", "r", encoding="utf-8") as f:
      auto_records = json.load(f)
  except FileNotFoundError:
    print(
        "Hata: 'femicide_auto.json' bulunamadı. Önce scrape.py çalıştırılmalı."
    )
    return

  # 2. Her kaydı yıl bazında grupla
  years_data = defaultdict(list)
  for record in auto_records:
    # Konu dışı haberleri (örn. Zonguldak'taki öğretmen haberi) otomatik ele
    if "öğretmen" in record.get("text", "").lower():
      continue

    text_to_search = (
        record.get("text", "")
        + " "
        + record.get("source_url", "")
        + " "
        + str(record.get("year", ""))
    )
    found_year = 2026
    for y in [2026, 2025, 2024, 2023, 2022, 2021]:
      if str(y) in text_to_search:
        found_year = y
        break
    record["year"] = found_year
    years_data[found_year].append(record)

  # 3. Mevcut yıl dosyalarını oku, üstbilgiyi koru ve yeni kayıtları ekle
  for year, new_records in years_data.items():
    filename = f"{year}.json"
    existing_data = []

    try:
      with open(filename, "r", encoding="utf-8") as f:
        existing_data = json.load(f)
    except FileNotFoundError:
      pass

    # Eğer dosya başlığında metadata (sözlük) varsa koru
    metadata = None
    if existing_data and isinstance(existing_data[0], dict) and "id" not in existing_data[0]:
      metadata = existing_data[0]
      actual_records = existing_data[1:]
    else:
      actual_records = existing_data

    # Aynı ID'ye sahip mükerrer kayıtları önleyerek yeni kayıtları ekle
    existing_ids = {r.get("id") for r in actual_records}
    added_count = 0
    for nr in new_records:
      if nr.get("id") not in existing_ids:
        actual_records.append(nr)
        existing_ids.add(nr.get("id"))
        added_count += 1

    # Final listeyi yeniden oluştur
    final_output = [metadata] + actual_records if metadata else actual_records

    with open(filename, "w", encoding="utf-8") as f:
      json.dump(final_output, f, ensure_ascii=False, indent=4)

    print(
        f"-> {filename}: Mevcut verilere {added_count} yeni otomatik vaka"
        " eklendi (Üstbilgiler korundu)."
    )


if __name__ == "__main__":
  merge_and_update_years()