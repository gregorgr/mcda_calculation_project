# methods/ahp/ahp.py
from numpy import array, sum, amax, linalg, transpose
import numpy as np
from methods.utils import normalize_matrix, round_scores

from db.database import save_results



def calculate_ahp_advance_with_method_id(alternatives, weights):
    """
    Perform advanced AHP and save results.

    Parameters:
        alternatives (list): List of alternatives with criteria values.
        weights (dict): Dictionary of criteria weights.

    Returns:
        list: List of results with global priorities.
    """

    # Filter out criteria with zero weights
    weights = {k: v for k, v in weights.items() if v > 0}
    if len(weights) < 3:
        raise ValueError("At least 3 criteria must have weights greater than 0.")

    # Number of alternatives and criteria
    m = len(alternatives)  # Number of alternatives
    n = len(weights)       # Number of criteria

    print("DEBUG: calculate_ahp_advance_with_method_id")
    print("Filtered weights:", weights)

    # Step 1: Pairwise Comparison Matrix for criteria (PCcriteria)
    PCcriteria = np.array([[weights[crit] / weights[crit2] for crit2 in weights.keys()] for crit in weights.keys()])
    print("PCcriteria Matrix (after validation):", PCcriteria)  # Debug

    # Consistency check for criteria
    lambdamax = np.amax(np.linalg.eigvals(PCcriteria).real)
    CI = (lambdamax - n) / (n - 1) if n > 1 else 0
    RI = [0, 0, 0.58, 0.90, 1.12, 1.24, 1.32, 1.41]  # Random Consistency Index
    CR = CI / RI[n - 1] if n - 1 < len(RI) else 0
    print("Consistency Ratio (CR) for criteria:", CR)  # Debug
    if CR > 0.1:
        print("Pairwise Comparison Matrix for criteria is inconsistent (CR =", CR, ")")

    # Step 2: Pairwise Comparison Matrices for alternatives (PCM)
    PCM = []
    for crit in weights.keys():
        crit_values = [alt[crit] for alt in alternatives]
        crit_values = [val if val != 0 else 1e-10 for val in crit_values]  # Replace 0 with a small positive value
        PCM.append(np.array([[v1 / v2 for v2 in crit_values] for v1 in crit_values]))
        print(f"Pairwise Comparison Matrix for criterion '{crit}':", PCM[-1])  # Debug

    PCM = np.vstack(PCM)  # Combine matrices along criteria
    print("PCM (all criteria combined):", PCM)

    # Step 3: Compute local priorities for alternatives
    def geomean(x):
        """
        Compute geometric mean for each row in a matrix.

        Parameters:
            x (numpy.ndarray): Input matrix.

        Returns:
            numpy.ndarray: Geometric mean for each row.
        """
        z = [1] * x.shape[0]
        for i in range(x.shape[0]):
            for j in range(x.shape[1]):
                if x[i][j] <= 0:  # Ensure no invalid values
                    x[i][j] = 1e-10  # Replace with a small positive value
                z[i] *= x[i][j]
            z[i] = pow(z[i], (1 / x.shape[0]))
        return np.array(z)

    S = []
    for i in range(n):
        submatrix = PCM[i * m:i * m + m, 0:m]
        GMalternatives = geomean(submatrix)
        s = GMalternatives / sum(GMalternatives)
        S.append(s)

    S = np.transpose(S)

    # Step 4: Compute global priorities
    GMcriteria = geomean(PCcriteria)
    w = GMcriteria / sum(GMcriteria)

    global_priorities = S.dot(w.T)
    global_priorities = [round(priority, 3) for priority in global_priorities]

    # Save results to database
    results = [{'company_id': alt['id'], 'name': alt['name'], 'score': global_priorities[i]} for i, alt in enumerate(alternatives)]
    print("Final AHP results:", results)  # Debug
    save_results(1, results)  # Save results with method_id = 1

    return results


def calculate_ahp_advance_with_method_id1(alternatives, weights):
    """
    Perform advanced AHP and save results.

    Parameters:
        alternatives (list): List of alternatives with criteria values.
        weights (dict): Dictionary of criteria weights.

    Returns:
        list: List of results with global priorities.
    """

    # Number of alternatives and criteria
    m = len(alternatives)  # Number of alternatives
    n = len(weights)       # Number of criteria

    print("DEBUG: calculate_ahp_advance_with_method_id")
    print("weights", weights)

     # Pairwise Comparison Matrix for criteria (PCcriteria)
    # Convert weights into a pairwise comparison matrix
    PCcriteria = np.array([[weights[crit] / weights[crit2] for crit2 in weights.keys()] for crit in weights.keys()])
    print("PCcriteria Matrix (after validation):", PCcriteria)  # Debug

      # Consistency check for criteria
    lambdamax = amax(linalg.eigvals(PCcriteria).real)
    CI = (lambdamax - n) / (n - 1)
    RI = [0, 0, 0.58, 0.90, 1.12, 1.24, 1.32, 1.41]  # Random Consistency Index
    CR = CI / RI[n - 1] if n - 1 < len(RI) else 0
    print("Consistency Ratio (CR) for criteria:", CR)  # Debug
    if CR > 0.1:
        print("Pairwise Comparison Matrix for criteria is inconsistent (CR =", CR, ")")
    
    

    # Step 2: Pairwise Comparison Matrices for alternatives (PCM)
    PCM = []
    for crit in weights.keys():
        crit_values = [alt[crit] for alt in alternatives]
        # crit_values = [alt.get(crit, 1e-10) for alt in alternatives]  # Avoid None or missing values
        print(f"Criterion '{crit}' values:", crit_values)  # Debug

        crit_values = [val if val != 0 else 1e-10 for val in crit_values]
        PCM.append(np.array([[v1 / v2 for v2 in crit_values] for v1 in crit_values]))
        print(f"Pairwise Comparison Matrix for criterion '{crit}':", PCM[-1])  # Debug

    PCM = np.vstack(PCM)  # Combine matrices along criteria
    print("PCM (all criteria combined):", PCM)

 

    ### ???
    # Local priorities for alternatives
    #S = []
    #for i in range(n):
    #    GMalternatives = geomean(PCM[i * m:i * m + m, 0:m])
    #    s = GMalternatives / sum(GMalternatives)
    #    S.append(s)
    #S = transpose(S)
    ###

    # Compute global priorities using geometric mean method
    def geomean(x):
        """
        Compute geometric mean for each row in a matrix.
        
        Parameters:
            x (numpy.ndarray): Input matrix.

        Returns:
            numpy.ndarray: Geometric mean for each row.
        """
        z = [1] * x.shape[0]
        for i in range(x.shape[0]):

            for j in range(x.shape[1]):
                if x[i][j] <= 0:  # Ensure no invalid values
                    print("comute geomean invalid value")
                    x[i][j] = 1e-10  # Replace with a small positive value
                z[i] *= x[i][j]
            z[i] = pow(z[i], (1 / x.shape[0]))
        #return z   # old version 
        return np.array(z)

    # Before computing geometric means
    for i, submatrix in enumerate(PCM):
        print(f"Submatrix for criterion {i + 1} (before geomean):", submatrix)

    # Step 3: Compute local priorities for alternatives
    # Consistency check for alternatives
    S = []
    for i in range(n):
        submatrix = PCM[i * m:i * m + m, 0:m]
        print(f"Submatrix for criterion {i + 1}:", submatrix)  # Debug
        GMalternatives = geomean(submatrix)
        print(f"Geometric Mean for criterion {i + 1}:", GMalternatives)  # Debug
        s = GMalternatives / sum(GMalternatives)
        print(f"Local priorities for criterion {i + 1}:", s)  # Debug
        S.append(s)

    S = transpose(S)

    # Step 4: Compute global priorities
    GMcriteria = geomean(PCcriteria)
    print("Geometric Mean of criteria:", GMcriteria)  # Debug
    w = GMcriteria / sum(GMcriteria)
    print("Normalized weights of criteria:", w)  # Debug
    

    global_priorities = S.dot(w.T)
    print("Global priorities before rounding:", global_priorities)  # Debug

    # Round results 
    global_priorities = [round(priority, 3) if priority is not None else 0 for priority in global_priorities]
    ### global_priorities = [round(priority, 3) for priority in global_priorities]
    print("Global priorities after rounding:", global_priorities)  # Debug


    # Save results to database
    results = [{'company_id': alt['id'], 'name': alt['name'], 'score': global_priorities[i]} for i, alt in enumerate(alternatives)]
    print("")
    print("Final AHP results:", results)  # Debug
    save_results(1, results)  # Save results with method_id = 1

    return results




def calculate_ahp_with_method_id(alternatives, weights):
    # Izračunaj AHP
    criteria = list(weights.keys())
    matrix = np.array([[alt[crit] for crit in criteria] for alt in alternatives])
    normalized_matrix = matrix / matrix.sum(axis=0)
    scores = normalized_matrix.dot(np.array(list(weights.values())))

    # Zaokroževanje na 3 decimalna mesta
    scores = [round(score, 3) for score in scores]

    # Pripravi rezultate
    results = [{'company_id': alt['id'], 'name': alt['name'], 'score': scores[i]} for i, alt in enumerate(alternatives)]
    print("Calculated AHP results:", results)  # Debug output

    save_results(1, results)  # 1 = method_id for AHP

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



def get_ahp_results():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM ahp_results ORDER BY score DESC')
    results = cursor.fetchall()
    conn.close()
    return results
