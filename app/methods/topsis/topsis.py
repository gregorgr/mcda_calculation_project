import math
import numpy as np
import pandas as pd


def topsis_calculate(decision_matrix, weights, use_entropy=False):
    """
    Calculate TOPSIS scores for the decision matrix.
    
    Parameters:
        decision_matrix (pd.DataFrame): Matrix containing criteria values.
        weights (dict): Criteria weights.
        use_entropy (bool): Whether to calculate weights using entropy.

    Returns:
        list: TOPSIS scores for each alternative.
    """
    # Extract criteria values
    criteria_matrix = decision_matrix[list(weights.keys())].values

    # If `use_entropy` is True, calculate weights using entropy method
    if use_entropy:
        weights = calculate_entropy_weights(criteria_matrix)

    # Normalize the decision matrix
    normalized_matrix = criteria_matrix / np.sqrt((criteria_matrix**2).sum(axis=0))

    # Weight the normalized matrix
    weighted_matrix = normalized_matrix * np.array(list(weights.values()))

    # Determine ideal and anti-ideal solutions
    ideal_solution = np.max(weighted_matrix, axis=0)
    anti_ideal_solution = np.min(weighted_matrix, axis=0)

    # Calculate distances to ideal and anti-ideal solutions
    distance_to_ideal = np.sqrt(((weighted_matrix - ideal_solution) ** 2).sum(axis=1))
    distance_to_anti_ideal = np.sqrt(((weighted_matrix - anti_ideal_solution) ** 2).sum(axis=1))

    # Calculate TOPSIS scores
    scores = distance_to_anti_ideal / (distance_to_ideal + distance_to_anti_ideal)

    return scores




def calculate_entropy_weights(matrix):
    """
    Calculate criteria weights using the entropy method.
    
    Parameters:
        matrix (numpy.ndarray): Decision matrix.
    
    Returns:
        dict: Normalized weights for each criterion.
    """
    # Normalize the matrix column-wise
    normalized_matrix = matrix / matrix.sum(axis=0)

    # Calculate entropy for each criterion
    epsilon = 1e-10  # To avoid log(0)
    entropy = -np.sum(normalized_matrix * np.log(normalized_matrix + epsilon), axis=0) / np.log(matrix.shape[0])

    # Calculate redundancy and weights
    redundancy = 1 - entropy
    weights = redundancy / redundancy.sum()

    return dict(enumerate(weights))


def normalize_weights(weights):
    """Normalize weights to ensure they sum up to 1."""
    total = sum(weights.values())
    return {k: v / total if total > 0 else 0 for k, v in weights.items()}

def calculate_entropy_weights(decision_matrix):
    """
    Calculate weights using the entropy method.
    Parameters:
        decision_matrix (pandas.DataFrame): Decision matrix where rows are alternatives and columns are criteria.
    Returns:
        dict: Normalized weights for each criterion.
    """
    # Convert to numpy array for calculations
    matrix = decision_matrix.to_numpy()
    
    # Normalize decision matrix
    norm_matrix = matrix / matrix.sum(axis=0)
    
    # Calculate entropy
    entropy = -np.nansum(norm_matrix * np.log(norm_matrix + 1e-10), axis=0) / np.log(len(matrix))
    
    # Calculate diversity
    diversity = 1 - entropy
    
    # Determine weights
    weights = diversity / diversity.sum()
    return dict(zip(decision_matrix.columns, weights))


def calculate_topsis_scores(decision_matrix, weights, criteria_types):
    """
    Perform TOPSIS analysis.
    Parameters:
        decision_matrix (pandas.DataFrame): Decision matrix.
        weights (dict): Normalized weights for each criterion.
        criteria_types (list): List of 1 for beneficial or -1 for non-beneficial criteria.
    Returns:
        pandas.Series: TOPSIS scores.
    """
    # Normalize decision matrix
    norm_matrix = decision_matrix / np.sqrt((decision_matrix**2).sum(axis=0))
    
    # Weighted normalized matrix
    weighted_matrix = norm_matrix * np.array([weights[c] for c in decision_matrix.columns])
    
    # Determine ideal and anti-ideal solutions
    ideal = weighted_matrix.max(axis=0) * np.array(criteria_types)
    anti_ideal = weighted_matrix.min(axis=0) * np.array(criteria_types)
    
    # Calculate distances to ideal and anti-ideal solutions
    distance_to_ideal = np.sqrt(((weighted_matrix - ideal)**2).sum(axis=1))
    distance_to_anti_ideal = np.sqrt(((weighted_matrix - anti_ideal)**2).sum(axis=1))
    
    # Calculate TOPSIS scores
    scores = distance_to_anti_ideal / (distance_to_ideal + distance_to_anti_ideal)
    return pd.Series(scores)


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