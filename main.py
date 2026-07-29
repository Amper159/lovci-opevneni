import os
import sqlite3
from flask import Flask, render_template, jsonify, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'tajny_klic_lovci_opevneni_1938'

UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_db():
    conn = sqlite3.connect('databaze.db')
    conn.row_factory = sqlite3.Row
    return conn

def vypocitej_hodnost(pocet):
    if pocet >= 100: return "Generál"
    elif pocet >= 50: return "Plukovník"
    elif pocet >= 25: return "Kapitán"
    elif pocet >= 10: return "Rotmistr"
    elif pocet >= 5: return "Četař"
    elif pocet >= 1: return "Kaprál"
    return "Vojín"

@app.route('/')
def index():
    user = session.get('user')
    return render_template('index.html', user=user)

# --- AUTH ---
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    jmeno = data.get('jmeno', '').strip()
    heslo = data.get('heslo', '')

    if not jmeno or not heslo:
        return jsonify({'error': 'Vyplň jméno i heslo.'}), 400

    hashed_password = generate_password_hash(heslo)
    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO uzivatele (jmeno, heslo) VALUES (?, ?)", (jmeno, hashed_password))
        conn.commit()
        user_id = cursor.lastrowid
        session['user'] = {'id': user_id, 'jmeno': jmeno}
        conn.close()
        return jsonify({'success': True, 'jmeno': jmeno})
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Jméno je již zabrané.'}), 400

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    jmeno = data.get('jmeno', '').strip()
    heslo = data.get('heslo', '')

    conn = get_db()
    cursor = conn.cursor()
    user = cursor.execute("SELECT * FROM uzivatele WHERE jmeno = ?", (jmeno,)).fetchone()
    conn.close()

    if user and check_password_hash(user['heslo'], heslo):
        session['user'] = {'id': user['id'], 'jmeno': user['jmeno']}
        return jsonify({'success': True, 'jmeno': user['jmeno']})
    
    return jsonify({'error': 'Nesprávné jméno nebo heslo.'}), 400

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({'success': True})

# --- DATA ---
@app.route('/api/objekty')
def get_objekty():
    conn = get_db()
    cursor = conn.cursor()
    user_id = session.get('user', {}).get('id')
    
    if user_id:
        query = '''
            SELECT o.id, o.osm_id, o.nazev, o.typ, o.lat, o.lon, o.popis,
                   CASE WHEN n.id IS NOT NULL THEN 1 ELSE 0 END as navstiveno,
                   n.datum_navstevy, n.poznamka, n.foto_path
            FROM objekty o
            LEFT JOIN navstevy n ON o.id = n.objekt_id AND n.user_id = ?
        '''
        objekty = cursor.execute(query, (user_id,)).fetchall()
    else:
        query = "SELECT id, osm_id, nazev, typ, lat, lon, popis, 0 as navstiveno FROM objekty"
        objekty = cursor.execute(query).fetchall()

    conn.close()
    return jsonify([dict(row) for row in objekty])

@app.route('/api/odlov', methods=['POST'])
def odlov_objekt():
    user = session.get('user')
    if not user:
        return jsonify({'error': 'Pro odlovení se musíš přihlásit.'}), 401

    objekt_id = request.form.get('objekt_id')
    poznamka = request.form.get('poznamka', '')
    foto = request.files.get('foto')

    foto_path = None
    if foto and foto.filename != '':
        filename = secure_filename(f"user_{user['id']}_obj_{objekt_id}_{foto.filename}")
        foto_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        foto.save(foto_path)
        foto_path = f"/static/uploads/{filename}"

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT OR REPLACE INTO navstevy (user_id, objekt_id, poznamka, foto_path)
        VALUES (?, ?, ?, ?)
    ''', (user['id'], objekt_id, poznamka, foto_path))

    conn.commit()

    pocet_odlovu = cursor.execute('SELECT COUNT(*) FROM navstevy WHERE user_id = ?', (user['id'],)).fetchone()[0]
    conn.close()

    return jsonify({
        'success': True,
        'pocet_odlovu': pocet_odlovu,
        'hodnost': vypocitej_hodnost(pocet_odlovu)
    })

@app.route('/api/stats')
def get_stats():
    user = session.get('user')
    if not user:
        return jsonify({'logged_in': False, 'odloveno': 0, 'hodnost': 'Vojín'})

    conn = get_db()
    cursor = conn.cursor()
    pocet = cursor.execute('SELECT COUNT(*) FROM navstevy WHERE user_id = ?', (user['id'],)).fetchone()[0]
    conn.close()

    return jsonify({
        'logged_in': True,
        'jmeno': user['jmeno'],
        'odloveno': pocet,
        'hodnost': vypocitej_hodnost(pocet)
    })

# --- NOVÉ: ŽEBŘÍČEK LEADERBOARD ---
@app.route('/api/leaderboard')
def leaderboard():
    conn = get_db()
    cursor = conn.cursor()
    query = '''
        SELECT u.jmeno, COUNT(n.id) as pocet
        FROM uzivatele u
        LEFT JOIN navstevy n ON u.id = n.user_id
        GROUP BY u.id
        ORDER BY pocet DESC
        LIMIT 10
    '''
    rows = cursor.execute(query).fetchall()
    conn.close()

    result = []
    for r in rows:
        result.append({
            'jmeno': r['jmeno'],
            'pocet': r['pocet'],
            'hodnost': vypocitej_hodnost(r['pocet'])
        })

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5001)