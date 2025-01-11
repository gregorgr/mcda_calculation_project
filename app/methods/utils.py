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



def format_data_numbers(rows):
    formatted_list = []
    for row in rows:
        # Pretvorite sqlite3.Row v slovar
        company = dict(row)
        
        
        # Formatiranje številk in odstotkov
        company['formatted_revenue'] = "{:,.2f}".format(company['revenue']).replace(",", "X").replace(".", ",").replace("X", ".")
        company['formatted_profit'] = "{:,.2f}".format(company['profit']).replace(",", "X").replace(".", ",").replace("X", ".")
        company['formatted_revenue_change'] = "{:.1f}".format(company['revenue_percent_change']).replace(".", ",")
        company['formatted_profit_change'] = "{:.1f}".format(company['profits_percent_change']).replace(".", ",")
        
        
        # Dodaj formatiran slovar v seznam
        formatted_list.append(company)
    return formatted_list



def round_mcda_method_scores(results, round_to):
    """
    Zaokroži in formatira rezultate v tabeli `scores` glede na `rounding_array`.

    :param results: Seznam podjetij s tabelo `scores`.
    :param methods: Seznam metod (ime stolpcev v `scores`).
    :param rounding_array: Seznam zaokroževanj za vsako metodo.
    :return: Posodobljen seznam podjetij z zaokroženimi vrednostmi.
    """
    formatted_list = []
    for company in results:
        # Pridobi originalni rezultat
        original_score = company['score']

        # Zaokroži rezultat glede na določen indeks
        rounded_score = round(original_score, round_to)

        # Formatiraj številko s piko za tisočice in vejico za decimalke
        formatted_score = "{:,.{precision}f}".format(rounded_score, precision=round_to)
        formatted_score = formatted_score.replace(",", "X").replace(".", ",").replace("X", ".")  # Slovenski zapis
        
        # Create a new dictionary for the row
        new_row = {}
        new_row['id'] = company['id']
        new_row['method_id'] = company['method_id']
        new_row['company_id'] = company['company_id']
        new_row['name'] = company['company_name']
        new_row['company_name'] = company['company_name']
        new_row['formatted_score'] = formatted_score
        new_row['score'] = company['score']

        # Add the new row to the formatted list
        formatted_list.append(new_row)

    return formatted_list



def round_mcda_scores(companies, methods, rounding_array):
    """
    Round and format results in the `scores` table while preserving original values for sorting.

    :param companies: List of companies with their `scores`.
    :param methods: List of methods (columns in `scores`).
    :param rounding_array: List of decimal places for rounding each method.
    :return: Updated list of companies with both original and formatted values.
    """
    for company in companies:
        company['scores_original'] = {}  # Store original scores for sorting
        for method_index, method in enumerate(methods):
            if method in company['scores']:
                # Get the original score
                original_score = company['scores'][method]

                # Round the score
                rounded_score = round(original_score, rounding_array[method_index])

                # Store the original score for sorting
                company['scores_original'][method] = rounded_score

                # Format the score for display
                formatted_score = "{:,.{precision}f}".format(rounded_score, precision=rounding_array[method_index])
                formatted_score = formatted_score.replace(",", "X").replace(".", ",").replace("X", ".")  # Slovene format

                # Update the displayed score
                company['scores'][method] = formatted_score

    return companies


def calculate_all_ranks(companies, methods):
    """
    Calculate ranks for each method and update the companies data.

    Parameters:
        companies (list): List of companies with their scores.
        methods (list): List of method names.

    Returns:
        list: Updated companies with rank data.
    """
    # Prepare a structure to hold scores per method
    method_scores = {method: [] for method in methods}

    # Collect scores for each method
    for company in companies:
        for method in methods:
            score = company['scores_original'].get(method, 0)
            method_scores[method].append((score, company))

    # Calculate ranks for each method
    for method, scores in method_scores.items():
        # Sort scores in descending order for ranking
        sorted_scores = sorted(scores, key=lambda x: x[0], reverse=True)

        # Assign ranks
        rank = 1
        for _, company in sorted_scores:
            if 'scores_rank' not in company:
                company['scores_rank'] = {}
            company['scores_rank'][method] = rank
            rank += 1

    return companies


def normalize_scores(companies, methods):
    """
    Normalize scores for each method across all companies.

    Parameters:
        companies (list): List of companies with their scores.
        methods (list): List of method names.

    Returns:
        list: Updated companies with normalized scores.
    """
    for method in methods:
        # Extract all original scores for this method
        scores = [company['scores_original'].get(method, 0) for company in companies]

        # Calculate min and max for normalization
        min_score = min(scores)
        max_score = max(scores)
        range_score = max_score - min_score if max_score != min_score else 1  # Avoid division by zero

        # Normalize scores
        for company in companies:
            original = company['scores_original'].get(method, 0)
            normalized = (original - min_score) / range_score  # Normalize to 0-1
            if 'scores_normalized' not in company:
                company['scores_normalized'] = {}
            company['scores_normalized'][method] = normalized

    return companies