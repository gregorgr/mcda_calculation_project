import math


def topsis_normalize_decision_matrix(matrix, weights):
    """
    Normalizira matriko odločanja in upošteva uteži kriterijev.

    :param matrix: Seznam slovarjev, kjer vsak predstavlja vrednosti kriterijev za določeno alternativo.
                   Primer: [{'revenue': 100, 'profit': 50, ...}, {...}]
    :param weights: Normalizirane uteži kriterijev.
                   Primer: {'revenue': 0.3, 'profit': 0.2, ...}
    :return: Normalizirana in ponderirana matrika odločanja.
    """
    # Izračun korena vsote kvadratov za vsak kriterij
    criteria_sums = {key: math.sqrt(sum(row[key]**2 for row in matrix)) for key in matrix[0]}
    
    # Normalizacija in ponderiranje matrike
    normalized_matrix = []
    for row in matrix:
        normalized_row = {key: (row[key] / criteria_sums[key]) * weights[key] for key in row}
        normalized_matrix.append(normalized_row)
    
    return normalized_matrix