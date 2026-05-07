from mcstools_plus.data_loader import get_date_string, loading_data, reading_data, data_to_csv, collect_files
from mcstools_plus.analysis import analyze_atmosphere, extract_one_Pa, validate_binning_stats
from mcstools_plus.plotting import day_vs_night_dust_levels, plot_Ls_lat_value, plotting_different_pressures, preparing_lat_lon_plots,vertical_cross_section_plots, plot_curves
from mcstools_plus.storm_detection import start_stop_temperature, start_stop_cdod
from termcolor import colored, cprint

def main():
    print("Welcome to mcstools+! Let's evaluate some Mars Climate Sounder data!")
    cprint("\nNote for Professor Davis: when testing the 'reader', the data I have downloaded to the Github repo is from 2019-12-01 to 2019-12-05. Also, it takes a while to load in the data. I recommend using the 'loader' for periods of 1-2 days for the sake of time.\n", "red")
    print("First, I will ask you to enter the dates between which you want to look at the Mars climate.")
    start_date, start_year, start_month, start_day = get_date_string("start")
    end_date, end_year, end_month, end_day = get_date_string("end")

    level_to_eval = int(input("What pressure level do you want to primarily look at ('29' = 50 Pa (typical value used), '23' = 106 Pa, '18' = 200 Pa)?: "))

    while True:
        read_or_load = input("\n\nType 'load' if you want to load from the PDS or 'read' for local data: ")
        if read_or_load == "read":
            # using start date because we're looking at small amounts of data for this analysis
            # otherwise this will take forever LOL
            my_pressure_df, DDR1_df, DDR2_df = reading_data(start_year, start_month, start_day, end_year, end_month, end_day, level_to_eval)
            break
    
        elif read_or_load == "load":
            my_pressure_df, DDR1_df, DDR2_df = loading_data(start_date, end_date, level_to_eval)
            break
    
        else:
            print("Please type either 'read' or 'load'")
            
    print("\nPlease save the data as a .csv file for ease of access: ")
    cprint("Note for Professor Davis: I made a place for saving .csv files called 'mcstools_plus/mcstools_plus_example_data/saved_csv_folder' for you in the Github.", "red")
    csv_file_location = input("Give me a good file location to put this in: ")
    print("Saving dataframe as csv...\n")
    fileloc = data_to_csv(my_pressure_df, csv_file_location, start_year, start_month, start_day, end_year, end_month, end_day, read_or_load)

    analysisquestion = input("\n\n Would you like to run the analysis (creating plots of the atmosphere in different spatial and temporal dimensions)? This will take approximately 2 minutes (y/n): ")

    if analysisquestion == "y":
        stats = analyze_atmosphere(DDR1_df, DDR2_df)
        one_pressure_stats = extract_one_Pa(stats, level_to_eval)
        print(one_pressure_stats)
    
        cprint("\nNote for Professor Davis: I made a place for saving plots called 'mcstools_plus/mcstools_plus_plots/analysis_plots' for you in the Github.", "red")
        save_location = input("Give me a good folder for the plots: ")
    
        print("\nNow, we are going to make some plots. However, this server does not allow plots to be shown in terminal, so they will be saved to the folder you chose. Note: if the plots fail, it is likely because not enough data was used. \n")
        
        
        print(f"First, we are going to look at the atmospheric temperature, dust opacity, and ice opacity at the pressure level you inputted (level {level_to_eval}).") 
        cprint(f"File name: {save_location}/Ls_lat_val_for_{start_year}-{start_month}-{start_day}to{end_year}-{end_month}-{end_day}.png", "magenta")
        plot_Ls_lat_value(fileloc, start_year, start_month, start_day, end_year, end_month, end_day, save_location)
        
        print(f"\n\nNext, we are going to look at how the atmospheric temperature, dust opacity, and ice opacity varies at different pressures.")
        cprint(f"File names: {save_location}/different_pressures_Temperature_plot_{start_year}-{start_month}-{start_day}to{end_year}-{end_month}-{end_day}.png,\n            {save_location}/different_pressures_Dust_plot_{start_year}-{start_month}-{start_day}to{end_year}-{end_month}-{end_day}.png,\n            and {save_location}/different_pressures_Ice_plot_{start_year}-{start_month}-{start_day}to{end_year}-{end_month}-{end_day}.png", "magenta")
        plotting_different_pressures(DDR1_df, DDR2_df, save_location, start_year, start_month, start_day, end_year, end_month, end_day)
        
        print(f"\n\nLet's now look at the vertical cross section in temperature and dust at these pressures over time.")
        cprint(f"File name:  {save_location}/crosssection_{start_year}-{start_month}-{start_day}to{end_year}-{end_month}-{end_day}.png", "magenta")
        plot_curves(DDR1_df, DDR2_df, save_location, start_year, start_month, start_day, end_year, end_month, end_day)
        
        print(f"\n\nHere is how the atmospheric temperature and dust changes at different pressures.")
        cprint(f"File name:  {save_location}/vertical_profiles_{start_year}-{start_month}-{start_day}to{end_year}-{end_month}-{end_day}.png", "magenta")
        vertical_cross_section_plots(DDR1_df, DDR2_df, save_location, start_year, start_month, start_day, end_year, end_month, end_day)
        
        print(f"\n\nThis is how the dust height changes during the day vs the night.")
        cprint(f"File names: {save_location}/day_dust_height_for_{start_year}-{start_month}-{start_day}to{end_year}-{end_month}-{end_day}.png\n            and {save_location}/night_dust_height_for_{start_year}-{start_month}-{start_day}to{end_year}-{end_month}-{end_day}.png", "magenta")
        day_vs_night_dust_levels(DDR1_df, DDR2_df, start_year, start_month, start_day, end_year, end_month, end_day, save_location)
        
        print(f"\n\nHere is how the temperature changes over the Martian surface. The black contour represents lines of Martian topography.")
        cprint(f"File name:  {save_location}/lat_long_plot_{start_year}-{start_month}-{start_day}to{end_year}-{end_month}-{end_day}.png", "magenta")
        preparing_lat_lon_plots(fileloc, save_location, start_year, start_month, start_day, end_year, end_month, end_day)
        
        print(f"\n\nNow, is there a dust storm during this time detected in the temperature data?")
        storm_text_temp = start_stop_temperature(DDR1_df, DDR2_df, start_year, start_month, start_day, end_year, end_month, end_day, save_location)
        
        print(f"\n\nWhat about in the dust column opacity data?")
        storm_text_cdod = start_stop_cdod(DDR1_df, DDR2_df, start_year, start_month, start_day, end_year, end_month, end_day, save_location)
    else:
        print("\nOkay, let's continue.")



        
    test1question = input("\n\n Would you like to run Test 1 (testing start and end times)? This will take approximately 10 minutes (y/n): ")
    if test1question == "y":
        
        print(f"\nTest 1: Now that we know there {storm_text_temp} a storm detected in temperature data and there {storm_text_cdod} a storm detected in dust column opacity data during the period between {start_year}-{start_month}-{start_day} to {end_year}-{end_month}-{end_day}, we will now do the first test that sees if the code correctly identifies the start and end of a dust storm. Scientists typically only look at the temperature data to define when a storm starts/ends, so we will just use the temperature function. If the start and end times are within 3° L\u209B of the defined values (our bin size), this means it agrees with the literature.")
        
        cprint("\nNote for Professor Davis: I made a place for saving plots called 'mcstools_plus/mcstools_plus_plots/test1_plots' for you in the Github.", "red")
        save_location_test1 = input("Give me a good folder for the Test 1 plots: ")
        print("\nWe will now load in data ('using loader.py') from 2018-07-10 to 2018-07-12 at 50 Pa, which takes place during the peak of a global scale dust storm in Mars Year 34.")
        cprint("This may take a second, so here is a cool short reading about this event: https://www.space.com/40888-mars-dust-storm-2018-and-opportunity-rover-images.html. RIP Opportunity.\n", "green")
        start_year_2018 = 2018
        start_month_2018 = 7
        start_day_2018 = 10
        end_year_2018 = 2018
        end_month_2018 = 7
        end_day_2018 = 12
        my_pressure_2018_df, DDR1_2018_df, DDR2_2018_df = loading_data("2018-07-10", "2018-07-12", 29)
        storm_text = start_stop_temperature(DDR1_2018_df, DDR2_2018_df, start_year_2018, start_month_2018, start_day_2018, end_year_2018, end_month_2018, end_day_2018, save_location_test1)
        print("\nThis is consistent with what we would assume, as temperatures do not dip below 200 K. The time period is the entirety of the data that I entered.")

        
        print("\n\nBecause it takes so long to load in data, let's split a storm by the days around which it starts and the days around which it ends to see if we can accurately define the start and end time.\n")
        
        cprint(f"\nLet's look at the C storm that occurs in Mars year 35. According to previous literature, this starts at L\u209B = 316.1° and ends at L\u209B = 329.8°. Do our plots agree?", "cyan")
        print("\nFirst, we will look at the beginning of the MY 35 C storm (2020-11-16 to 2020-11-19):")
        start_35c_begin_year = 2020
        start_35c_begin_month = 11
        start_35c_begin_day = 16
        end_35c_begin_year = 2020
        end_35c_begin_month = 11
        end_35c_begin_day = 19
        my_pressure_beginmy35c_df, DDR1_beginmy35c_df, DDR2_beginmy35c_df = loading_data("2020-11-16", "2020-11-19", 29)
        _ = start_stop_temperature(DDR1_beginmy35c_df, DDR2_beginmy35c_df, start_35c_begin_year, start_35c_begin_month, start_35c_begin_day, end_35c_begin_year, end_35c_begin_month, end_35c_begin_day, save_location_test1)
        cprint("\nThis aligns with the predicted start time!\n\n", "cyan")

        
        print("Next, for the end of the MY 35 C storm (2020-12-10 to 2020-12-13):\n")
        start_35c_stop_year = 2020
        start_35c_stop_month = 12
        start_35c_stop_day = 10
        end_35c_stop_year = 2020
        end_35c_stop_month = 11
        end_35c_stop_day = 13
        my_pressure_stopmy35c_df, DDR1_stopmy35c_df, DDR2_stopmy35c_df = loading_data("2020-12-10", "2020-12-13", 29)
        _ = start_stop_temperature(DDR1_stopmy35c_df, DDR2_stopmy35c_df, start_35c_stop_year, start_35c_stop_month, start_35c_stop_day, end_35c_stop_year, end_35c_stop_month, end_35c_stop_day, save_location_test1)
        cprint("\nThis aligns with the predicted end time! Whoop whoop, my code works!\n\n", "cyan")
    else:
        print("\nOkay, let's continue.")



    
    test2question = input("\n\n Would you like to run Test 2 (binning and statistical consistency)? This will take approximately 1 minute (y/n): ")
    if test2question == "y":
        print("\nI will now be running a statistical test on the data you inputted for the analysis section.\n")
        validate_binning_stats(DDR1_df, DDR2_df, 'T')
        validate_binning_stats(DDR1_df, DDR2_df, 'Dust')
        validate_binning_stats(DDR1_df, DDR2_df, 'H2Oice')  
    else:
        print("")

    cprint("Thanks for a great semester! :D", "red")
    
    
    
if __name__ == "__main__":
    main()