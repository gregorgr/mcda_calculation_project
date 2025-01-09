# methods/utils.py
# import numpy as np

#from methods.utils import normalize_matrix, round_scores

def normalize_matrix(matrix):
    """Normalizira matriko po stolpcih."""
    return matrix / matrix.sum(axis=0)

def round_scores(scores, decimals=3):
    return [round(score, decimals) for score in scores]

def normalize_weights(weights):
    """
    Normalizira uteži tako, da seštevek vseh uteži postane 1.

    :param weights: Slovar z utežmi kriterijev.
    :return: Slovar z normaliziranimi utežmi.
    """
    total_weight = sum(weights.values())
    if total_weight == 0:
        return {key: 0 for key in weights}  # Če je seštevek 0, vrne vse 0
    return {key: value / total_weight for key, value in weights.items()}
