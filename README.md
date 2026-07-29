# 🛡️ Lovci Opevnění

**Lovci Opevnění** je webová komunitní a geolokační aplikace určená pro nadšence do čs. vojenské historie, urbexu a turistiky. Aplikace mapařům a lovcům umožňuje objevovat, vyhledávat, navigovat a zaznamenávat návštěvy lehkých i těžkých objektů československého opevnění z let 1935–1938 na území České republiky.

---

## 🚀 Hlavní Funkce

* **🗺️ Interaktivní mapa v taktickém vzhledu:** Vizualizace více než 7 000 objektů po celé ČR (řopíky vz. 37/36, pěchotní sruby a dělostřelecké tvrze) pomocí knihovny Leaflet.js.
* **🏷️ Inteligentní kategorizace:** Odlišení typů objektů (lehké / těžké opevnění / tvrze) podle jejich vojenského kódování a typových vlastností (např. *MO-S 24*, *N-S 82* atd.).
* **🚩 Herní systém & Hodnosti:** Registrace lovců, možnost označovat navštívené objekty, přikládat vlastní fotky a písemné poznámky z terénu. S rostoucím počtem odlovů uživatel stoupá ve vojenských hodnostech (Vojín → Kaprál → Četař → ... → Generál).
* **🏆 Komunitní žebříček:** Živý leaderboard zobrazující TOP lovce s nejvyšším počtem úspěšných odlovů.
* **🚗 Chytrá navigace:** Přímá integrace Google Maps (režim **Autem** a **Pěšky**) pro plánování tras přímo z aktuální GPS polohy uživatele až k vybranému řopíku.
* **🎯 Moje Poloha:** Geolokační tlačítko pro rychlé zaměření aktuální pozice lovce přímo na mapě v terénu.
* **🔍 Filtrování a vyhledávání:** Okamžité vyhledávání podle názvu úseku, zón nebo typu objektu s možností filtrovat pouze neodlovená místa.

---

## 🛠️ Použité Technologie

* **Backend:** Python 3, Flask framework
* **Databáze:** SQLite3
* **Frontend:** HTML5, CSS3 (Tactical Dark UI), JavaScript (ES6, Fetch API)
* **Mapové podklady & API:** Leaflet.js, CartoDB Dark Matter tiles, OpenStreetMap via Overpass API

---

## 📦 Instalace a Spuštění

### 1. Klonování repozitáře
```bash
git clone [https://github.com/TVOJE_JMENO/lovci-opevneni.git](https://github.com/TVOJE_JMENO/lovci-opevneni.git)
cd lovci-opevneni
