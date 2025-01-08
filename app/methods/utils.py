# methods/utils.py
# import numpy as np

#from methods.utils import normalize_matrix, round_scores

def normalize_matrix(matrix):
    """Normalizira matriko po stolpcih."""
    return matrix / matrix.sum(axis=0)

def round_scores(scores, decimals=3):
    return [round(score, decimals) for score in scores]
