import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from termcolor import colored, cprint

from mcstools_plus.data_loader import split_df_by_level
from mcstools_plus.plotting import split_df_by_time, load_in_csv_data, bin_data, build_full_df

def split_df_by_error(df, var, threshold):
    """Removing all values with error greater than threshold to improve the accuracy of our data"""
    error_search = (df[var] < threshold) 
    error_df = df.loc[error_search].copy()
    return error_df

def start_stop_temperature(DDR1, DDR2, start_year, start_month, start_day, end_year, end_month, end_day, save_location):
    """Using the temp threshold (>200 K at 50 Pa) defined by Kass et al. to determine if a dust storm occurs"""
    vmin = 120 # minimum and maximum temperatures on plot
    vmax = 250
    levels = np.linspace(vmin,vmax,56)

    df = build_full_df(DDR1, DDR2)
    level_dict = split_df_by_level(df)
    df_50Pa = level_dict[29]

    # loading in, limiting error, and using daytime data
    error_df = split_df_by_error(df_50Pa, 'T_err', 3)
    day, night = split_df_by_time(error_df)
    df = day.copy()
    heatmap, smallest_Ls, largest_Ls, L_s_bin = bin_data(df, 'T')

    plt.figure(figsize=(16, 8))
    X, Y = np.meshgrid(heatmap.columns, heatmap.index)
    X = X + 0.5 # so binning doesn't cut off any data from plot
    contourf = plt.contourf(X, Y, heatmap, levels=levels, cmap='rainbow', vmin=vmin, vmax=vmax) # colors for the full plot
    contour = plt.contour(X, Y, heatmap, colors='black', linestyles=':', levels=[200]) # putting a contour line at 200 K

    segments = contour.allsegs[0]
    valid_segments = [seg for seg in segments if seg.size > 0] # non zero segments
    if valid_segments:
        cprint(f"File name: {save_location}/dust_storm_detection_temp_{start_year}-{start_month}-{start_day}to{end_year}-{end_month}-{end_day}.png", "magenta")
        contour_coordinates = max(valid_segments, key=lambda x: x.shape[0]) # grabs the largest segment (aka the longest 200 K contour line)
        x_contour = contour_coordinates[:, 0]
        x_start = min(np.min(seg[:, 0]) for seg in valid_segments) # start is min val for segment
        x_end = max(np.max(seg[:, 0]) for seg in valid_segments) # end is max
        
        # finding the peak temperature within the contour
        masking_columns = [col for col in heatmap.columns if x_start < col < x_end] # only looks between x_start and x_end
        masked_data = heatmap[masking_columns] # applying this mask to the heatmap
        if masked_data.size == 0:
            print("A 200 K contour was found, but no data is inside the bounds.")
            storm_text = "was not enough data inputted to find"
            return storm_text
    
        maximum_temp = np.nanmax(masked_data.values) # finding the maximum temp and its index
        maximum_index = np.unravel_index(np.nanargmax(masked_data.values), masked_data.shape)
    
        x_masked, y_masked = np.meshgrid(masked_data.columns, masked_data.index)
        x_max = x_masked[maximum_index]
        print(f"Temperature analysis: There is a dust storm happening in this dataset ({start_year}-{start_month}-{start_day} to {end_year}-{end_month}-{end_day}) starting at L\u209B {round(x_start, 1)}°, peaking at L\u209B {round(x_max, 1)}°, and ending at L\u209B {round(x_end, 1)}°.")
        plt.axvline(x=x_start, color='r', linestyle='--', linewidth=2, label=f"Est. Contour Start: L\u209B = {round(x_start, 1)}°") # creating the lines and labels for the...
        plt.axvline(x=x_end, color='purple', linestyle='--', linewidth=2, label=f"Est. Contour End: L\u209B = {round(x_end, 1)}°") # start and end of the contour
        plt.axvline(x=x_max, color='green', linestyle='--', linewidth=2, label=f"Peak: {round(maximum_temp, 1)} K at L\u209B = {x_max}°") # """

        cbar = plt.colorbar(contourf)
        cbar.set_label("Temperature (K)", rotation=270, labelpad=15)

        plt.xticks(rotation=45)
        plt.yticks(ticks=[-90, -45, 0, 45, 90])
        plt.xlabel("$L_{s}$ (°)")
        plt.ylabel('Latitude (°)')
        plt.clabel(contour)
        plt.grid(color='navy', linestyle=':')
        plt.legend(loc='upper right')
        plt.title(f"Dust Storm Detection from {start_year}-{start_month}-{start_day} to {end_year}-{end_month}-{end_day}")
        plt.savefig(f"{save_location}/dust_storm_detection_temp_{start_year}-{start_month}-{start_day}to{end_year}-{end_month}-{end_day}.png")
        plt.show()
        storm_text = "was" 
    else:
        cprint(f"Temperature analysis: No dust storm happens between {start_year}-{start_month}-{start_day} and {end_year}-{end_month}-{end_day}.", "blue")
        storm_text = "was not" 
    return storm_text
    
def start_stop_cdod(DDR1, DDR2, start_year, start_month, start_day, end_year, end_month, end_day, save_location):
    """Same thing but for dust column optical depth (dust integrated from top to bottom of atmosphere)"""
    # i know i could make it the same function but it would have sooooooo many function vars
    vmin = 0
    vmax = 0.18
    levels = np.linspace(vmin,vmax,56)

    df = build_full_df(DDR1, DDR2)
    level_dict = split_df_by_level(df)
    df_50Pa = level_dict[29]

    # loading in, limiting error, and using daytime data
    error_df = split_df_by_error(df_50Pa, 'Dust_column_err', 0.1)
    day, night = split_df_by_time(error_df)
    df = day.copy()
    heatmap, smallest_Ls, largest_Ls, L_s_bin = bin_data(df, 'Dust_column')

    plt.figure(figsize=(16, 8))
    X, Y = np.meshgrid(heatmap.columns, heatmap.index)
    X = X + 0.5 # so binning doesn't cut off any data from plot
    contourf = plt.contourf(X, Y, heatmap, levels=levels, cmap='YlOrBr', vmin=vmin, vmax=vmax) # colors for the full plot
    contour = plt.contour(X, Y, heatmap, colors='black', linestyles=':', levels=[0.1]) # putting a contour line at 0.1

    segments = contour.allsegs[0]
    valid_segments = [seg for seg in segments if seg.size > 0] # non zero segments
    if valid_segments:
        cprint(f"File name: {save_location}/dust_storm_detection_cdod_{start_year}-{start_month}-{start_day}to{end_year}-{end_month}-{end_day}.png", "magenta")
        contour_coordinates = max(valid_segments, key=lambda x: x.shape[0]) # grabs the largest segment (aka the longest 200 K contour line)
        x_contour = contour_coordinates[:, 0]
        x_start = min(np.min(seg[:, 0]) for seg in valid_segments) # start is min val for segment
        x_end = max(np.max(seg[:, 0]) for seg in valid_segments) # end is max
        
        # finding the peak temperature within the contour
        masking_columns = [col for col in heatmap.columns if x_start < col < x_end] # only looks between x_start and x_end
        masked_data = heatmap[masking_columns] # applying this mask to the heatmap
        if masked_data.size == 0:
            print("A 0.1 contour was found, but no data is inside the bounds.")
            storm_text = "was not enough data inputted to find"
            return storm_text
    
        maximum_temp = np.nanmax(masked_data.values) # finding the maximum temp and its index
        maximum_index = np.unravel_index(np.nanargmax(masked_data.values), masked_data.shape)
    
        x_masked, y_masked = np.meshgrid(masked_data.columns, masked_data.index)
        x_max = x_masked[maximum_index]
        print(f"Dust opacity analysis: There is a dust storm happening in this dataset ({start_year}-{start_month}-{start_day} to {end_year}-{end_month}-{end_day}) starting at L\u209B {round(x_start, 1)}°, peaking at L\u209B {round(x_max, 1)}°, and ending at L\u209B {round(x_end)}°.")
        plt.axvline(x=x_start, color='r', linestyle='--', linewidth=2, label=f"Est. Contour Start: L\u209B = {round(x_start, 1)}°") # creating the lines and labels for the...
        plt.axvline(x=x_end, color='purple', linestyle='--', linewidth=2, label=f"Est. Contour End: L\u209B = {round(x_end, 1)}°") # start and end of the contour
        plt.axvline(x=x_max, color='green', linestyle='--', linewidth=2, label=f"Peak: {round(maximum_temp, 1)} K at L\u209B = {x_max}°") # """

        cbar = plt.colorbar(contourf)
        cbar.set_label("Dust column optical depth", rotation=270, labelpad=15)

        plt.xticks(rotation=45)
        plt.yticks(ticks=[-90, -45, 0, 45, 90])
        plt.xlabel("$L_{s}$ (°)")
        plt.ylabel('Latitude (°)')
        plt.clabel(contour)
        plt.grid(color='navy', linestyle=':')
        plt.legend(loc='upper right')
        plt.title(f"Dust Storm Detection from {start_year}-{start_month}-{start_day} to {end_year}-{end_month}-{end_day}")
        plt.savefig(f"{save_location}/dust_storm_detection_cdod_{start_year}-{start_month}-{start_day}to{end_year}-{end_month}-{end_day}.png")
        plt.show()
        storm_text = "was" 
    else:
        cprint(f"Dust opacity analysis: No dust storm happens between {start_year}-{start_month}-{start_day} and {end_year}-{end_month}-{end_day}.", "blue")
        storm_text = "was not" 
    return storm_text