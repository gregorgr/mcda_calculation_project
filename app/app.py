# from flask import Flask, jsonify, render_template
from flask import Flask, g, jsonify, request, redirect, url_for, render_template, session
from scrape500.scrape500 import scrape_fortune500
from db.database import init_db, save_results, get_all_companies, get_all_results_with_methods, save_companies_to_db, get_results, get_all_companies_for_group
import numpy as np
from constants import METHODS, FORTUNE_URL, SECRET_KEY
from methods.ahp.ahp import  calculate_ahp_advance_with_method_id
from methods.promethee.promethee import classify_and_normalize, calculate_difference_matrix
import locale

locale.setlocale(locale.LC_ALL, 'sl_SI.UTF-8')

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



@app.route('/topsis', methods=['GET'])
def topsis_main():
    return render_template('methods/topsis.html')



@app.route('/wsm1', methods=['GET', 'POST'])
def wsm_main1():

    # prednstavljene vrednosti za polnjenje 

    if request.method == 'POST':
        group = request.args.get('group', 'A')  # Default group "A" if not provided

        # če je kalkulacija mogoča, potem vstavi izračune tukaj

        # sicer preusmeri na naslednjo formo
        return redirect('/wsm/calculate?group=' + group)



    return render_template('methods/wsm-input.html')


@app.route('/wsm', methods=['GET', 'POST'])
def wsm_main():
    group = request.args.get('group', 'A') 
    # Retrieve companies for the selected group
    companies = get_all_companies_for_group(group)
    # prednstavljene vrednosti za polnjenje 
    criterias = ['revenue', 
                'revenue_percent_change', 
                'profit', 
                'profits_percent_change', 
                'employees', 
                'assets',
                'change_in_rank'] 
    criteria_display = {
                "revenue": "Revenue",
                "revenue_percent_change": "Revenue Percent Change",
                "profit": "Profit",
                "profits_percent_change": "Profits Percent Change",
                "employees": "Employees",
                "assets": "Assets",
                "change_in_rank": "Change in Rank"
                }
     # Example attributes
    #print("WSM Debug: companies:")
    ##for row in companies:
    #    print(dict(row))  # Pretvori SQLite Row v navaden slovar


    if request.method == 'POST':
        # Pridobivanje podatkov iz obrazca
        try:
            num_criteria = int(request.form.get('num_criteria'))
            weights = list(map(float, request.form.getlist('weights')))
            criteria_values = [
                list(map(float, request.form.getlist(f'criteria_{i}')))
                for i in range(len(companies))
            ]

            # Preverjanje, če so pravilne uteži
            if sum(weights) != 1.0:
                raise ValueError("Uteži morajo biti normalizirane in njihova vsota mora biti 1.")

            scores = []
            for company in companies:
                # WSM score is the weighted sum of the criteria
                score = sum(company[criterion] * weight for criterion, weight in zip(criterias, weights))
                scores.append(score)

            # Prepare results in the correct format
            results = [{'company_id': company['id'], 'name': company['name'], 'score': scores[i]} for i, company in enumerate(companies)] 

            #from pprint import pprint
            #print("WSM Debug: results:")
            #pprint(results)
            #print("\nWSM Debug: results:")
            #for row in results:
            #    print(row)  # Pretvori SQLite Row v navaden slovar
            #    print(dict(row))  # Pretvori SQLite Row v navaden slovar
            # Shranjevanje rezultatov
            save_results(4, results)  # method_id = 4 za WSM

            # return render_template('methods/wsm-results.html', results=results, group=group)
            return redirect(url_for('results', method_id=4, group=group))

        except ValueError as e:
            return render_template('methods/wsm-input.html', group=group, companies=companies, error=str(e))


    # koda za GET metodo
    return render_template('methods/wsm-input.html', group=group, criteria_display=criteria_display)



@app.route('/wsm/calculate', methods=['GET', 'POST'])
def wsm_calculate():
    group = request.args.get('group', 'A')  # Default group "A" if not provided
    # prednstavljene vrednosti za polnjenje 
    
    result=[]

    # implementacija

    # Save results to database
    save_results(3, results)  # Save results with method_id = 3

    return redirect(url_for('results', method_id=3, group=group))







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

    # Retrieve companies for the selected group
    companies = get_all_companies_for_group(group)
    

    #print("PROMETHEE Debug: companies:")
    #for row in companies:
    #    print(dict(row))  # Pretvori SQLite Row v navaden slovar

    # Save results to database
    # save_results(3, results)  # Save results with method_id = 3
    company_names = [company['name'] for company in companies]
    session['promethee_company_names'] = company_names  # Store company names in session


    classification_attributes = {
        'revenue': 'beneficial',
        'revenue_percent_change': 'beneficial',
        'profit': 'beneficial',
        'profits_percent_change': 'beneficial',
        'employees': 'beneficial',
        'assets': 'beneficial',
        'change_in_rank': 'non-beneficial'
    }

    classification_attributes = session.get('promethee_classification_attributes', classification_attributes)
    #print("Difference Matrix:\n", difference_matrix)
    if request.method == 'POST':
        # Save classification to database or memory
        for attribute in classification_attributes.keys():
            classification_attributes[attribute] = request.form.get(attribute, classification_attributes[attribute])

        # Store attributes in session
        session['group'] = group
        session['promethee_classification_attributes'] = classification_attributes

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

    parameter_attributes = session.get('promethee_parameter_attributes', parameter_attributes)

    if request.method == 'POST':
        # Update parameter settings based on user input
        for attr in parameter_attributes.keys():
            parameter_attributes[attr]['weight'] = float(request.form.get(f'{attr}_weight', parameter_attributes[attr]['weight']))
            parameter_attributes[attr]['preference'] = request.form.get(f'{attr}_preference', parameter_attributes[attr]['preference'])
        
        session['promethee_parameter_attributes'] = parameter_attributes
        # Save parameter settings to database or memory
        print("Updated parameters:", parameter_attributes)

        # Redirect to processing step (e.g., normalization)
        return redirect('/promethee/decision-matrix?group=' + group)
        # return redirect('/promethee/normalize?group=' + group)

    return render_template('methods/promethee-parameters.html', attributes=parameter_attributes, group=group)


#step 3 (optional)
@app.route('/promethee/decision-matrix', methods=['GET', 'POST'])
def promethee_decision_matrix():

    group = request.args.get('group', 'A')  # Default group "A"

    # Example decision matrix
    decision_matrix = np.array([
            [500, 5, 50, 3, 1000, 2000, -2],
            [700, 6, 80, 4.5, 1500, 3000, 1],
            [600, 4, 60, 2, 1200, 2500, 0]
        ])
    print("DEBUG [promethee_decision_matrix]0: decision_matrix:\n",decision_matrix)
    # decision_matrix = session.get('decision_matrix', decision_matrix)
    # parameter_attributes = session.get('parameter_attributes', parameter_attributes)
    attributes = ['revenue', 
                'revenue_percent_change', 
                'profit', 
                'profits_percent_change', 
                'employees', 
                'assets',
                'change_in_rank']  # Example attributes
    
    #print("DEBUG [promethee_decision_matrix]1: decision_matrix:\n",decision_matrix)

    if request.method == 'POST':

        # Retrieve decision matrix from user input
        # num_alternatives = int(request.form.get('num_alternatives', 3))
        num_alternatives = int(request.form.get('num_alternatives', 20))
        decision_matrix = []
        # decision_matrix = []
        #print("DEBUG [promethee_decision_matrix]2: decision_matrix\n")
        decision_matrix = []
        for i in range(1, num_alternatives + 1):
            row = []

            for attribute in attributes:
            
                value = request.form.get(f'alt_{i}_{attribute}', '')
                #print(f"DEBUG [promethee_decision_matrix]3: Alt {i}, Attr {attribute}, Value: {value}")  # Debug

                try:
                    value = float(value) if value else 0.0
                except ValueError:
                    #print(f"DEBUG [promethee_decision_matrix]4: ValueError")  # Debug    
                    value = 0.0  # Default to 0 if conversion fails
                row.append(value)
            decision_matrix.append(row)

        # Save decision matrix in session or database
        session['promethee_decision_matrix'] = decision_matrix
        #print("DEBUG [promethee_decision_matrix]5: Constructed decision_matrix:\n",decision_matrix)
        # Redirect to processing step (e.g., normalization)
        return redirect('/promethee/normalize?group=' + group)

    # Render form to input decision matrix
    #return render_template('methods/promethee-decision-matrix.html', num_alternatives=3, attributes=attributes, group=group)
    # Render the form with pre-filled values
    return render_template('methods/promethee-decision-matrix.html', 
                           decision_matrix=decision_matrix, 
                           attributes=attributes, 
                           num_alternatives=len(decision_matrix), 
                           group=group,
                           enumerate=enumerate)  # Dodamo enumerate v kontekst)
# step 4
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
    classification_attributes = session.get('promethee_classification_attributes', {})

    if not classification_attributes:
        error_text  = "Classification attributes not found. Please complete the previous step."
        return render_template('error.html', error_text=error_text)
    
    # Example decision matrix
    #decision_matrix = np.array([
    #    [500, 5, 50, 3, 1000, 2000, -2],
    #    [700, 6, 80, 4.5, 1500, 3000, 1],
    #    [600, 4, 60, 2, 1200, 2500, 0]
    #])

    # Example decision matrix
    decision_matrix = session.get('promethee_decision_matrix', {})
    if not decision_matrix:
        error_text  = "Decision matrix not found. Please complete the previous step."
        return render_template('error.html', error_text=error_text)
    print("DEBUG [promethee_normalize]: decision_matrix:\n",decision_matrix)
    print("DEBUG [promethee_normalize]: classification_attributes:\n",classification_attributes)
    # print("promethee_normalize:decision Matrix:", decision_matrix)
    # Normalize decision matrix
    normalized_matrix = classify_and_normalize(decision_matrix, classification_attributes)
        # Store in session
    # session['classification_attributes'] = classification_attributes
    session['promethee_normalized_matrix'] = normalized_matrix.tolist()
    print("DEBUG [promethee_normalize]: normalized_matrix:\n",normalized_matrix)

    # Save normalized matrix (e.g., in memory or database)
    return redirect('/promethee/differences?group=' + group)

# step 5
@app.route('/promethee/differences', methods=['GET'])
def promethee_differences():
    group = request.args.get('group', 'A')

    # Example normalized matrix (replace with saved data)
    #normalized_matrix = np.array([
    #    [0.0, 0.5, 0.0, 0.5, 0.0, 0.0, 1.0],
    #    [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0],
    #    [0.5, 0.0, 0.5, 0.0, 0.5, 0.5, 0.5]
    #])

        # Retrieve from session
    normalized_matrix = np.array(session.get('promethee_normalized_matrix', []))
    # attributes = session.get('attributes', {})
    if normalized_matrix.size == 0:
        error_text  = "Normalized matrix not found. Please complete the previous step."
        return render_template('error.html', error_text=error_text)
    print("DEBUG [promethee_differences]: normalized_matrix:\n",normalized_matrix)

    # Calculate difference matrix
    difference_matrix = calculate_difference_matrix(normalized_matrix)
    session['promethee_difference_matrix'] = difference_matrix.tolist()
    print("DEBUG [promethee_differences]: Difference Matrix:\n", difference_matrix)

    # Save difference matrix (e.g., in memory or database)
    # return "Difference matrix calculated. Proceed to preference functions."
    return redirect('/promethee/preference-functions?group=' + group)



# Route for PROMETHEE method
# step 6 
@app.route('/promethee/preference-functions', methods=['GET'])
def preference_functions():
    group = request.args.get('group', 'A')
    
    # Retrieve difference matrix and parameter attributes
    difference_matrix = session.get('promethee_difference_matrix', None)
    parameter_attributes = session.get('promethee_parameter_attributes', {})
    
    if difference_matrix is None or not parameter_attributes:
        error_text  = "Difference matrix or parameter attributes not found. Please complete previous steps."
        return render_template('error.html', error_text=error_text)
    
    # Ensure the difference matrix is a numpy array
    difference_matrix = np.array(difference_matrix, dtype=float)
    print("DEBUG [preference_functions]: Difference Matrix:\n", difference_matrix)

    # Define preference functions (example for linear)
    num_alternatives = difference_matrix.shape[0]
    num_attributes = difference_matrix.shape[2]
    preference_matrix = np.zeros((num_alternatives, num_alternatives, num_attributes))


    # Define preference functions (example for linear)
    #preference_matrix = np.zeros_like(difference_matrix)


    #for attr_index, (attr, params) in enumerate(parameter_attributes.items()):
    #    for i in range(len(difference_matrix)):
    #        for j in range(len(difference_matrix)):
    #            diff = difference_matrix[i, j, attr_index]
    #            if params['preference'] == 'linear':
    #                preference_matrix[i, j, attr_index] = max(0, diff)
                    
    for attr_index, (attr, params) in enumerate(parameter_attributes.items()):
        for i in range(num_alternatives):
            for j in range(num_alternatives):
                diff = difference_matrix[i, j, attr_index]
                if params['preference'] == 'linear':
                    preference_matrix[i, j, attr_index] = max(0, diff)

    # Save preference matrix in session
    session['promethee_preference_matrix'] = preference_matrix.tolist()
    print("Preference Matrix:\n", preference_matrix)

    return redirect('/promethee/aggregate?group=' + group)


@app.route('/promethee/aggregate', methods=['GET'])
def aggregate_preferences():
    group = request.args.get('group', 'A')

    # Retrieve preference matrix and parameter attributes
    preference_matrix = np.array(session.get('promethee_preference_matrix', []))
    parameter_attributes = session.get('promethee_parameter_attributes', {})
    companies = get_all_companies_for_group(group)
    company_names = session.get('promethee_company_names', [])  # Retrieve company names

    if preference_matrix.size == 0 or not parameter_attributes:
        error_text  = "Preference matrix or parameter attributes not found. Please complete previous steps."
        return render_template('error.html', error_text=error_text)
    
    # Compute aggregated preference matrix
    weights = [params['weight'] for params in parameter_attributes.values()]
    aggregated_preferences = np.sum(preference_matrix * weights, axis=2)
    print("Aggregated Preference Matrix:\n", aggregated_preferences)

    # Compute net flows
    positive_flows = np.mean(aggregated_preferences, axis=1)
    negative_flows = np.mean(aggregated_preferences, axis=0)
    net_flows = positive_flows - negative_flows
    
    # Link company names to Phi values
    #  results = [
    #    {"alternative": company_names[i] if i < len(company_names) else f"Alt {i+1}", "phi": net_flows[i]}
    #    for i in range(len(net_flows))
    #]
    #results = [
    #    {"id": companies[i]['id'], "alternative": company_names[i], "phi": net_flows[i]}
    #    for i in range(len(net_flows))
    #]
    results = [
        {"company_id": companies[i]['id'], "name": company_names[i], "score": net_flows[i]}
        for i in range(len(net_flows))
    ]

    results = sorted(results, key=lambda x: x['score'], reverse=True)  # Sort by Phi descending
    # session['promethee_promethee_results'] = results
    # session['promethee_promethee_results'] = results

    # Debugging output for verification
    from pprint import pprint
    print("PROMETHEE Debug: Results:")
    pprint(results)
    # Save results to database
    save_results(3, results)  # Save results with method_id = 3

    return redirect(url_for('results', method_id=3, group=group))

    # return render_template('methods/promethee-results.html', results=results, group=group)


# Route for PROMETHEE method
# next step ?? or 3
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
    print("DEBUG [classify_attributes]: Difference Matrix:\n", difference_matrix)
    #return render_template('methods/promethee-main.html')
    # Redirect to the next step in PROMETHEE
    # return redirect('/promethee/next')
    return redirect('/promethee')  # Replace '/promethee/next' with the next step




@app.route('/companies')
def companies_table():
    # companies = scrape_fortune500(FORTUNE_URL)  # Pridobi podatke
    companies = get_all_companies()
    # companies_list = companies.to_dict(orient='records')  # Pretvori v seznam slovarjev
    # print("Rendering template: companies/index.html")  # Debug
    companies=format_data_numbers(companies)
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
        companies = format_data_numbers(companies)
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

        return redirect(url_for('results', method_id=1, group=group)) # method_id='AHP'))
    
    # Če je GET zahteva, pokaži obrazec
    group = request.args.get('group', 'A')  # Privzeto skupina A
    return render_template('methods/ahp.html', group=group)




#@app.route('/ahp/results')
#def ahp_results():
#   return render_template('methods/ahp_results.html', results=get_ahp_results())
#

@app.route('/results/<int:method_id>')
def results(method_id):

    group = request.args.get('group', 'A') 
    results = get_results(method_id)
    # method_name = "AHP" if method_id == 1 else "PROMETHEE" if method_id == 2 else "WSM"
    method_name = METHODS.get(method_id, "Unknown Method")  # Dobimo ime metode
    return render_template('results.html', method_name=method_name, results=results, group=group)



@app.route('/compare')
def compare():
    """
    Compare results from all methods (AHP, WSM, etc.)
    """
  
    group = request.args.get('group', 'A') 

    # Retrieve results using the helper function
    rows = get_all_results_with_methods(group)

    print("debug COMPARE(): rows")
    print(rows)
    for row in rows:
        print(row)  # Pretvori SQLite Row v navaden slovar

    # Organize results by company
    comparison_data = {}
    for row in rows:
        method_id, company_id, company_name, score = row
        if company_id not in comparison_data:
            comparison_data[company_id] = {'name': company_name, 'scores': {}}
        comparison_data[company_id]['scores'][METHODS[method_id]] = score

    # Prepare companies for rendering
    companies = list(comparison_data.values())

    return render_template('compare.html', methods=METHODS.values(), companies=companies, group=group)

    # return render_template('compare.html', group=group, ahp=ahp_results, promethee=promethee_results, wsm=wsm_results)



def format_data_numbers(rows):
    formatted_list = []
    for row in rows:
        # Pretvorite sqlite3.Row v slovar
        company = dict(row)
        
        
        # Formatiranje številk in odstotkov
        company['formatted_revenue'] = "{:,.2f}".format(company['revenue']).replace(",", "X").replace(".", ",").replace("X", ".")
        company['formatted_profit'] = "{:,.2f}".format(company['profit']).replace(",", "X").replace(".", ",").replace("X", ".")
        company['formatted_revenue_change'] = "{:.1f}".format(company['revenue_percent_change']).replace(".", ",")
        company['formatted_profit_change'] = "{:.1f}".format(company['profits_percent_change']).replace(".", ",")
        
        
        # Dodaj formatiran slovar v seznam
        formatted_list.append(company)
    return formatted_list



if __name__ == '__main__':
    app.run(debug=True)

