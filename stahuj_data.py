import requests
import sqlite3
import re

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Rozšířený dotaz pokrývající všechny možné tagy opevnění v ČR
OVERPASS_QUERY = """
[out:json][timeout:180];
area["ISO3166-1"="CZ"][admin_level=2]->.searchArea;
(
  node["historic"="bunker"](area.searchArea);
  way["historic"="bunker"](area.searchArea);
  node["building"="bunker"](area.searchArea);
  way["building"="bunker"](area.searchArea);
  node["military"="bunker"](area.searchArea);
  way["military"="bunker"](area.searchArea);
  node["bunker:type"](area.searchArea);
  way["bunker:type"](area.searchArea);
);
out center;
"""



def koriguj_typ_objektu(tags):
    name = str(tags.get('name', '')).strip()
    ref = str(tags.get('ref', '')).strip()
    bunker_type = str(tags.get('bunker:type', '')).lower()
    description = str(tags.get('description', '')).lower()

    text_to_search = f"{name} {ref} {bunker_type} {description}".lower()

    # 1. Detekce tvrzí
    if "tvrz" in text_to_search or "fort" in bunker_type:
        return "tvrz"

    # 2. Detekce těžkého opevnění (srubů)
    # Hledáme vzor kódování srubů (např. MO-S 24, N-S 82, OP-S 10, T-S 19...)
    srub_pattern = r'\b[a-z]{1,3}-s\s?\d+\b'
    
    if (re.search(srub_pattern, text_to_search) or 
        "srub" in text_to_search or 
        "těžké" in text_to_search or 
        "tezke" in text_to_search or 
        bunker_type in ["blockhouse", "pillbox_heavy"]):
        return "srub"

    # 3. Vše ostatní spadá pod lehké opevnění (řopíky)
    return "ropik"

def stahni_a_uloz_data():
    print("⏳ Odesílám rozšířený dotaz na Overpass API (může to trvat 20-40 sekund)...")
    
    headers = {
        'User-Agent': 'LovciOpevneniApp/1.0 (contact: admin@lovciopevneni.cz)',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }

    try:
        response = requests.post(OVERPASS_URL, data={'data': OVERPASS_QUERY}, headers=headers, timeout=180)
        
        if response.status_code != 200:
            print(f"❌ Chyba při stahování dat (HTTP status {response.status_code})")
            return

        data = response.json()
        elements = data.get('elements', [])
        print(f"📦 Staženo {len(elements)} objektů z OpenStreetMap. Ukládám do databáze...")

        conn = sqlite3.connect('databaze.db')
        cursor = conn.cursor()

        vlozene = 0
        for el in elements:
            osm_id = str(el.get('id'))
            tags = el.get('tags', {})
            
            lat = el.get('lat') or el.get('center', {}).get('lat')
            lon = el.get('lon') or el.get('center', {}).get('lon')

            if not lat or not lon:
                continue

            nazev = tags.get('name') or tags.get('ref') or f"Řopík / Objekt #{osm_id}"
            typ = koriguj_typ_objektu(tags)
            popis = tags.get('description', 'Československé opevnění (1935–1938)')

            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO objekty (osm_id, nazev, typ, lat, lon, popis)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (osm_id, nazev, typ, lat, lon, popis))
                if cursor.rowcount > 0:
                    vlozene += 1
            except Exception as e:
                pass

        conn.commit()
        conn.close()
        print(f"🎉 Hotovo! Nově uloženo {vlozene} objektů opevnění do databáze.")

    except Exception as e:
        print(f"❌ Neočekávaná chyba: {e}")

if __name__ == '__main__':
    stahni_a_uloz_data()