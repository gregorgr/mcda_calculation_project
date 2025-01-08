import sqlite3

# Povezava z bazo
def get_db_connection():
    conn = sqlite3.connect('fortune500.db')
    conn.row_factory = sqlite3.Row  # Vrne rezultate kot slovarje
    return conn

# Inicializacija tabele
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fortune500 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rank INTEGER,
            name TEXT,
            revenue REAL,
            revenue_percent_change REAL,
            profit REAL,
            profits_percent_change REAL,
            assets REAL,
            employees REAL,
            change_in_rank INTEGER,
            years_on_list INTEGER
        )
    ''')

#    cursor.execute('''   
#        ALTER TABLE results RENAME TO results_backup;
#    ''')

    cursor.execute('''   
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            method_id INTEGER,
            company_id INTEGER,
            company_name TEXT,
            score REAL
        )     
    ''')
#    cursor.execute('''   
#        INSERT INTO results (id, method_id, company_id, company_name, score)
#        SELECT id, method_id, company_id, company_name, score FROM results_backup;       
#    ''')

   # cursor.execute('''   
   #     DROP TABLE results_backup;        
   # ''')


 #   cursor.execute('''   
 #       CREATE TABLE IF NOT EXISTS results (
 #           id INTEGER PRIMARY KEY AUTOINCREMENT,
 #           method_id INTEGER,       -- Identifikator metode (1 = AHP, 2 = PROMETHEE, 3 = WSM)
 #           company_id INTEGER,      -- ID podjetja iz fortune500
 #           company_name TEXT,       -- Ime podjetja
 #       score REAL               -- Ocena podjetja
 #       )         
#    ''')
    conn.commit()
    conn.close()
#CREATE TABLE IF NOT EXISTS ahp_results (
#            id INTEGER PRIMARY KEY AUTOINCREMENT,
#                company_name TEXT,
#                score REAL
#        )

def get_results(method_id):
    """Pridobi rezultate za določeno metodo."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM results WHERE method_id = ? ORDER BY score DESC', (method_id,))
    results = cursor.fetchall()
    print("Results from DB:", results) 
    conn.close()
    return results


def get_all_companies_for_group(group):
    """Pridobi podjetja za izbrano skupino."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if group == 'A':
        query = 'SELECT * FROM fortune500 WHERE rank BETWEEN 1 AND 20 ORDER BY rank ASC'
    elif group == 'B':
        query = 'SELECT * FROM fortune500 WHERE rank BETWEEN 21 AND 40 ORDER BY rank ASC'
    elif group == 'C':
        query = 'SELECT * FROM fortune500 WHERE rank BETWEEN 41 AND 60 ORDER BY rank ASC'
    else:
        return []  # Neveljavna skupina
    
    cursor.execute(query)
    companies = cursor.fetchall()
    conn.close()
    return companies


# Pridobitev vseh podjetij
def get_all_companies(limit=None, offset=None):
    """Pridobi podjetja z omejitvijo in zamikom."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = 'SELECT * FROM fortune500 ORDER BY rank ASC'
    if limit is not None and offset is not None:
        query += f' LIMIT {limit} OFFSET {offset}'
    cursor.execute(query)
    companies = cursor.fetchall()
    conn.close()
    return companies


def insert_or_update_company(company):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Preveri, ali podjetje že obstaja
    cursor.execute('SELECT id FROM fortune500 WHERE name = ?', (company['name'],))
    existing_company = cursor.fetchone()

    if existing_company:
        # Posodobi obstoječe podjetje
        cursor.execute('''
            UPDATE fortune500
            SET 
                rank = ?,
                revenue = ?,
                revenue_percent_change = ?,
                profit = ?,
                profits_percent_change = ?,
                assets = ?,
                employees = ?,
                change_in_rank = ?,
                years_on_list = ?
            WHERE id = ?
        ''', (
            company['rank'],
            company['revenue'],
            company['revenue_percent_change'],
            company['profit'],
            company['profits_percent_change'],
            company['assets'],
            company['employees'],
            company['change_in_rank'],
            company['years_on_list'],
            existing_company['id']
        ))
    else:
        # Vstavi novo podjetje
        cursor.execute('''
            INSERT INTO fortune500 (
                rank, name, revenue, revenue_percent_change, profit, 
                profits_percent_change, assets, employees, change_in_rank, years_on_list
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            company['rank'],
            company['name'],
            company['revenue'],
            company['revenue_percent_change'],
            company['profit'],
            company['profits_percent_change'],
            company['assets'],
            company['employees'],
            company['change_in_rank'],
            company['years_on_list']
        ))
    
    conn.commit()
    conn.close()



def save_companies_to_db(companies):
    for _, company in companies.iterrows():  # iterrows iterira čez DataFrame
        insert_or_update_company(company)




def save_results(method_id, results):
    """Shrani rezultate določene metode v bazo."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Počisti obstoječe rezultate za metodo
    cursor.execute('DELETE FROM results WHERE method_id = ?', (method_id,))
    
    # Vstavi nove rezultate
    for result in results:
        cursor.execute(
            'INSERT INTO results (method_id, company_name, score) VALUES (?, ?, ?)',
            (method_id, result['name'], result['score'])
        )
    conn.commit()
    conn.close()