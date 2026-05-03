import pandas as pd
from datetime import datetime, timedelta
import glob

from mcstools.reader import L2Reader
from mcstools.loader import L2Loader

def get_date_string(start_or_end):
    """Making sure date strings are inputted in the correct format to the loader"""
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

def build_day_list(start_year, start_month, start_day, end_year, end_month, end_day):
    """Builds a list of the days between the inputted user data"""
    start = datetime(start_year, start_month, start_day)
    end = datetime(end_year, end_month, end_day)
    days = []
    current = start
    
    while current <= end:
        days.append(current.strftime("%Y%m%d"))
        current += timedelta(days=1)
    return days

def collect_files(path, start_year, start_month, start_day, end_year, end_month, end_day):
    """For the reader, grabbing the files between the start and end days"""
    valid_days = build_day_list(start_year, start_month, start_day, end_year, end_month, end_day)

    all_files = []

    for day in valid_days: # going through the days until we reach the end of the days list
        year = day[:4]
        year_month = day[:6]
        folder = f"{path}/{year}/{year_month}/{day}"
        pattern = f"{folder}/*.TAB"
        files = glob.glob(pattern)
        print(f"{day}: {len(files)} files")
        all_files.extend(files)

    all_files = sorted(all_files)
    if len(all_files) == 0:
        print("No files in this directory")

    return all_files

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
    return complete_dataset, DDR1_df, DDR2_df

def reading_data(start_year, start_month, start_day, end_year, end_month, end_day, level_to_eval):
    """Reading data that is downloaded onto a computer"""
    reader = L2Reader(pds=True) # i'm assuming you downloaded data from the PDS
    print("Note for Prof. Davis: you can access the downloaded data in 'mcs_data/atmos.nmsu.edu/PDS/data/MROM_2160/DATA'")
    
    # UNCOMMENT THIS OUT 
    #path = str(input(f"\nInsert data folder location. Stop before the year.\n"))
    path = 'mcs_data/atmos.nmsu.edu/PDS/data/MROM_2160/DATA'
    # grabbing the .TAB files. can edit to grab specific data, but i'm grabbing the full month.
    print("Reading data... This will take about 1 minute.")
    sorted_data = collect_files(path, start_year, start_month, start_day, end_year, end_month, end_day)
    
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
    return complete_dataset, DDR1_df, DDR2_df

def data_to_csv(df, good_csv_location, start_year, start_month, start_day, end_year, end_month, end_day, read_or_load):
    """Turning read/loaded data into a csv file for ease of use"""
    # the read_or_load is just so we can compare the two!
    df.to_csv(f'{good_csv_location}/{read_or_load}_df_for_{start_year}-{start_month}-{start_day}TO{end_year}-{end_month}-{end_day}.csv')
    return f'{good_csv_location}/{read_or_load}_df_for_{start_year}-{start_month}-{start_day}TO{end_year}-{end_month}-{end_day}.csv'

