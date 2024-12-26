from datetime import datetime
import pandas as pd
import numpy as np

from datetime import datetime
import pandas as pd
import numpy as np

def exceedance_rate_for_base_period(climate_data, variable_name):
    """
    Calculate the exceedance rates for a given climate variable during a base period.

    Parameters:
    climate_data (DataFrame): The climate data containing the variable of interest.
    variable_name (str): The name of the climate variable.

    Returns:
    tuple: A tuple containing two dictionaries. The first dictionary contains the exceedance rates for each year in the base period.
    The second dictionary contains the exceedance rate for each year in the base period, with the year as the key.

    """
    exceedance_rates = {}
    all_exceedance_data = {}

    base_period_years = range(1961, 1991)
    base_period_data = climate_data[climate_data['DATE'].dt.year.isin(base_period_years)]

    # Precompute thresholds for all days in the base period
    thresholds = {}
    for day in base_period_data['DAY'].unique():
        thresholds[day] = centered_percentile(day, base_period_data, variable_name)

    for out_of_base_year in base_period_years:
        out_of_base_data = climate_data[climate_data['DATE'].dt.year == out_of_base_year].copy()
        out_of_base_data['THRESHOLD'] = out_of_base_data['DAY'].map(thresholds)

        if variable_name == "TMAX":
            exceedance_rate = (out_of_base_data[variable_name] > out_of_base_data['THRESHOLD']).mean()
        elif variable_name == "TMIN":
            exceedance_rate = (out_of_base_data[variable_name] < out_of_base_data['THRESHOLD']).mean()

        exceedance_rates[out_of_base_year] = exceedance_rate
        all_exceedance_data[out_of_base_year] = {out_of_base_year: exceedance_rate}

    return exceedance_rates, all_exceedance_data

def centered_percentile(date, base_df, variable_name):
    """
    Calculate the centered percentile for a given date and variable in a DataFrame.

    Args:
        date (datetime): The date for which to calculate the centered percentile.
        base_df (pandas.DataFrame): The base DataFrame containing the data.
        variable_name (str): The name of the variable for which to calculate the centered percentile.

    Returns:
        float: The centered percentile value.

    """
    filtered_df = base_df[(base_df["DATE"] >= datetime(1960, 12, 29)) & (base_df["DATE"] <= datetime(1991, 1, 2))]
    window_values = []

    for x in filtered_df[filtered_df['DAY'] == date]['DATE']:
        window_values.extend(filtered_df[(filtered_df['DATE'] >= x - pd.Timedelta(days=2)) &
                                         (filtered_df['DATE'] <= x + pd.Timedelta(days=2))][variable_name].tolist())

    if variable_name == "TMAX":
        return np.percentile(window_values, 90)
    elif variable_name == "TMIN":
        return np.percentile(window_values, 10)

def exceedance_rate_for_outbase_period(climate_data, variable_name):
    """
    Calculates the exceedance rate for a given climate variable during an outbase period.

    Parameters:
    climate_data (pd.DataFrame): The climate data containing the variable of interest.
    variable_name (str): The name of the variable to calculate the exceedance rate for.

    Returns:
    pd.DataFrame: A DataFrame containing the exceedance rate for each day in the outbase period.
    """
    
    date_range = pd.date_range('2024-01-01', '2024-12-31', freq='D')
    df_exceedance = pd.DataFrame({'DAY': date_range})

    df_exceedance['THRESHOLD'] = df_exceedance['DAY'].apply(lambda day_value: centered_percentile(day_value, climate_data, variable_name))

    return df_exceedance

def centered_percentile(date, base_df, variable_name):
    """
    Calculate the centered percentile for a given date and variable in a base dataframe.

    Parameters:
    date (datetime): The date for which to calculate the centered percentile.
    base_df (DataFrame): The base dataframe containing the data.
    variable_name (str): The name of the variable for which to calculate the centered percentile.

    Returns:
    float: The centered percentile value.

    """
    filtered_df = base_df[(base_df["DATE"] >= datetime(1960, 12, 29)) & (base_df["DATE"] <= datetime(1991, 1, 2))]
    window_values = []

    for x in filtered_df[filtered_df['DAY'] == date]['DATE']:
        window_values.extend(filtered_df[(filtered_df['DATE'] >= x - pd.Timedelta(days=2)) &
                                         (filtered_df['DATE'] <= x + pd.Timedelta(days=2))][variable_name].tolist())

    if variable_name == "TMAX":
        return np.percentile(window_values, 90)
    elif variable_name == "TMIN":
        return np.percentile(window_values, 10)