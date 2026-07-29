import sqlite3
import re

def koriguj_typ(nazev, popis):
    text = f"{nazev} {popis}".lower()

    if "tvrz" in text:
        return "tvrz"

    # Regex pro sruby (MO-S 24, N-S 82, OP-S 10, atd.)
    srub_pattern = r'\b[a-z]{1,4}-s\s?\d+\b'
    
    if re.search(srub_pattern, text) or "srub" in text or "těžké" in text or "tezke" in text:
        return "srub"

    return "ropik"

def oprav_databazi():
    conn = sqlite3.connect('databaze.db')
    cursor = conn.cursor()

    cursor.execute("SELECT id, nazev, popis, typ FROM objekty")
    objekty = cursor.fetchall()

    opraveno_srubu = 0
    opraveno_tvrzi = 0

    for obj_id, nazev, popis, stary_typ in objekty:
        novy_typ = koriguj_typ(nazev or '', popis or '')
        
        if novy_typ != stary_typ:
            cursor.execute("UPDATE objekty SET typ = ? WHERE id = ?", (novy_typ, obj_id))
            if novy_typ == 'srub':
                opraveno_srubu += 1
            elif novy_typ == 'tvrz':
                opraveno_tvrzi += 1

    conn.commit()
    conn.close()

    print(f"🎉 Hotovo! Přeřazeno {opraveno_srubu} objektů na sruby a {opraveno_tvrzi} na tvrze.")

if __name__ == '__main__':
    oprav_databazi()