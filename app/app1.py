from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Pomožna funkcija za povezavo z bazo
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row  # Omogoča vračanje vrstic kot slovarji
    return conn

# Inicializacija baze
def init_db():
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT
            )
        ''')
    print("Database initialized!")

@app.route('/')
def hello_world():
    return "Hello, Flask CRUD API!"

# Create - Dodaj element
@app.route('/items', methods=['POST'])
def create_item():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    with get_db_connection() as conn:
        conn.execute('INSERT INTO items (name, description) VALUES (?, ?)', (name, description))
        conn.commit()
    return jsonify({'message': 'Item created!'}), 201

# Read - Pridobi vse elemente
@app.route('/items', methods=['GET'])
def get_items():
    with get_db_connection() as conn:
        items = conn.execute('SELECT * FROM items').fetchall()
    return jsonify([dict(item) for item in items])

# Update - Posodobi element
@app.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    with get_db_connection() as conn:
        conn.execute('UPDATE items SET name = ?, description = ? WHERE id = ?', (name, description, item_id))
        conn.commit()
    return jsonify({'message': 'Item updated!'})

# Delete - Izbriši element
@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    with get_db_connection() as conn:
        conn.execute('DELETE FROM items WHERE id = ?', (item_id,))
        conn.commit()
    return jsonify({'message': 'Item deleted!'})

if __name__ == '__main__':
    init_db()  # Inicializiraj bazo ob zagonu
    app.run(debug=True)



@app.route('/ahp', methods=['GET', 'POST'])
def ahp():
    if request.method == 'POST':
        # Preberi uteži od uporabnika
        weights = {
            'revenue': float(request.form['revenue']),
            'profit': float(request.form['profit']),
            'employees': float(request.form['employees']),
            'assets': float(request.form['assets']),
        }
        
        # Pridobi podjetja (alternative) iz baze
        companies = get_all_companies()
        alternatives = [
            {
                'name': c['name'],
                'revenue': c['revenue'],
                'profit': c['profit'],
                'employees': c['employees'],
                'assets': c['assets']
            }
            for c in companies
        ]
        
        # Izračunaj AHP
        results = calculate_ahp(alternatives, weights)
        
        # Shrani rezultate v bazo
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM ahp_results')  # Počisti stare rezultate
        for result in results:
            cursor.execute('INSERT INTO ahp_results (company_name, score) VALUES (?, ?)', (result['name'], result['score']))
        conn.commit()
        conn.close()
        
        return redirect(url_for('ahp_results'))
    
    return render_template('ahp.html')

@app.route('/ahp/results')
def ahp_results():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM ahp_results ORDER BY score DESC')
    results = cursor.fetchall()
    conn.close()
    return render_template('ahp_results.html', results=results)