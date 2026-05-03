import pandas as pd

def analyze_atmosphere(DDR1_df, DDR2_df):
    """Analyzing the mean, min, and max of important atmospheric properties at diff pressures"""
    merged = pd.merge(DDR2_df, DDR1_df, on="Profile_identifier")

    grouped = merged.groupby(["level"]) # grouping the merged data by level

    # finding the mean, min, and max data at each pressure level
    stats = grouped.agg({ "T": ["mean", "min", "max"],
        "Dust": ["mean", "min", "max"],
        "H2Oice": ["mean", "min", "max"]})
    return stats

def extract_one_Pa(stats, level_to_eval):
    """Only showing the statistics at the level the user inputted"""
    print(f"Statistics at your chosen level (level {level_to_eval})")
    return stats.loc[level_to_eval]