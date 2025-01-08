# /app/methods/promethee/promethee.py
import numpy as np
import pandas as pd

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