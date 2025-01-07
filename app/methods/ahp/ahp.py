from numpy import array, sum, amax, linalg, transpose
import numpy as np
from methods.ahp.utils import normalize_matrix
from db.database import save_results





def calculate_ahp_advance_with_method_id(alternatives, weights):
    """Izvede napreden AHP in shrani rezultate."""
    # Število alternativ in kriterijev
    m = len(alternatives)  # Število alternativ
    n = len(weights)       # Število kriterijev
    
    # Pairwise Comparison Matrika za kriterije (PCcriteria)
    # Primer: Pretvorba uteži v primerjalno matriko
    PCcriteria = np.array([[weights[crit] / weights[crit2] for crit2 in weights.keys()] for crit in weights.keys()])
    
    # Preverjanje skladnosti za kriterije
    lambdamax = amax(linalg.eigvals(PCcriteria).real)
    CI = (lambdamax - n) / (n - 1)
    RI = [0, 0, 0.58, 0.90, 1.12, 1.24, 1.32, 1.41]  # Random Consistency Index
    CR = CI / RI[n - 1] if n - 1 < len(RI) else 0
    if CR > 0.1:
        print("Pairwise Comparison Matrix for criteria is inconsistent (CR =", CR, ")")

    # Pairwise Comparison Matrike za alternative (PCM)
    PCM = []
    for crit in weights.keys():
        crit_values = [alt[crit] for alt in alternatives]
        PCM.append(np.array([[v1 / v2 for v2 in crit_values] for v1 in crit_values]))
    PCM = np.vstack(PCM)  # Združimo matrike po kriterijih

    # Preverjanje skladnosti za alternative
    for i in range(n):
        lambdamax = amax(linalg.eigvals(PCM[i * m:i * m + m, 0:m]).real)
        CI = (lambdamax - m) / (m - 1)
        CR = CI / RI[m - 1] if m - 1 < len(RI) else 0
        if CR > 0.1:
            print(f"Pairwise Comparison Matrix for criterion {i + 1} is inconsistent (CR =", CR, ")")

    # Izračun globalnih prioritet z metodo geom. sredine
    def geomean(x):
        z = [1] * x.shape[0]
        for i in range(x.shape[0]):
            for j in range(x.shape[1]):
                z[i] *= x[i][j]
            z[i] = pow(z[i], (1 / x.shape[0]))
        return z

    # Lokalni prioriteti za alternative
    S = []
    for i in range(n):
        GMalternatives = geomean(PCM[i * m:i * m + m, 0:m])
        s = GMalternatives / sum(GMalternatives)
        S.append(s)
    S = transpose(S)

    # Globalni prioriteti za alternative
    GMcriteria = geomean(PCcriteria)
    w = GMcriteria / sum(GMcriteria)
    global_priorities = S.dot(w.T)

    # Shranjevanje rezultatov v bazo
    results = [{'company_id': alt['id'], 'name': alt['name'], 'score': global_priorities[i]} for i, alt in enumerate(alternatives)]
    print("Calculated advanced AHP results:", results)  # Debug
    save_results(1, results) # 2 = method_id for advanced AHP

    return results




def calculate_ahp(alternatives, weights):
    # Priprava matrike alternativ
    criteria = list(weights.keys())
    matrix = np.array([[alt[crit] for crit in criteria] for alt in alternatives])
    
    # Normalizacija matrike (vsak kriterij deliš z vsoto stolpca)
    normalized_matrix = matrix / matrix.sum(axis=0)
    
    # Izračun ocene za vsako alternativo (uteži * normalizirane vrednosti)
    scores = normalized_matrix.dot(np.array(list(weights.values())))
    
    # Dodaj ocene alternativam
    for i, alt in enumerate(alternatives):
        alt['score'] = scores[i]
    
    return sorted(alternatives, key=lambda x: x['score'], reverse=True)



def calculate_ahp_with_method_id(alternatives, weights):
    # Izračunaj AHP
    criteria = list(weights.keys())
    matrix = np.array([[alt[crit] for crit in criteria] for alt in alternatives])
    normalized_matrix = matrix / matrix.sum(axis=0)
    scores = normalized_matrix.dot(np.array(list(weights.values())))
    
    # Pripravi rezultate
    results = [{'name': alt['name'], 'score': scores[i]} for i, alt in enumerate(alternatives)]
    print("Results from AHP calculation:", results) 
    # Shrani rezultate z metodo "AHP"
    save_results(1, results)
    
    return results





def get_ahp_results():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM ahp_results ORDER BY score DESC')
    results = cursor.fetchall()
    conn.close()
    return results
