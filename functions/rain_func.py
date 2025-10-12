import numpy as np

def consecutive_dry_days(series):
    """
    Calculates the maximum number of consecutive dry days in a series.
    
    Parameters:
    series (list): A list of boolean values representing whether each day is dry or not.
    
    Returns:
    int: The maximum number of consecutive dry days.
    """
    consec_dry = 0
    max_consec_dry = 0
    for value in series:
        if value:  # If it's a dry day (True)
            consec_dry += 1
        else:  # If it's not a dry day (False)
            max_consec_dry = max(max_consec_dry, consec_dry)
            consec_dry = 0
    return max_consec_dry

def count_consecutive_days(series):
    """
    Counts the number of consecutive days with rain in a series.

    Args:
        series (list): A list of boolean values representing rainy days.

    Returns:
        list: A list containing the count of consecutive rainy days for each day in the series.
    """
    count = 0
    result = []
    for value in series:
        if value:
            count += 1
        else:
            count = 0
        result.append(count)
    return result