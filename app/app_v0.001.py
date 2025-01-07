from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt

app = Flask(__name__)

# URL za Fortune 500
FORTUNE_URL = "https://fortune.com/ranking/global500/search/"

# Pomožna funkcija za pridobitev Fortune 500 podatkov
def scrape_fortune500():
    response = requests.get(FORTUNE_URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Pridobi tabelo s podatki podjetij
    table = soup.find('table')
    rows = table.find_all('tr')

    companies = []
    for row in rows[1:]:  # Preskoči naslovno vrstico
        cols = row.find_all('td')
        companies.append({
            'rank': int(cols[0].text.strip()),
            'name': cols[1].text.strip(),
            'revenue': float(cols[2].text.strip().replace(',', '').replace('$', '')),
            'profit': float(cols[3].text.strip().replace(',', '').replace('$', '')),
            'employees': int(cols[4].text.strip().replace(',', ''))
        })
    
    return pd.DataFrame(companies)

# MCDA metoda (npr. normalizacija in uteži)
def mcda_ranking(companies, weights):
    # Normalizacija podatkov
    for col in ['revenue', 'profit', 'employees']:
        companies[col + '_normalized'] = companies[col] / companies[col].max()
    
    # Izračun rezultatov z utežmi
    companies['score'] = (
        weights['revenue'] * companies['revenue_normalized'] +
        weights['profit'] * companies['profit_normalized'] -
        weights['employees'] * companies['employees_normalized']  # Nižja vrednost zaposlenih = boljše
    )
    
    return companies.sort_values(by='score', ascending=False)

# Začetna stran
@app.route('/')
def home():
    return render_template('index.html')

# Endpoint za pridobitev in razvrstitev podjetij
@app.route('/rank', methods=['POST'])
def rank_companies():
    weights = request.json.get('weights', {'revenue': 0.4, 'profit': 0.4, 'employees': 0.2})
    companies = scrape_fortune500()
    ranked_companies = mcda_ranking(companies, weights)
    return ranked_companies.head(10).to_json(orient='records')

# Vizualizacija rezultatov
@app.route('/plot')
def plot_results():
    companies = scrape_fortune500()
    ranked_companies = mcda_ranking(companies, {'revenue': 0.4, 'profit': 0.4, 'employees': 0.2})
    
    plt.figure(figsize=(10, 6))
    plt.bar(ranked_companies['name'][:10], ranked_companies['score'][:10])
    plt.xticks(rotation=45, ha='right')
    plt.title('Top 10 Fortune 500 Companies')
    plt.xlabel('Company')
    plt.ylabel('MCDA Score')
    plt.tight_layout()
    plt.savefig('static/plot.png')
    
    return render_template('plot.html', image_url='/static/plot.png')

if __name__ == '__main__':
    app.run(debug=True)


