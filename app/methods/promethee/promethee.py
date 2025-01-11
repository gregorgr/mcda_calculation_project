# /app/methods/promethee/promethee.py
import numpy as np
import pandas as pd


def build_decision_matrix(form_data, attributes):
    """
    Build the decision matrix from form input.
    """
    num_alternatives = int(form_data.get('num_alternatives', 0))
    decision_matrix = []

    for i in range(1, num_alternatives + 1):
        row = []
        for attribute in attributes:
            try:
                value = float(form_data.get(f'alt_{i}_{attribute}', 0))
            except ValueError:
                value = 0.0
            row.append(value)
        decision_matrix.append(row)

    return decision_matrix


def calculate_difference_matrix(normalized_matrix):
    """
    Calculate the difference matrix for each pair of alternatives.

    Parameters:
        normalized_matrix (numpy.ndarray): Normalized decision matrix.

    Returns:
        numpy.ndarray: Difference matrix (alternatives x alternatives x attributes).
    """
    num_alternatives, num_attributes = normalized_matrix.shape
    difference_matrix = np.zeros((num_alternatives, num_alternatives, num_attributes))

    for a in range(num_alternatives):
        for b in range(num_alternatives):
            difference_matrix[a, b] = normalized_matrix[a] - normalized_matrix[b]

    return difference_matrix

def calculate_difference_matrix_new(normalized_matrix):
    """
    Calculate the difference matrix for the PROMETHEE method.
    """
    n, m = normalized_matrix.shape
    difference_matrix = np.zeros((n, n, m))

    for i in range(n):
        for j in range(n):
            difference_matrix[i, j] = normalized_matrix[i] - normalized_matrix[j]

    return difference_matrix


def calculate_preference_functions(difference_matrix, parameter_attributes):
    """
    Compute the preference matrix based on the difference matrix and attributes.

    Parameters:
        difference_matrix (list or np.ndarray): Difference matrix.
        parameter_attributes (dict): Attributes and their parameters (e.g., weight, preference type).

    Returns:
        np.ndarray: Preference matrix.
    """
    # Convert difference_matrix to a NumPy array if it's a list
    difference_matrix = np.array(difference_matrix, dtype=float)

    # Get the shape of the difference matrix
    num_alternatives, _, num_attributes = difference_matrix.shape

    # Initialize the preference matrix
    preference_matrix = np.zeros_like(difference_matrix)

    # Apply preference functions
    for attr_index, (attr, params) in enumerate(parameter_attributes.items()):
        for i in range(num_alternatives):
            for j in range(num_alternatives):
                diff = difference_matrix[i, j, attr_index]
                if params['preference'] == 'linear':
                    preference_matrix[i, j, attr_index] = max(0, diff)

    return preference_matrix





def classify_and_normalize(matrix, attributes):
    """
    Classify attributes into beneficial and non-beneficial categories
    and normalize the evaluation matrix.

    Parameters:
        matrix (list of lists or numpy.ndarray): Decision matrix (alternatives x attributes).
        attributes (dict): Dictionary of attribute classifications:
            {'attribute_name': 'beneficial' or 'non-beneficial'}.

    Returns:
        numpy.ndarray: Normalized decision matrix.
    """
    
    # Ensure matrix is a numpy array
    matrix = np.array(matrix, dtype=float)
    
    # Initialize the normalized matrix
    normalized_matrix = np.zeros_like(matrix, dtype=float)

    for j, (attr_name, attr_type) in enumerate(attributes.items()):
        column = matrix[:, j]  # Get the column for the attribute
        
        if attr_type == 'beneficial':
            # Normalization for beneficial attributes
            normalized_matrix[:, j] = (column - np.min(column)) / (np.max(column) - np.min(column))
        elif attr_type == 'non-beneficial':
            # Normalization for non-beneficial attributes
            normalized_matrix[:, j] = (np.max(column) - column) / (np.max(column) - np.min(column))
        else:
            raise ValueError(f"Invalid attribute type for '{attr_name}': {attr_type}")

    return normalized_matrix



def linguistic_to_numeric(matrix):
    """
    Convert linguistic values to numeric values for the decision matrix.
    Mapping:
    1 - Low
    2 - Below Average
    3 - Average
    4 - Good
    5 - Excellent
    """
    mapping = {
        'Low': 1,
        'Below Average': 2,
        'Average': 3,
        'Good': 4,
        'Excellent': 5
    }
    # Apply mapping to the matrix
    return matrix.replace(mapping)



def validate_matrix(matrix):
    """
    Validate the decision matrix for completeness and consistency.
    """
    if matrix.isnull().values.any():
        raise ValueError("Decision matrix contains missing values.")
    if not all(matrix.dtypes == 'object'):
        raise ValueError("All values in the matrix should initially be strings.")
    return True



def process_decision_matrix(matrix):
    """
    Process the decision matrix:
    - Validate
    - Convert linguistic values to numeric
    """
    validate_matrix(matrix)
    return linguistic_to_numeric(matrix)


def normalize_decision_matrix(decision_matrix, classification_attributes):
    """
    Normalize the decision matrix based on attribute classification.
    """
    matrix = np.array(decision_matrix, dtype=float)
    for i, attribute in enumerate(classification_attributes.keys()):
        column = matrix[:, i]
        if classification_attributes[attribute] == 'beneficial':
            column = column / np.max(column)
        else:  # Non-beneficial
            column = np.min(column) / column
        matrix[:, i] = column

    return matrix


def promethee_aggregate_preferences(preference_matrix, parameter_attributes, companies, company_names):
    """
    Aggregate preference matrix and compute net flows.

    Parameters:
        preference_matrix (list or np.ndarray): Preference matrix.
        parameter_attributes (dict): Attributes and their weights.
        companies (list): List of companies (alternatives).
        company_names (list): Names of the companies.

    Returns:
        list: Results with company names and scores.
    """
    # Convert preference_matrix to NumPy array if it's a list
    preference_matrix = np.array(preference_matrix, dtype=float)

    # Extract weights from parameter_attributes and convert to NumPy array
    weights = np.array([params['weight'] for params in parameter_attributes.values()], dtype=float)

    # Ensure the preference matrix and weights are compatible
    if preference_matrix.shape[2] != len(weights):
        raise ValueError("Number of attributes in preference matrix and weights do not match.")

    # Compute aggregated preference matrix
    aggregated_preferences = np.sum(preference_matrix * weights, axis=2)
    print("Aggregated Preference Matrix:\n", aggregated_preferences)

    # Compute positive and negative flows
    positive_flows = np.mean(aggregated_preferences, axis=1)
    negative_flows = np.mean(aggregated_preferences, axis=0)
    net_flows = positive_flows - negative_flows

    # Combine net flows with company information
    results = [
        {"company_id": companies[i]['id'], "name": company_names[i], "score": net_flows[i]}
        for i in range(len(net_flows))
    ]

    # Sort results by score in descending order
    return sorted(results, key=lambda x: x['score'], reverse=True)
