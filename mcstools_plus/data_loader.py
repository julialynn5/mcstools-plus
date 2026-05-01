import pandas as pd
from datetime import datetime
import glob

from mcstools.reader import L2Reader
from mcstools.loader import L2Loader

def get_date_string(start_or_end):
    """Making sure date strings are inputted in the correct format"""
    year = int(input(f"Enter the {start_or_end} year (YYYY): "))
    month = int(input(f"Enter the {start_or_end} month (MM): "))
    day = int(input(f"Enter the {start_or_end} day (DD): "))
    print("\n")
    date = datetime(year, month, day)
    return date.strftime("%Y-%m-%d"), year, month, day

def split_df_by_level(dataframe):
    """Splitting the DDR2 data by (pressure) level. Level 29 = 50 Pa."""
    grouped = dataframe.groupby('level')
    level_vals = {name: group for name, group in grouped}
    return level_vals

def loading_data(start_date, end_date, level_to_eval):
    """Loading data (for when someone doesn't have it downloaded on their computer)"""
    # using the L2Loader function from mcstools and grabbing data from the Planetary Database (PDS)
    loader = L2Loader(pds=True)
    
    # mcs data is organized into DDR1 and DDR2 files, where DDR1 contains the basic information
    # about a retrieval (Earth date, solar longitude, profile latitude and longitude, etc...)
    # and DDR2 contains the data at a given pressure level (temperature, dust opacity, etc...)
    print("Loading data... This takes approx 2 mins per day loaded.")
    DDR1_df = loader.load_date_range(start_date, end_date, "DDR1")
    profiles = DDR1_df["Profile_identifier"]
    DDR2_df = loader.load(profiles=profiles, ddr="DDR2") # uses the same dates chosen for DDR1
    
    # splitting the data by pressure level because DDR1 contains only one line of data and DDR2
    # contains data for 105 pressure levels
    level_dict_split = split_df_by_level(DDR2_df)
    level_df = level_dict_split[level_to_eval]

    DDR1_df = DDR1_df.reset_index(drop=True)
    level_df = level_df.reset_index(drop=True)
    complete_dataset = pd.concat([DDR1_df, level_df], axis=1)
    return complete_dataset

def reading_data(data_year, data_month, level_to_eval):
    """Reading data that is downloaded onto a computer"""
    reader = L2Reader(pds=True) # i'm assuming you downloaded data from the PDS
    print("Note for Prof. Davis: you can access the downloaded data in 'mcs_data/atmos.nmsu.edu/PDS/data/MROM_2160'")
    data_load_location = str(input(f"\nInsert data folder location. Stop before the year.\n"))
    # grabbing the .TAB files. can edit to grab specific data, but i'm grabbing the full month.
    print("Reading data...")
    data_location = f"{data_load_location}/**/*.TAB"
    sorted_data = sorted(glob.glob(data_location, recursive=True))
    
    # making a list with all DDR1 data
    DDR1_list = []
    num1 = 0
    for i in sorted_data:
        df_ddr1 = reader.read(i, "DDR1")
        num1+=1
        #print(f"DDR1 {num1} {i}") # if the read in fails, this shows where the weird data comes from
        DDR1_list.append(df_ddr1)
    DDR1_df = pd.concat(DDR1_list)

    DDR2_list = []
    num2 = 0
    for i in sorted_data:
        df_ddr2 = reader.read(i, "DDR2")
        num2+=1
        #print(f"DDR2 {num1} {i}")
        DDR2_list.append(df_ddr2)
    DDR2_df = pd.concat(DDR2_list)
    # only grabbing the level we want from DDR2
    level_dict_split = split_df_by_level(DDR2_df)
    level_df = level_dict_split[level_to_eval]

    DDR1_df = DDR1_df.reset_index(drop=True)
    level_df = level_df.reset_index(drop=True)
    complete_dataset = pd.concat([DDR1_df, level_df], axis=1)
    return complete_dataset

def data_to_csv(df, good_csv_location, data_year, data_month, data_day, read_or_load):
    """Turning read/loaded data into a csv file for ease of use"""
    # the read_or_load is just so we can compare the two!
    df.to_csv(f'{good_csv_location}/{read_or_load}_df_for_{data_year}-{data_month}-{data_day}.csv')

