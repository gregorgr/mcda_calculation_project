# from flask import Flask, jsonify, render_template
from flask import Flask, g, jsonify, request, redirect, url_for, render_template
from scrape500.scrape500 import scrape_fortune500
from db.database import init_db, get_all_companies, save_companies_to_db, get_results, get_all_companies_for_group
from methods.ahp.ahp import calculate_ahp_with_method_id, calculate_ahp_advance_with_method_id
from constants import METHODS, FORTUNE_URL 



app = Flask(__name__)

# Inicializacija baze
@app.before_request
def before_request():
    # Inicializacija baze
    init_db()

    # Preberi skupino iz URL parametra, če obstaja, in preveri veljavnost
    group = request.args.get('group', 'A').upper()  # Privzeta skupina je "A"
    if group not in ['A', 'B', 'C']:
        group = 'A'  # Če skupina ni veljavna, nastavi privzeto
    g.group = group  # Nastavi skupino v globalni kontekst



# Začetna stran
@app.route('/')
def home():
    return render_template('home.html')

#@app.route('/init-db')
#def init_database():
#    init_db()
#    return jsonify({'message': 'Database initialized!'})


@app.route('/companies')
def companies_table():
    # companies = scrape_fortune500(FORTUNE_URL)  # Pridobi podatke
    companies = get_all_companies()
    # companies_list = companies.to_dict(orient='records')  # Pretvori v seznam slovarjev
    print("Rendering template: companies/index.html")  # Debug
    return render_template('companies/index.html', companies=companies)



@app.route('/scrape-and-save')
def scrape_and_save():
    companies = scrape_fortune500(FORTUNE_URL)  # Pridobi najnovejše podatke
    save_companies_to_db(companies)  # Posodobi bazo
    # return jsonify({'message': 'Data scraped and saved successfully!'})
    return render_template('scrape.html')


# API endpoints
# Endpoint za scraping Fortune 500
@app.route('/api/scrape-fortune-500')
def scrape_fortune_500_route():
    companies = scrape_fortune500(FORTUNE_URL)
    return companies.to_json(orient='records'), 200, {'Content-Type': 'application/json'}



@app.route('/select-companies', methods=['GET', 'POST'])
def select_companies():
    print("Helo world")
    if request.method == 'POST':
        group = request.form['group'].upper()

        if group not in ['A', 'B', 'C']:
            group = 'A'  # Privzeta skupina

        if group == 'A':
            companies = get_all_companies(limit=20, offset=0)
        elif group == 'B':
            companies = get_all_companies(limit=20, offset=20)
        elif group == 'C':
            companies = get_all_companies(limit=20, offset=40)
        else:
            companies = []
        # return redirect(url_for('select_companies', group=group))
        return render_template('select_companies.html', companies=companies, group=group)
    
    return render_template('select_companies.html')



@app.route('/ahp', methods=['GET', 'POST'])
def ahp():
    if request.method == 'POST':

        # Preberi skupino iz URL parametra (GET)
        group = request.args.get('group', 'A')  # Privzeto "A", če ni definirano
        # Preberi skupino iz obrazca
        # group = request.form.get('group', 'A')  # Privzeto skupina A, če ni definirana
        
        # Preberi uteži in alternative
        weights = {
            'revenue': float(request.form['revenue']),
            'profit': float(request.form['profit']),
            'employees': float(request.form['employees']),
            'assets': float(request.form['assets']),
        }

        # Preveri, ali so vse uteži pozitivne
        if any(w <= 0 for w in weights.values()):
            return "Weights must be positive numbers.", 400
        
        # normalisation if weights
        total_weight = sum(weights.values())
        if total_weight == 0:
            return "Total weight must be greater than 0.", 400
        weights = {k: v / total_weight for k, v in weights.items()}  # normalisation

        # Preveri normalizirane uteži
        print("Normalized weights:", weights)
        # Pridobi podjetja za izbrano skupino
        companies = get_all_companies_for_group(group)
        print("Selected companies:", companies)  # Izpis podjetij
        alternatives = [
            {
                'id': c['id'],
                'name': c['name'],
                'revenue': c['revenue'],
                'profit': c['profit'],
                'employees': c['employees'],
                'assets': c['assets']
            }
            for c in companies
        ]

        # Če ni podjetij, vrni sporočilo
        if not alternatives:
            return "No companies found for the selected group.", 400


        # Izračunaj AHP in shrani rezultate
        # calculate_ahp_with_method_id(alternatives, weights)
        # calculate_ahp_with_method_id(companies, weights)
        calculate_ahp_advance_with_method_id(companies, weights)

        return redirect(url_for('results', method_id=1)) # method_id='AHP'))
    
    # Če je GET zahteva, pokaži obrazec
    group = request.args.get('group', 'A')  # Privzeto skupina A
    return render_template('methods/ahp.html', group=group)


#@app.route('/ahp/results')
#def ahp_results():
#   return render_template('methods/ahp_results.html', results=get_ahp_results())
#

@app.route('/results/<int:method_id>')
def results(method_id):

    results = get_results(method_id)
    # method_name = "AHP" if method_id == 1 else "PROMETHEE" if method_id == 2 else "WSM"
    method_name = METHODS.get(method_id, "Unknown Method")  # Dobimo ime metode
    return render_template('results.html', method_name=method_name, results=results)



@app.route('/compare')
def compare():
    ahp_results = get_results(1)
    promethee_results = get_results(2)
    wsm_results = get_results(3)
    return render_template('compare.html', ahp=ahp_results, promethee=promethee_results, wsm=wsm_results)





if __name__ == '__main__':
    app.run(debug=True)
