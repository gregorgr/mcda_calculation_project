# methods/ahp/utils.py
import numpy as np

def normalize_matrix(matrix):
    """Normalizira matriko po stolpcih."""
    return matrix / matrix.sum(axis=0)