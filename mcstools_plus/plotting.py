import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

def split_df_by_time(df):
    """Splitting data into daytime and nighttime dataframes"""
    # LTST = local true solar time
    day = df[(df['LTST'] > 9/24) & (df['LTST'] < 21/24)].copy()
    night = df[(df['LTST'] < 9/24) | (df['LTST'] > 21/24)].copy()
    return day, night

def split_df_by_obsqual(df):
    """Splitting dataframe by observational geometry"""
    grouped = df.groupby('Obs_qual', observed=False)
    obsqual_vals = {name: group for name, group in grouped} 
    return obsqual_vals

def load_in_csv_data(fileloc):
    csv_df = pd.read_csv(fileloc)
    return csv_df
    
def bin_data(df, value_col):
    """Binning the data from the inputted dataframe when making lat vs Ls plots"""
    df = df.copy()
    smallest_ls = df["L_s"].min()
    largest_ls = df["L_s"].max()
    L_s_bin = np.arange(smallest_ls, largest_ls + 0.5, 0.5)
    df['L_s_binned'] = pd.cut(df['L_s'], bins=L_s_bin)
    df['lat_binned'] = pd.cut(df['Profile_lat'], bins=np.linspace(-90, 90, 61))
    df['L_s_center'] = df['L_s_binned'].apply(lambda x: x.mid)
    df['lat_center'] = df['lat_binned'].apply(lambda x: x.mid)
    heatmap = df.pivot_table(columns='L_s_center', index='lat_center', values=value_col, aggfunc='mean', dropna=False, observed=False)
    return heatmap, smallest_ls, largest_ls

def prepare_dust_height_data(DDR2, subset):
    """Prepares bins for either the daytime or nighttime data"""
    subset = subset.copy() # subset is the daytime data OR the nighttime data
    subset["L_s"] = pd.to_numeric(subset["L_s"], errors="coerce")
    subset["degree_bin"] = (subset["L_s"] * 2).astype(int) / 2 # using bins of 1/2 degree Ls

    # shows what indices have what bin degrees so that i can correlate the degrees with the dust values
    key = "Profile_identifier"
    index_map = subset[[key, "degree_bin"]]
    DDR2 = DDR2[DDR2[key].isin(subset[key])].copy()
    DDR2 = DDR2.merge(index_map, on=key)
    DDR2["Dust"] = pd.to_numeric(DDR2["Dust"], errors="coerce")
    
    return (DDR2.groupby(["degree_bin", "level", "Pres"], observed=False)["Dust"].mean().reset_index().sort_values("Pres", ascending=False))

def plot_dust_height_map(df, title, save_path):
    """Plotting the dust height data for the daytime and nighttime"""
    # creating a pivot table with pressure and dust grouped by degree Ls
    pivot = df.pivot_table(columns="degree_bin", index="Pres", values="Dust", aggfunc="mean")
    
    # basic plotting of a seaborn heatmap
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.heatmap(pivot, cmap="rainbow", vmin=0, vmax=0.0085, ax=ax) # vmin and vmax are just the lowest and highest vals shown
    cbar = ax.collections[0].colorbar
    cbar.set_label("Dust opacity per km on the pressure surface at 463 wavenumbers", rotation=270, labelpad=15)
    ax.set_xlabel("$L_s$ (°)")
    ax.set_ylabel("Pressure (Pa)")
    ax.set_title(title)
    plt.savefig(save_path)
    plt.show()

def prepare_Ls_lat_val_plot(ax, df, vmin, vmax, cmap, label, title, smallest_ls, largest_ls):
    """Function that makes the plots because we need to load in 3 different datasets"""
    X, Y = np.meshgrid(df.columns, df.index)
    levels = np.linspace(vmin, vmax, 50)
    cf = ax.contourf(X, Y, df, levels=levels, cmap=cmap, vmin=vmin, vmax=vmax)
    cbar = plt.colorbar(cf, ax=ax)

    # setting the colorbar ticks
    if "Dust" in label:
        ticks = [0.000, 0.001, 0.002, 0.003, 0.004, 0.005]
    elif "Ice" in label:
        ticks = [0.000, 0.0025, 0.005, 0.0075, 0.1]
    elif "Temperature" in label:
        ticks = [120, 140, 160, 180, 200]

    cbar.set_ticks(ticks)
    cbar.set_label(label, fontsize=20)
    cbar.ax.tick_params(labelsize=20)

    ax.set_yticks([-90, -45, 0, 45, 90])
    ax.set_xticks(np.arange(smallest_ls, largest_ls, 0.5))
    ax.tick_params(axis='x', rotation=45)
    ax.set_ylabel("Mars Profile Latitude (°)")
    ax.set_title(title)
    ax.grid(linestyle=":")

def day_vs_night_dust_levels(DDR1, DDR2, start_year, start_month, start_day, end_year, end_month, end_day, save_location):
    # splitting day and night data
    day_DDR1, night_DDR1 = split_df_by_time(DDR1)
    
    # preparing the data for the plot
    day_avg = prepare_dust_height_data(DDR2, day_DDR1)
    night_avg = prepare_dust_height_data(DDR2, night_DDR1)

    # plotting!
    plot_dust_height_map(day_avg, f"Daytime Dust Map ({start_year}-{start_month}-{start_day} to {end_year}-{end_month}-{end_day})", f"{save_location}/day_dust_height_for_{start_year}-{start_month}-{start_day}TO{end_year}-{end_month}-{end_day}.csv.png")
    plot_dust_height_map(night_avg, f"Nighttime Dust Map ({start_year}-{start_month}-{start_day} to {end_year}-{end_month}-{end_day})", f"{save_location}/night_dust_height_for_{start_year}-{start_month}-{start_day}TO{end_year}-{end_month}-{end_day}.png")

def plot_Ls_lat_value(fileloc, start_year, start_month, start_day, end_year, end_month, end_day, save_location):
    df = load_in_csv_data(fileloc)
    day, night = split_df_by_time(df)
    dust_map, Ls_min, Ls_max = bin_data(day[day['Dust_column_err'] < 0.1], 'Dust') # binning and getting rid of vals with large error
    temp_map, _, _ = bin_data(day[day['T_err'] < 3], 'T')
    ice_map, _, _  = bin_data(day[day['H2Oice_column_err'] < 0.1], 'H2Oice')
    
    fig, axes = plt.subplots(3, 1, figsize=(14, 16))
    fig.suptitle(f"Dust opacity, temperature, and water ice opacity data from {start_year}-{start_month}-{start_day} to {end_year}-{end_month}-{end_day}")
    plt.rcParams.update({
    'font.size': 22,
    'axes.titlesize': 26,
    'axes.labelsize': 24,
    'xtick.labelsize': 20,
    'ytick.labelsize': 20,
    'figure.titlesize': 32
})
    
    prepare_Ls_lat_val_plot(axes[0], dust_map, vmin=0, vmax=0.0055, cmap='YlOrBr', label="Dust Optical Depth", title=f"Dust Opacity", smallest_ls=Ls_min, largest_ls=Ls_max)
    prepare_Ls_lat_val_plot(axes[1], temp_map, vmin=120, vmax=240, cmap='rainbow',label="Temperature (K)", title=f"Temperature", smallest_ls=Ls_min, largest_ls=Ls_max)
    prepare_Ls_lat_val_plot(axes[2], ice_map, vmin=0, vmax=0.012, cmap='YlGnBu', label="H2O Ice Opacity", title=f"Water Ice Opacity", smallest_ls=Ls_min, largest_ls=Ls_max)
    
    plt.tight_layout()
    plt.xlabel("$L_s$ (°)")
    plt.savefig(f"{save_location}/Ls_lat_val_for_{start_year}-{start_month}-{start_day}TO{end_year}-{end_month}-{end_day}.png")
    plt.show()
    