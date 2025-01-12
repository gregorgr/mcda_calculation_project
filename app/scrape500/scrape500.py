import requests
from bs4 import BeautifulSoup
import pandas as pd



# URL za Fortune 500
#FORTUNE_URLx = "https://fortune.com/ranking/global500/search/"



def scrape_fortune500(URL):
    companies = []
    
    try:
        response = requests.get(URL)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Najdi tabelo s podatki podjetij
        table = soup.find('table')
        rows = table.find_all('tr')

        
        for row in rows[1:]:  # Preskoči naslovno vrstico
            cols = row.find_all('td')

            # Pomožna funkcija za čiščenje številčnih vrednosti
            def clean_number(value):
                """Čisti številske vrednosti in jih pretvori v float."""
                if not value or value.strip() in ['-', 'N/A']:  # Prazne ali neveljavne vrednosti
                    return 0.0
                return float(value.strip().replace(',', '').replace('$', '').replace('%', ''))

            # Dodaj podatke podjetja
            companies.append({
                        'rank': int(cols[0].text.strip()),
                        'name': cols[1].text.strip(),
                        'revenue': clean_number(cols[2].text),
                        'revenue_percent_change': clean_number(cols[3].text),
                        'profit': clean_number(cols[4].text),
                        'profits_percent_change': clean_number(cols[5].text),
                        'assets': clean_number(cols[6].text),
                        'employees': clean_number(cols[7].text.strip()),
                        'change_in_rank': int(cols[8].text.strip()) if cols[8].text.strip().lstrip('-').isdigit() else 0,          
                        'years_on_list': int(cols[9].text.strip()) if cols[9].text.strip().isdigit() else 0,
                    })

    except requests.exceptions.RequestException as e:
        print(f"Error with the HTTP request: {e}")
    except ValueError as e:
        print(f"Data extraction error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


    return pd.DataFrame(companies)

#                    'employees': cols[3].text.strip(),
 #                  'revenue_percent_change': clean_number(cols[5].text),
 #                  'profits_percent_change': clean_number(cols[6].text),
 #                  'change_in_rank': int(cols[7].text.strip()) if cols[7].text.strip().isdigit() else 0,
 #                  'assets': clean_number(cols[8].text),
  #                 