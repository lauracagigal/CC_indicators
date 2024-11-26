import os
import os.path as op
import pandas as pd
import xarray as xr
import numpy as np

import requests
import re
from io import BytesIO


# MLO
def download_MLO_CO2_data(url):

    """
     Loads MLO CO2 data from a given URL.

     Parameters:
     url (str): The URL of the data file.

     Returns:
     pandas.DataFrame: The loaded MLO CO2 data.
    """

    # The graphs show monthly mean carbon dioxide measured at Mauna Loa Observatory, Hawaii. 
    # The carbon dioxide data on Mauna Loa constitute the longest record of direct measurements of CO2 in the atmosphere.
    #  They were started by C. David Keeling of the Scripps Institution of Oceanography in March of 1958 at a facility of the National 
    # Oceanic and Atmospheric Administration [Keeling, 1976]. NOAA started its own CO2 measurements in May of 1974, and they have run
    # in parallel with those made by Scripps since then [Thoning, 1989]. 

    MLO_data = pd.read_csv(url, sep = r'\s+', na_values = -999.99, header=158, usecols=range(11))
    MLO_data.index = pd.to_datetime(MLO_data['datetime'])
    MLO_data = MLO_data.rename(columns = {'value':'CO2'}).drop(columns=['datetime', 'time_decimal',\
            'year', 'month', 'day', 'hour', 'minute', 'second'])

    return MLO_data

#HOT
def download_HOT_CO2_data(url: str) -> pd.DataFrame:    
    """
    Load the CO2 data from the HOT station.

    Parameters:
    - url (str): The URL to the data file.
    Parameters:
    ----------
    url : str
        The URL to the data file.

    Returns:
    - HOT_data (pandas.DataFrame): The CO2 and pH data from the HOT station.
    """

    # # Get the HOT data from U. Hawaii
    # The data set is called "HOT_surface_CO2.txt" and can be found at http://hahana.soest.hawaii.edu/hotco2/products.html.  
    # The dataset was by John Dore (jdore@montana.edu) and can be cited as:
    # Dore, J.E., R. Lukas, D.W. Sadler, M.J. Church, and D.M. Karl.  2009.  Physical and biogeochemical modulation of ocean 
    # acidification in the central North Pacific.  Proc Natl Acad Sci USA 106:12235-12240.
    # There is also documentation (HOT_surface_CO2_readme.pdf) at http://hahana.soest.hawaii.edu/hot/products/products.html

    # Explanation: The data are laid out in an ASCII table, so we can use pandas read_csv to read them in and put them in a DataFrame.
    # Note that the file has header information at the top, so we will skip that (header=7 to skip the top seven lines).
    # Note also that the file has column headings, so we can read them directly.
    # Finally, this file is not comma separated, but white space separated (data columns are separated by a different number of white spaces).

    HOT_data = pd.read_csv(url, header=7, sep=r'\s+', na_values=-999.0)
    HOT_data.index = pd.to_datetime(HOT_data['date'], format='%d-%b-%y')
    HOT_data = HOT_data.drop(columns=['date']).rename(columns={'pCO2calc_insitu': 'CO2', 'pHmeas_insitu': 'pH'})

    return HOT_data


#GHCN

class GHCN:
    @staticmethod
    def download_country_codes():
        """
        Downloads the GHCN country codes from the NOAA website and returns a DataFrame
        containing the country codes and corresponding country names.

        Returns:
        df_countries (pandas.DataFrame): DataFrame with columns 'Code' and 'Country',
                                        representing the GHCN country codes and country names.
        """
        url = "https://www.ncei.noaa.gov/pub/data/ghcn/daily/ghcnd-countries.txt"

        country_codes = requests.get(url).text
        country_codes = country_codes.split("\n")

        # Create lists
        codes = [line.split(" ")[0] for line in country_codes]  # Code
        countries = [
            " ".join(line.split(" ")[1:]).strip() for line in country_codes
        ]  # Country

        # DataFrame
        df_countries = pd.DataFrame({"Code": codes, "Country": countries})

        return df_countries

    @staticmethod
    def get_country_code(country):
        """
        Retrieves the GHCN country code for a given country.

        Parameters:
        country (str): The name of the country.

        Returns:
        DataFrame: A DataFrame containing the GHCN country code for the given country.
        """
        df = GHCN.download_country_codes()

        return df.loc[df["Country"] == country]

    @staticmethod
    def download_stations_info():
        """
        Downloads the GHCN stations information from the NOAA website and processes it into a DataFrame.

        Returns:
        df_stations (pandas.DataFrame): DataFrame containing the GHCN stations information, including ID, Latitude, Longitude, Elevation, and Name.
        """
        url = "https://www.ncei.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt"

        stations = requests.get(url).text
        stations = stations.split("\n")

        # Process each line dynamically
        processed_data = []
        for line in stations:
            if len(line) > 0:
                parts = line.split()
                station_id = parts[0]  # ID
                latitude = float(parts[1])  # Latitude
                longitude = float(parts[2])  # Longitude
                elevation = float(parts[3])  # Elevation
                name = " ".join(parts[4:])  # Name
                processed_data.append([station_id, latitude, longitude, elevation, name])

        # Create DataFrame
        df_stations = pd.DataFrame(
            processed_data, columns=["ID", "Latitude", "Longitude", "Elevation", "Name"]
        )

        return df_stations

    @staticmethod
    def extract_dict_data_var(GHCND_dir, var, df_country_stations):
        """
        Extracts data for a specific variable from GHCND files for each station in df_country_stations.

        Parameters:
        GHCND_dir (str): The directory where the GHCND files are located.
        var (str): The variable to extract from the GHCND files.
        df_country_stations (pandas.DataFrame): The DataFrame containing information about the country stations.

        Returns:
        list: A list containing dictionaries with information about the extracted data for each station.
        """
        dict_name = f"dict_{var}"
        globals()[dict_name] = []
        IDS = []
        for i in range(len(df_country_stations)):
            
            url_download = GHCND_dir + df_country_stations.iloc[i]['ID'] + '.csv'

            df = pd.read_csv(url_download, na_values=['-9999'])
            df.index = pd.to_datetime(df['DATE'])
            
            if var in df.columns:

                # print(f'Var: {var}, Station: {df_country_stations.iloc[i]['ID']}, {df_country_stations.iloc[i]['Name']}')
                IDS.append(df_country_stations.iloc[i]['ID'])

                if var == 'TMIN' or var == 'TMAX':
                    df[var] = df[var] / 10
                    label = f'Station {df_country_stations.iloc[i]['ID']}' 
                else:
                    label = f'Station {df_country_stations.iloc[i]['ID']}' 

                info_dic = {'data' : df[[var]], 'var' : var, 'ax' : 1, 'label' : label}
                globals()[dict_name].append(info_dic)           
        
        return globals()[dict_name], IDS
    

#IBTrACS
    
def download_ibtracs(url, basin=None):
    """
    Downloads a file from the given URL and returns an xarray dataset.

    Parameters:
    url (str): The URL of the file to be downloaded.
    basin (str, optional): The basin to filter the dataset by. Defaults to None.

    Returns:
    xr.Dataset: The downloaded file as an xarray dataset.

    Raises:
    None
    """
    
    response = requests.get(url)
    # Verify the request was successful
    if response.status_code == 200:
        tcs = xr.open_dataset(BytesIO(response.content))
    else:
        print(f"Error while downloading file: {response.status_code}")
    
    if basin:
        tcs = tcs.isel(storm=np.where(tcs.isel(date_time=0).basin.values.astype(str) == basin)[0])

    return tcs[['wmo_wind', 'wmo_pres', 'name']]
