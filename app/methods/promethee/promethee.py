# /app/methods/promethee/promethee.py
import numpy as np
import pandas as pd



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



def classify_and_normalize(matrix, attributes):
    """
    Classify attributes into beneficial and non-beneficial categories
    and normalize the evaluation matrix.

    Parameters:
        matrix (numpy.ndarray): Decision matrix (alternatives x attributes).
        attributes (dict): Dictionary of attribute classifications:
            {'attribute_name': 'beneficial' or 'non-beneficial'}.

    Returns:
        numpy.ndarray: Normalized decision matrix.
    """
    normalized_matrix = np.zeros_like(matrix, dtype=float)

    for j, (attr_name, attr_type) in enumerate(attributes.items()):
        column = matrix[:, j]
        
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