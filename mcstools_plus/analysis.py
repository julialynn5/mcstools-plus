import pandas as pd
import numpy as np
from termcolor import colored, cprint

from mcstools_plus.plotting import bin_data, build_full_df
from mcstools_plus.data_loader import split_df_by_level
from mcstools_plus.storm_detection import split_df_by_error

def extract_one_Pa(stats, level_to_eval):
    """Only showing the statistics at the level the user inputted"""
    print(f"Statistics at your chosen level (level {level_to_eval})")
    return stats.loc[level_to_eval]

def analyze_atmosphere(DDR1_df, DDR2_df):
    """Analyzing the mean, min, and max of important atmospheric properties at diff pressures"""
    merged = pd.merge(DDR2_df, DDR1_df, on="Profile_identifier")

    grouped = merged.groupby(["level"]) # grouping the merged data by level

    # finding the mean, min, and max data at each pressure level
    stats = grouped.agg({ "T": ["mean", "min", "max"],
        "Dust": ["mean", "min", "max"],
        "H2Oice": ["mean", "min", "max"]})
    return stats

def validate_binning_stats(DDR1, DDR2, value_col):
    """Validating the mean, min, and max for manual vs automated calculations"""
    df = build_full_df(DDR1, DDR2)
    
    print("Running binning statistical test...\n")
    df = df.copy()

    print("L_s min:", df["L_s"].min())
    print("L_s max:", df["L_s"].max())
    print("Shape:", df.shape)

    heatmap, smallest_Ls, largest_Ls, L_s_bin = bin_data(df, value_col)

    # binning inputted data the exact same way
    df['L_s_binned'] = pd.cut(df['L_s'], bins=L_s_bin)
    df['lat_binned'] = pd.cut(df['Profile_lat'], bins=np.linspace(-90, 90, 61))
    
    # comparing results using .groupby
    grouped_stats = df.groupby(["lat_binned", "L_s_binned"])[value_col].agg(["mean", "min", "max"])

    # using the row that contains the maximum as a test
    max_row = df.loc[df[value_col].idxmax()]
    min_row = df.loc[df[value_col].idxmin()]

    bins_to_test = []
    
    bins_to_test.append((max_row["L_s_binned"], max_row["lat_binned"], "Max bin"))
    bins_to_test.append((min_row["L_s_binned"], min_row["lat_binned"], "Min bin"))

    # also want to test a few random bins
    unique_bins = df[['L_s_binned', 'lat_binned']].dropna().drop_duplicates()
    random_bins = unique_bins.sample(n=min(4, len(unique_bins)), random_state=75)
    for _, row in random_bins.iterrows():
        bins_to_test.append((row["L_s_binned"], row["lat_binned"], "Random bin"))

    # looping through selected bins to test
    print("Looping through the bins I want to test...")
    for Ls_bin, lat_bin, label in bins_to_test:
        print(f"L\u209B bin: {Ls_bin}, Latitude bin: {lat_bin}")
        bin_df = df[(df["L_s_binned"] == Ls_bin) & (df["lat_binned"] == lat_bin)]

        if bin_df.empty:
            print("The selected bin is empty, skipping.\n\n")
            continue
        
        # calculating the mean, min, and max the super duper totally hard way
        manual_mean = bin_df[value_col].mean()
        manual_min = bin_df[value_col].min()
        manual_max = bin_df[value_col].max()

        # stats using .groupby
        auto_stats = grouped_stats.loc[(lat_bin, Ls_bin)]
        group_mean = auto_stats['mean']
        group_min  = auto_stats['min']
        group_max  = auto_stats['max']
    
        # calculating the mean from the heatmap
        lat_center = lat_bin.left
        ls_center  = Ls_bin.left
        auto_mean = heatmap.loc[lat_center, ls_center]
    
        print(f"Manual mean:    {manual_mean}")
        print(f"Manual min:     {manual_min}")
        print(f"Manual max:     {manual_max}\n")
        
        print(f"Automatic mean: {group_mean}")
        print(f"Automatic min:  {group_min}")
        print(f"Automatic max:  {group_max}\n")
        
        print(f"Heatmap mean:   {auto_mean}\n")
    
        # seeing if the mean values "match"
        if np.isclose(manual_mean, group_mean, atol=1e-6) and np.isclose(manual_mean, auto_mean, atol=1e-6):
            cprint("The mean values match!\n\n", "green")
        else:
            cprint("The mean values do NOT match!\n\n", "red")
            
        if np.isclose(manual_max, group_max, atol=1e-6):
            cprint("The max values match!\n\n", "green")
        else:
            cprint("The max values do NOT match!\n\n", "red")
        
        if np.isclose(manual_min, group_min, atol=1e-6):
            cprint("The min values match!\n\n", "green")
        else:
            cprint("The min values do NOT match!\n\n", "red")
