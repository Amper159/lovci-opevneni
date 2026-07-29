import sqlite3

def init_db():
    conn = sqlite3.connect('databaze.db')
    cursor = conn.cursor()

    # Tabulka pro pevnostní objekty
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS objekty (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            osm_id TEXT UNIQUE,
            nazev TEXT NOT NULL,
            typ TEXT NOT NULL,          -- ropik / srub / tvrz / jine
            kraj TEXT,
            lat REAL NOT NULL,
            lon REAL NOT NULL,
            popis TEXT,
            stav TEXT                   -- zachovaly / zniceny / muzeum
        )
    ''')

    # Tabulka pro uživatele (stejná logika jako u hradů)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS uzivatele (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            jmeno TEXT UNIQUE NOT NULL,
            heslo TEXT NOT NULL
        )
    ''')

    # Tabulka pro odlovená místa
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS navstevy (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            objekt_id INTEGER,
            datum_navstevy DATETIME DEFAULT CURRENT_TIMESTAMP,
            poznamka TEXT,
            foto_path TEXT,
            FOREIGN KEY (user_id) REFERENCES uzivatele (id),
            FOREIGN KEY (objekt_id) REFERENCES objekty (id)
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ Databáze byla úspěšně vytvořena!")

if __name__ == '__main__':
    init_db()