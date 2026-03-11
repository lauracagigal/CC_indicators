import sys
import os
import os.path as op
import xarray as xr
import geopandas as gpd
import pandas as pd
import cartopy.crs as ccrs
import numpy as np
from scipy import stats

def process_trend_with_nan(sea_level_anomaly):
    # Flatten the data and get a time index
    # first ensure time is the first dimension regardless of other dimensions
    sea_level_anomaly = sea_level_anomaly.transpose('time', ...)
    sla_flat = sea_level_anomaly.values.reshape(sea_level_anomaly.shape[0], -1)
    time_index = pd.to_datetime(sea_level_anomaly.time.values).to_julian_date()

    detrended_flat = np.full_like(sla_flat, fill_value=np.nan)
    detrended_flat_err = np.full_like(sla_flat, fill_value=np.nan)
    trend_rates = np.full(sla_flat.shape[1], np.nan)
    trend_errors = np.full(sla_flat.shape[1], np.nan)
    p_values = np.full(sla_flat.shape[1], np.nan)

    # Loop over each grid point
    for i in range(sla_flat.shape[1]):
        # Get the time series for this grid point
        y = sla_flat[:,i]
        mask = ~np.isnan(y)

        if np.any(mask):
            time_masked = time_index[mask]
            y_masked = y[mask]

            slope, intercept, _, p_value, std_error = stats.linregress(time_masked, y_masked)
            trend = slope * time_index + intercept

            detrended_flat[:,i] = y - trend
            trend_rates[i] = slope
            trend_errors[i] = std_error
            p_values[i] = p_value

    detrended = detrended_flat.reshape(sea_level_anomaly.shape)
    trend_errors_reshaped = trend_errors.reshape(sea_level_anomaly.shape[1:])

    # Calculate trend magnitude
    sea_level_trend = sea_level_anomaly - detrended
    trend_mag = sea_level_trend[-1] - sea_level_trend[0]

    times = pd.to_datetime(sea_level_anomaly['time'].values)
    time_mag = (times[-1] - times[0]).days/365.25 # in years

    trend_rate = trend_mag / time_mag
    trend_err = trend_errors_reshaped / time_mag

    return trend_mag, sea_level_trend, trend_rate, np.nanmean(p_value) , np.nanmean(trend_err)




import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

    # ==================================================
    # CLASSIFY BLEACHING LEVELS
    # ==================================================
def classify_bleaching_level(hotspot, dhw):
    if hotspot <= 0:
        return "No stress"
    elif 0 < hotspot < 1:
        return "Bleaching Watch"
    elif hotspot >= 1 and 0 < dhw < 4:
        return "Bleaching Warning"
    elif hotspot >= 1 and 4 <= dhw < 8:
        return "Alert level 1"
    else:
        return "Alert level 2"
    
def process_bleaching_levels(data_crw):

    # ==================================================
    # PREPARE DATA
    # ==================================================
    df = data_crw.copy()
    df.index = pd.to_datetime(df.index)

    df["year"] = df.index.year
    df["bleaching_level"] = df.apply(
        lambda r: classify_bleaching_level(
            r["SSTA@90th_HS"],
            r["DHW_from_90th_HS>1"]
        ),
        axis=1
    )
    # ==================================================
    # DEFINE PERIODS (SAFE VERSION)
    # ==================================================
    years_sorted = np.sort(df["year"].unique())

    first_10_years = years_sorted[:10]
    last_10_years  = years_sorted[-10:]

    df["period"] = pd.NA
    df.loc[df["year"].isin(first_10_years), "period"] = "First 10 years"
    df.loc[df["year"].isin(last_10_years),  "period"] = "Last 10 years"

    df_periods = df.dropna(subset=["period"])

    # ==================================================
    # COUNT DAYS PER ALERT LEVEL
    # ==================================================
    days_by_level = (
        df_periods
        .groupby(["period", "bleaching_level"])
        .size()
        .rename("n_days")
        .reset_index()
    )

    # Enforce consistent order
    level_order = [
        "No stress",
        "Bleaching Watch",
        "Bleaching Warning",
        "Alert level 1",
        "Alert level 2"
    ]

    days_by_level["bleaching_level"] = pd.Categorical(
        days_by_level["bleaching_level"],
        categories=level_order,
        ordered=True
    )

    days_by_level = days_by_level.sort_values("bleaching_level")

    # Pivot table
    days_pivot = (
        days_by_level
        .pivot(index="bleaching_level", columns="period", values="n_days")
        .fillna(0)
    )

    return df, days_pivot
