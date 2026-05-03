from mcstools_plus.data_loader import get_date_string, loading_data, reading_data, data_to_csv
from mcstools_plus.analysis import analyze_atmosphere, extract_one_Pa

def main():
    print("Note for Prof Davis: the data I have downloaded here is from 2019-12-01 to 2019-12-05. Also, it takes a while to load in the data. I recommend doing that for periods of 1 day.\n")
    start_date, start_year, start_month, start_day = get_date_string("start")
    end_date, end_year, end_month, end_day = get_date_string("end")

    level_to_eval = int(input("What pressure level do you want to primarily look at ('29' = 50 Pa (typical value used), '23' = 106 Pa, '18' = 200 Pa)?: "))

    while True:
        read_or_load = input("Type 'load' if you want to load from the PDS or 'read' for local data: ")
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
    print("Please save the data as a csv file for ease of use: ")
    print("Note for Prof Davis: I made a place for saving csv files called 'mcs_data/saved_csv_folder' for you in the github.")
    csv_file_location = input("Give me a good file location to put this in: ")
    print("Saving dataframe as csv...\n")
    fileloc = data_to_csv(my_pressure_df, csv_file_location, start_year, start_month, start_day, end_year, end_month, end_day, read_or_load)

    stats = analyze_atmosphere(DDR1_df, DDR2_df)
    one_pressure_stats = extract_one_Pa(stats, level_to_eval)
    print(one_pressure_stats)

    print("Note for Prof Davis: I made a place for saving plots called 'mcs_plus_plots' for you in the github.")
    plots_location = input("Give me a good folder for the plots: ")

    
if __name__ == "__main__":
    main()