import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import rasterio
from rasterio.enums import Resampling
import warnings
from rasterio.errors import NotGeoreferencedWarning
warnings.filterwarnings("ignore", category=NotGeoreferencedWarning) # i dont want to use a .tif so get rid of warning

from mcstools_plus.data_loader import split_df_by_level

def split_df_by_time(df):
    """Splitting data into daytime and nighttime dataframes"""
    # LTST = local true solar time
    day = df[(df['LTST'] > 9/24) & (df['LTST'] < 21/24)].copy()
    night = df[(df['LTST'] < 9/24) | (df['LTST'] > 21/24)].copy()
    return day, night

def load_in_csv_data(fileloc):
    """Loading in data previously saved into a csv file"""
    csv_df = pd.read_csv(fileloc)
    return csv_df

def build_full_df(DDR1, DDR2):
    """Merges DDR1 and DDR2 using Profile_identifier"""
    return DDR2.merge(DDR1[['Profile_identifier', 'Profile_lat', 'L_s', 'LTST', 'Dust_column', 'Dust_column_err']], on='Profile_identifier', how='left')
    
def bin_data(df, value_col):
    """Binning the data from the inputted dataframe when making lat vs Ls plots"""
    df = df.copy()
    # using the largest and smallest Ls (solar longitude) values to define the bins
    smallest_Ls = df["L_s"].min()
    largest_Ls = df["L_s"].max()
    smallest_Ls = np.floor(df["L_s"].min() * 2) / 2
    largest_Ls  = np.ceil(df["L_s"].max() * 2) / 2
    
    L_s_bin = np.arange(smallest_Ls, largest_Ls + 0.5, 0.5) # bins of 0.5 degrees in Ls
    df['L_s_binned'] = pd.cut(df['L_s'], bins=L_s_bin)
    df['lat_binned'] = pd.cut(df['Profile_lat'], bins=np.linspace(-90, 90, 61))
    df['L_s_center'] = df['L_s_binned'].apply(lambda x: x.left) # definining the bins from the left to prevent data gaps in the plots
    df['lat_center'] = df['lat_binned'].apply(lambda x: x.left) # calling it center but its actually left lol

    # defining the heatmap using a pivot table
    heatmap = df.pivot_table(columns='L_s_center', index='lat_center', values=value_col, aggfunc='mean', dropna=False, observed=False)
    heatmap = heatmap.dropna(axis=1, how='all')
    return heatmap, smallest_Ls, largest_Ls, L_s_bin

def prepare_dust_height_data(df):
    """Prepares bins for either the daytime or nighttime data"""
    df = df.copy()
    df["L_s"] = pd.to_numeric(df["L_s"], errors="coerce")
    # 0.5-degree bins
    df["degree_bin"] = (df["L_s"] * 2).astype(int) / 2
    df["Dust"] = pd.to_numeric(df["Dust"], errors="coerce")
    df["Pres"] = df["Pres"].round().astype(int)
    return (df.groupby(["degree_bin", "level", "Pres"], observed=False)["Dust"].mean().reset_index().sort_values("Pres", ascending=False))

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
    ax.tick_params(axis='y', rotation=45)
    ax.set_title(title)
    plt.savefig(save_path)
    plt.show()

def prepare_Ls_lat_val_plot(ax, df, vmin, vmax, cmap, label, title, smallest_Ls, largest_Ls):
    """Function that makes the plots because we need to load in 3 different datasets"""
    X, Y = np.meshgrid(df.columns, df.index)
    levels = np.linspace(vmin, vmax, 50)
    cf = ax.contourf(X, Y, df, levels=levels, cmap=cmap, vmin=vmin, vmax=vmax)
    cbar = plt.colorbar(cf, ax=ax)

    # setting the colorbar ticks so they're pretty
    if "Dust" in label:
        ticks = [0.000, 0.001, 0.002, 0.003, 0.004, 0.005]
    elif "Ice" in label:
        ticks = [0.000, 0.0025, 0.005, 0.0075, 0.01]
    elif "Temperature" in label:
        ticks = [120, 140, 160, 180, 200, 220]
    cbar.set_ticks(ticks)
    cbar.set_label(label)

    # latitude and Ls ticks
    ax.set_yticks([-90, -45, 0, 45, 90])
    ax.set_xticks(np.arange(smallest_Ls, largest_Ls, 0.5))
    ax.set_ylabel("Latitude (°)")
    ax.set_title(title) # makes naming each subplot easy!
    ax.grid(linestyle=":")

def day_vs_night_dust_levels(DDR1, DDR2, start_year, start_month, start_day, end_year, end_month, end_day, save_location):
    """Splitting up, plotting, and saving the daytime and nighttime dust height data"""
    # splitting day and night data
    df = build_full_df(DDR1, DDR2)
    day, night = split_df_by_time(df)
    
    # preparing the data for the plot
    day_avg = prepare_dust_height_data(day)
    night_avg = prepare_dust_height_data(night)

    # plotting!
    plot_dust_height_map(day_avg, f"Daytime Dust Map ({start_year}-{start_month}-{start_day} to {end_year}-{end_month}-{end_day})", f"{save_location}/day_dust_height_for_{start_year}-{start_month}-{start_day}to{end_year}-{end_month}-{end_day}.png")
    plot_dust_height_map(night_avg, f"Nighttime Dust Map ({start_year}-{start_month}-{start_day} to {end_year}-{end_month}-{end_day})", f"{save_location}/night_dust_height_for_{start_year}-{start_month}-{start_day}to{end_year}-{end_month}-{end_day}.png")

def plot_Ls_lat_value(fileloc, start_year, start_month, start_day, end_year, end_month, end_day, save_location):
    """Plotting the lat vs Ls plots for temp, dust opacity, and water ice opacity"""
    df = load_in_csv_data(fileloc)
    day, night = split_df_by_time(df)
    dust_map, Ls_min, Ls_max, _ = bin_data(day[day['Dust_column_err'] < 0.1], 'Dust') # binning and getting rid of vals with large error
    temp_map, _, _, _ = bin_data(day[day['T_err'] < 3], 'T')
    ice_map, _, _, _  = bin_data(day[day['H2Oice_column_err'] < 0.1], 'H2Oice')
    
    fig, axes = plt.subplots(3, 1, figsize=(14, 16))
    fig.suptitle(f"Dust opacity, temperature, and water ice opacity data from {start_year}-{start_month}-{start_day} to {end_year}-{end_month}-{end_day}")

    # using the defined function so i dont have to do the exact same process three times! :D
    prepare_Ls_lat_val_plot(axes[0], dust_map, vmin=0, vmax=0.005, cmap='YlOrBr', label="Dust Optical Depth", title=f"Dust Opacity", smallest_Ls=Ls_min, largest_Ls=Ls_max)
    prepare_Ls_lat_val_plot(axes[1], temp_map, vmin=120, vmax=220, cmap='rainbow',label="Temperature (K)", title=f"Temperature", smallest_Ls=Ls_min, largest_Ls=Ls_max)
    prepare_Ls_lat_val_plot(axes[2], ice_map, vmin=0, vmax=0.01, cmap='YlGnBu', label="H2O Ice Opacity", title=f"Water Ice Opacity", smallest_Ls=Ls_min, largest_Ls=Ls_max)

    # single x axis label for Ls
    plt.xlabel("$L_s$ (°)")
    # saving and showing
    plt.savefig(f"{save_location}/Ls_lat_val_for_{start_year}-{start_month}-{start_day}to{end_year}-{end_month}-{end_day}.png")
    plt.show()

def process_pressure_level(DDR1, DDR2):
    """"Making heatmaps for the important pressure levels"""
    df = build_full_df(DDR1, DDR2)
    df = df[['Profile_lat','L_s','LTST','level','Pres','T','T_err','Dust','Dust_err','H2Oice','H2Oice_err']]
    levels = {"200 Pa": 18, "100 Pa": 24, "50 Pa": 29, "25 Pa": 34, "10 Pa": 42, "1 Pa": 60}
    daytime, _ = split_df_by_time(df)
    level_dict = split_df_by_level(daytime)

    # i want consistent Ls vals so i'm running it once at 50 Pa to define all Ls bins
    df_50Pa = level_dict[29]
    _, Ls_min, Ls_max, L_s_bin = bin_data(df_50Pa, 'T')

    # defining the dicts i will use
    temp_maps = {}
    dust_maps = {}
    ice_maps = {}
    
    for label, lvl in levels.items():
        # going through each pressure and defining the temp, dust, and h2o ice at that level
        subset = level_dict[lvl]
        temp, _, _, _ = bin_data(subset, 'T')
        dust, _, _, _ = bin_data(subset, 'Dust')
        ice, _, _, _  = bin_data(subset, 'H2Oice')
        temp_maps[label] = temp
        dust_maps[label] = dust
        ice_maps[label] = ice

    return temp_maps, dust_maps, ice_maps, Ls_min, Ls_max

def prepare_plot_important_pressures_grid(data_dict, vmin, vmax, cmap, title, cbar_label, Ls_min, Ls_max, save_location, start_year, start_month, start_day, end_year, end_month, end_day):
    """Making the plot for the pressures we want to look at"""
    fig, axs = plt.subplots(2, 3, figsize=(10, 6), constrained_layout=True)
    axs = axs.flatten()

    levels = np.linspace(vmin, vmax, 56)
    # going through the dictionary and creating contour plots for each pressure level
    for i, (ax, (label, data)) in enumerate(zip(axs, data_dict.items())):
        
        if data.shape[1] < 2 or data.shape[0] < 2: # to help when we are going through sparse data
            ax.set_title(f"{label}\n(no data)")
            ax.axis('off')
            continue
            
        X, Y = np.meshgrid(data.columns, data.index)
        cf = ax.contourf(X, Y, data, levels=levels, cmap=cmap, vmin=vmin, vmax=vmax)
        ax.set_title(label)
        xticks = np.arange(Ls_min, Ls_max, 0.5)
        ax.set_xticks(xticks[::1]) # show every other tick
        ax.tick_params(axis='x', rotation=25)
        if i >= 3: # for only the bottom 3 plots put the Ls label
            ax.set_xlabel("$L_s$ (°)")
        if i % 3 == 0:
            ax.set_ylabel("Latitude (°)")

    cbar = fig.colorbar(cf, ax=axs, location='right', pad=0.1)
    cbar.set_label(cbar_label, rotation=270, labelpad=15)
    
    if "Dust" in cbar_label:
        ticks = [0.000, 0.001, 0.002, 0.003, 0.004, 0.005]
    elif "Ice" in cbar_label:
        ticks = [0.000, 0.0025, 0.005, 0.0075, 0.01]
    elif "Temperature" in cbar_label:
        ticks = [120, 140, 160, 180, 200, 220]

    cbar.set_ticks(ticks)
    fig.suptitle(title)
    plt.savefig(f"{save_location}/different_pressures_{title}_plot_{start_year}-{start_month}-{start_day}to{end_year}-{end_month}-{end_day}.png")
    plt.show()

def plotting_different_pressures(DDR1, DDR2, save_location, start_year, start_month, start_day, end_year, end_month, end_day):
    """Making the plots for the important pressures we noted above"""
    temp_maps, dust_maps, ice_maps, Ls_min, Ls_max = process_pressure_level(DDR1, DDR2)
    vmin_dust=0
    vmax_dust=0.005
    vmin_temp=120
    vmax_temp=220
    vmin_ice=0
    vmax_ice=0.01
    prepare_plot_important_pressures_grid(temp_maps, vmin_temp, vmax_temp, 'rainbow',"Temperature", "Temperature (K)", Ls_min, Ls_max, save_location, start_year, start_month, start_day, end_year, end_month, end_day)
    prepare_plot_important_pressures_grid(dust_maps, vmin_dust, vmax_dust, 'YlOrBr', "Dust", "Dust Opacity", Ls_min, Ls_max, save_location, start_year, start_month, start_day, end_year, end_month, end_day)
    prepare_plot_important_pressures_grid(ice_maps, vmin_ice, vmax_ice, 'YlGnBu', "Ice", "H2O Ice Opacity", Ls_min, Ls_max, save_location, start_year, start_month, start_day, end_year, end_month, end_day)

def prepare_curves(data_dict, ylabel, Ls_min, Ls_max, ax):
    """Making the lines for the plots of temp and dust for different pressures vs time"""
    for label, data in data_dict.items():
        curve = data.mean(axis=0)
        ax.plot(curve.index, curve.values, label=label)

    ax.set_xlabel("$L_s$ (°)")
    ax.set_ylabel(ylabel)
    ax.set_xlim(Ls_min, Ls_max - 0.5)
    ax.legend()

def plot_curves(DDR1, DDR2, save_location, start_year, start_month, start_day, end_year, end_month, end_day):
    """Making the actual plots"""
    temp_maps, dust_maps, ice_maps, Ls_min, Ls_max = process_pressure_level(DDR1, DDR2)
    fig, axs = plt.subplots(1, 2, figsize=(12, 6), constrained_layout=True)
    
    prepare_curves(temp_maps, "Temperature (K)", Ls_min, Ls_max, axs[0])
    prepare_curves(dust_maps, "Dust Opacity", Ls_min, Ls_max, axs[1])
    
    fig.suptitle("Cross sections of Temperature and Dust Opacity over Time")
    plt.savefig(f"{save_location}/crosssection_{start_year}-{start_month}-{start_day}to{end_year}-{end_month}-{end_day}.png")
    plt.show()

def preparing_lat_lon_plots(fileloc, save_location, start_year, start_month, start_day, end_year, end_month, end_day):
    """Preparing latitude vs longitude temp plots with Mars topography in background"""
    plt.rcParams.update({'font.size': 12, 'axes.titlesize': 14, 'axes.labelsize': 12, 'xtick.labelsize': 12, 'ytick.labelsize': 12})
    df = load_in_csv_data(fileloc)
    df = df.copy()
    smallest_Ls = df["L_s"].min()
    largest_Ls = df["L_s"].max()
    
    L_s_bin = np.arange(smallest_Ls, largest_Ls + 0.5, 0.5)
    day, night = split_df_by_time(df)

    vmin = 140 # temperature scale
    vmax = 210

    df['L_s_bin'] = pd.cut(df['L_s'], bins=L_s_bin)

    dem_file = "mcstools_plus/mcstools_plus_example_data/mars_hrsc_mola_blenddem_global_200mp_1024.jpg"

    scale_factor = 0.9  # used to reduce resolution
    # using rasterio to load in the dem file
    with rasterio.open(dem_file) as src:
        dem = src.read(1,out_shape=(int(src.height * scale_factor), int(src.width * scale_factor)), resampling=Resampling.bilinear)
        dem = np.flipud(dem)
        lon_dem = np.linspace(src.bounds.left, src.bounds.right, dem.shape[1])
        lat_dem = np.linspace(src.bounds.bottom, src.bounds.top, dem.shape[0])

    n_bins = len(L_s_bin) - 1
    n_cols = 2
    n_rows = int(np.ceil(n_bins / n_cols))
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(10, 6), sharex=True, sharey=True)
    axes = axes.flatten()

    lon_bins = np.linspace(-180, 180, 15) # 15 bins of 24 degrees
    lat_bins = np.linspace(-90, 90, 10) # 10 bins of 18 degrees
    lon_centers = (lon_bins[:-1] + np.diff(lon_bins)/2)
    lat_centers = (lat_bins[:-1] + np.diff(lat_bins)/2)

    for i, L_s_bin in enumerate(df['L_s_bin'].cat.categories):
        df_bin = df[df['L_s_bin'] == L_s_bin].copy()
        ax = axes[i]
    
        df_bin['lon_bin'] = np.digitize(df_bin['Profile_lon'], lon_bins) - 1
        df_bin['lat_bin'] = np.digitize(df_bin['Profile_lat'], lat_bins) - 1
        df_bin['Profile_lon_center'] = lon_centers[df_bin['lon_bin'].values]
        df_bin['Profile_lat_center'] = lat_centers[df_bin['lat_bin'].values]

        # creating heatmap
        heatmap_data = df_bin.pivot_table(columns='Profile_lon_center', index='Profile_lat_center', values='T', aggfunc='mean', dropna=False, observed=False).reindex(index=lat_centers, columns=lon_centers)
        
        # plotting elevation contours
        dem_min = np.nanmin(dem)
        dem_max = np.nanmax(dem)
        elev_levels = np.linspace(dem_min, dem_max, 6) 
        elev_contours = ax.contour(np.linspace(-180, 180, dem.shape[1]),np.linspace(-90, 90, dem.shape[0]), dem,levels=elev_levels, colors='grey',linewidths=0.7,zorder=1)

        # plotting temp contours on top
        contourf = ax.contourf(lon_centers,lat_centers,heatmap_data,levels=np.linspace(vmin, vmax, 56),cmap='rainbow',alpha=1,zorder=0)
    
        # ticks
        lat_ticks = [-45, 0, 45]
        lat_labels = [str(t) for t in lat_ticks]
        if i % n_cols == 0:
            # only plotting lat ticks on the lefttmost axis
            ax.set_yticks(lat_ticks)
            ax.set_yticklabels(lat_labels)
        else:
            ax.set_yticklabels([])
    
        lon_ticks = [-120, -60, 0, 60, 120]
        lon_labels = [str(t) for t in lon_ticks]
        if i // n_cols == n_rows - 1:
            # only plotting long ticks on the bottommost axis
            ax.set_xticks(lon_ticks)
            ax.set_xticklabels(lon_labels, rotation=45)
        else:
            ax.set_xticklabels([])
    
        # labelling Ls in the top corner of each bin
        ax.text(0.02, 0.2, f"L\u209B {L_s_bin.left:.0f}°", transform=ax.transAxes, fontweight='semibold', va='top', ha='left', color='black', bbox=dict(facecolor='white', alpha=0.6, edgecolor='none', boxstyle='round,pad=0.2'))
    
        ax.minorticks_on()
        ax.grid(color='navy', linestyle=':', linewidth=0.3)
        
    # colorbar
    cbar_ax = fig.add_axes([0.15, 0.04, 0.7, 0.02])
    cbar = fig.colorbar(contourf, cax=cbar_ax, orientation='horizontal')
    cbar.set_label("Temperature (K)")
    int_ticks = np.arange(np.ceil(vmin), np.floor(vmax)+1, 10)
    cbar.set_ticks(int_ticks)
    cbar.set_ticklabels([str(int(t)) for t in int_ticks])
    fig.supxlabel("Longitude (°)", y=0.06)
    fig.supylabel("Latitude (°)", x=0.06)
    fig.subplots_adjust(hspace=0.12, wspace=0.12, left=0.12, right=0.95, top=0.95, bottom=0.2)
    plt.suptitle(f"Mars Temperature vs Solar Longitude for {start_year}-{start_month}-{start_day} to {end_year}-{end_month}-{end_day}")
    plt.savefig(f"{save_location}/lat_long_plot_{start_year}-{start_month}-{start_day}to{end_year}-{end_month}-{end_day}.png")
    plt.show()

def vertical_cross_section_plots(DDR1, DDR2, save_location, start_year, start_month, start_day, end_year, end_month, end_day):
    """Making vertical cross section plots of dust, temp, and ice vs time"""
    df = build_full_df(DDR1, DDR2)
    # lowkey this is doing about the same thing as prepare_plot_important_pressures_grid but for all pressures but whateva
    # instead of splitting but the important levels, getting all levels
    level_dict = {lvl: g.reset_index(drop=True) for lvl, g in df.groupby("level")}
    
    pressure_profile = []
    temperature_profile = []
    dust_profile = []
    ice_profile = []
    levels_available = sorted(level_dict.keys())

    # for each of the levels available, we are taking its average
    for lvl in levels_available:
        df_lvl = level_dict[lvl]
        pres = df_lvl["Pres"].mean() if "Pres" in df_lvl.columns else np.nan
        temp = df_lvl["T"].mean() if "T" in df_lvl.columns else np.nan
        dust = df_lvl["Dust"].mean() if "Dust" in df_lvl.columns else np.nan
        ice = df_lvl["H2Oice"].mean() if "H2Oice" in df_lvl.columns else np.nan
    
        pressure_profile.append(pres)
        temperature_profile.append(temp)
        dust_profile.append(dust)
        ice_profile.append(ice)
    
    pressure_profile = np.array(pressure_profile)
    temperature_profile = np.array(temperature_profile)
    dust_profile = np.array(dust_profile)
    ice_profile = np.array(ice_profile)
    
    # going to do this in the fugly lazy way because im tired of making separate plotting functions
    fig, axes = plt.subplots(1, 3, figsize=(18, 8), sharey=True)

    # dust
    axes[0].plot(dust_profile, pressure_profile, marker="o")
    axes[0].invert_yaxis()
    axes[0].set_xlabel("Dust Opacity", fontsize=25)
    axes[0].set_ylabel("Pressure (Pa)", fontsize=25)
    axes[0].grid()
    axes[0].set_yscale('log')
    axes[0].ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
    axes[0].set_ylim(2500, 0.01)
    axes[0].set_xlim(-0.0005, 4.5e-3)
    axes[0].tick_params(axis='both', labelsize=25)

    # temp
    axes[1].plot(temperature_profile, pressure_profile, marker="o")
    axes[1].invert_yaxis()
    axes[1].set_xlabel("Temperature (K)", fontsize=25)
    axes[1].grid()
    axes[1].set_yscale('log')
    axes[1].set_ylim(2500, 0.01)
    axes[1].set_xlim(120, 220)
    axes[1].tick_params(axis='both', labelsize=25)

    # ice
    axes[2].plot(ice_profile, pressure_profile, marker="o")
    axes[2].invert_yaxis()
    axes[2].set_xlabel("Ice Opacity", fontsize=25)
    axes[2].grid()
    axes[2].set_yscale('log')
    axes[2].ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
    axes[2].set_ylim(2500, 0.01)
    axes[2].set_xlim(-0.0005, 2.5e-3)
    axes[2].tick_params(axis='both', labelsize=25)

    axes[0].xaxis.get_offset_text().set_fontsize(25) # need this because the 1e-3 was super tiny
    axes[2].xaxis.get_offset_text().set_fontsize(25)

    fig.suptitle(f"Vertical Profiles\n{start_year}-{start_month}-{start_day} to {end_year}-{end_month}-{end_day}", fontsize=30)
    plt.savefig(f"{save_location}/vertical_profiles_{start_year}-{start_month}-{start_day}to{end_year}-{end_month}-{end_day}.png")
    plt.show()