# from flask import Flask, jsonify, render_template
from flask import Flask, g, jsonify, request, redirect, url_for, render_template, session
from scrape500.scrape500 import scrape_fortune500
from db.database import init_db, get_all_companies, save_companies_to_db, get_results, get_all_companies_for_group
import numpy as np
from constants import METHODS, FORTUNE_URL, SECRET_KEY
from methods.ahp.ahp import  calculate_ahp_advance_with_method_id
from methods.promethee.promethee import classify_and_normalize, calculate_difference_matrix




app = Flask(__name__)
app.secret_key = 'SECRET_KEY'

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


# Route for PROMETHEE method
# step 1
@app.route('/promethee', methods=['GET', 'POST'])
def promethee():

    group = request.args.get('group', 'A')  # Default group "A" if not provided
    #Render the main page for the PROMETHEE method.
    classification_attributes = {
        'revenue': 'beneficial',
        'revenue_percent_change': 'beneficial',
        'profit': 'beneficial',
        'profits_percent_change': 'beneficial',
        'employees': 'beneficial',
        'assets': 'beneficial',
        'change_in_rank': 'non-beneficial'
    }

    classification_attributes = session.get('classification_attributes', classification_attributes)
    #print("Difference Matrix:\n", difference_matrix)
    if request.method == 'POST':
        # Save classification to database or memory
        for attribute in classification_attributes.keys():
            classification_attributes[attribute] = request.form.get(attribute, classification_attributes[attribute])

        # Store attributes in session
        session['classification_attributes'] = classification_attributes

        # Redirect to parameter settings
        return redirect('/promethee/parameters?group=' + group)

    return render_template('methods/promethee-classify.html', attributes=classification_attributes, group=group)



# Route for PROMETHEE method
# step 2
@app.route('/promethee/parameters', methods=['GET', 'POST'])
def promethee_parameters():
    group = request.args.get('group', 'A')  # Default group "A"

    # Default parameter settings
    parameter_attributes = {
        'revenue': {'weight': 0.2, 'preference': 'linear'},
        'revenue_percent_change': {'weight': 0.2, 'preference': 'linear'},
        'profit': {'weight': 0.2, 'preference': 'linear'},
        'profits_percent_change': {'weight': 0.1, 'preference': 'linear'},
        'employees': {'weight': 0.1, 'preference': 'linear'},
        'assets': {'weight': 0.1, 'preference': 'linear'},
        'change_in_rank': {'weight': 0.1, 'preference': 'threshold'}
    }

    parameter_attributes = session.get('parameter_attributes', parameter_attributes)

    if request.method == 'POST':
        # Update parameter settings based on user input
        for attr in parameter_attributes.keys():
            parameter_attributes[attr]['weight'] = float(request.form.get(f'{attr}_weight', parameter_attributes[attr]['weight']))
            parameter_attributes[attr]['preference'] = request.form.get(f'{attr}_preference', parameter_attributes[attr]['preference'])
        
        session['parameter_attributes'] = parameter_attributes
        # Save parameter settings to database or memory
        print("Updated parameters:", parameter_attributes)

        # Redirect to processing step (e.g., normalization)
        return redirect('/promethee/normalize?group=' + group)

    return render_template('methods/promethee-parameters.html', attributes=parameter_attributes, group=group)


@app.route('/promethee/decision-matrix', methods=['GET', 'POST'])
def promethee_decision_matrix():
    if request.method == 'POST':
        # Retrieve decision matrix from user input
        num_alternatives = int(request.form.get('num_alternatives', 3))
        attributes = ['revenue', 'profit', 'employees', 'assets']  # Example attributes
        decision_matrix = []

        for i in range(1, num_alternatives + 1):
            row = []
            for attribute in attributes:
                value = float(request.form.get(f'alt_{i}_{attribute}', 0))
                row.append(value)
            decision_matrix.append(row)

        # Save decision matrix in session or database
        session['decision_matrix'] = decision_matrix
        return redirect('/promethee/normalize')

    # Render form to input decision matrix
    return render_template('methods/promethee-decision-matrix.html', num_alternatives=3, attributes=['revenue', 'profit', 'employees', 'assets'])


@app.route('/promethee/normalize', methods=['GET'])
def promethee_normalize():
    group = request.args.get('group', 'A')

 

    # Attribute classification (replace with database or user input)
    #classification_attributes = {
    #    'revenue': 'beneficial',
    #    'revenue_percent_change': 'beneficial',
    #    'profit': 'beneficial',
    #    'profits_percent_change': 'beneficial',
    #    'employees': 'beneficial',
    #    'assets': 'beneficial',
    #    'change_in_rank':
    #    'non-beneficial'
    #}
    
    # Retrieve classification attributes from session
    classification_attributes = session.get('classification_attributes', {})
    if not classification_attributes:
        error_text  = "Classification attributes not found. Please complete the previous step."
        return render_template('error.html', error_text=error_text)
    
    # Example decision matrix
    decision_matrix = np.array([
        [500, 5, 50, 3, 1000, 2000, -2],
        [700, 6, 80, 4.5, 1500, 3000, 1],
        [600, 4, 60, 2, 1200, 2500, 0]
    ])

      

    # print("promethee_normalize:decision Matrix:", decision_matrix)
    # Normalize decision matrix
    normalized_matrix = classify_and_normalize(decision_matrix, classification_attributes)
        # Store in session
    session['classification_attributes'] = classification_attributes
    session['normalized_matrix'] = normalized_matrix.tolist()
    
    print("promethee_normalize: Normalized Matrix:", normalized_matrix)

    # Save normalized matrix (e.g., in memory or database)
    return redirect('/promethee/differences?group=' + group)


@app.route('/promethee/differences', methods=['GET'])
def promethee_differences():
    group = request.args.get('group', 'A')

    # Example normalized matrix (replace with saved data)
    normalized_matrix = np.array([
        [0.0, 0.5, 0.0, 0.5, 0.0, 0.0, 1.0],
        [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0],
        [0.5, 0.0, 0.5, 0.0, 0.5, 0.5, 0.5]
    ])

        # Retrieve from session
    normalized_matrix = np.array(session.get('normalized_matrix', []))
    attributes = session.get('attributes', {})
    if normalized_matrix.size == 0:
        return "Normalized matrix not found. Please complete the previous step."

    # Calculate difference matrix
    difference_matrix = calculate_difference_matrix(normalized_matrix)
    print("Difference Matrix:", difference_matrix)

    # Save difference matrix (e.g., in memory or database)
    return "Difference matrix calculated. Proceed to preference functions."


# Route for PROMETHEE method
# step 3
@app.route('/promethee/classify', methods=['POST'])
def classify_attributes():

    group = request.form.get('group')  # Retrieve the group

    # Example decision matrix
    decision_matrix = np.array([
        [500, 5, 50, 3, 1000, 2000, -2],
        [700, 6, 80, 4.5, 1500, 3000, 1],
        [600, 4, 60, 2, 1200, 2500, 0]
    ])

    attributes = {
        'revenue': request.form.get('revenue'),
        'revenue_percent_change': request.form.get('revenue_percent_change'),
        'profit': request.form.get('profit'),
        'profits_percent_change': request.form.get('profits_percent_change'),
        'employees': request.form.get('employees'),
        'assets': request.form.get('assets'),
        'change_in_rank': request.form.get('change_in_rank')
    }
    # Save or use attributes for normalization
    #return redirect('/promethee')
        # Log the updated classifications (can be replaced with saving to a database or file)
    print(f"Group: {group}, Attributes: {attributes}")

        # Normalize decision matrix
    normalized_matrix = classify_and_normalize(decision_matrix, attributes)
    print("Normalized Matrix:\n", normalized_matrix)
    # Calculate difference matrix
    difference_matrix = calculate_difference_matrix(normalized_matrix)
    print("Difference Matrix:\n", difference_matrix)
    #return render_template('methods/promethee-main.html')
    # Redirect to the next step in PROMETHEE
    # return redirect('/promethee/next')
    return redirect('/promethee')  # Replace '/promethee/next' with the next step



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
        print("Selected group:", group)  # Izpis podjetij
        # Preberi uteži in alternative
        weights = {
            'revenue': float(request.form['revenue']),
            'revenue_percent_change': float(request.form.get('revenue_percent_change', 0.0)),
            'profit': float(request.form['profit']),
            'profits_percent_change': float(request.form.get('profits_percent_change', 0.0)),
            'employees': float(request.form['employees']),
            'assets': float(request.form['assets']),
            'change_in_rank': float(request.form.get('change_in_rank', 0.0)),
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
              
        # Če ni podjetij, vrni sporočilo
        if not companies:
            error_text  = "No companies found for the selected group."
            return render_template('error.html', error_text=error_text)
        
        # print("Selected companies:", companies)  # Izpis podjetij
        alternatives = [
            {
                'id': c['id'],
                'name': c['name'],
                'revenue': c['revenue'],
                'profit': c['profit'],
                'employees': c['employees'],
                'assets': c['assets'],
                'revenue_percent_change': c['revenue_percent_change'],
                'profits_percent_change': c['profits_percent_change'],
                'change_in_rank': c['change_in_rank'],
            }
            for c in companies
        ]

        
        # Če ni podjetij, vrni sporočilo
        if not alternatives:
            error_text  = "No companies found for the selected group."
            return render_template('error.html', error_text=error_text)
            # return "No companies found for the selected group.", 400
            


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
