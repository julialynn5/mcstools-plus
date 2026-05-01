from mcstools_plus.data_loader import get_date_string, loading_data, reading_data, data_to_csv

def main():
    print("Note for Prof Davis: the data I have downloaded here is from 2019-12-01 to 2019-12-05. Also, it takes a while to load in the data. I recommend doing that for periods of 1 day.\n")
    start_date, start_year, start_month, start_day = get_date_string("start")
    end_date, end_year, end_month, end_day = get_date_string("end")

    level_to_eval = int(input("What level do you want to look at ('29' = 50 Pa, typical value used)?: "))

    while True:
        read_or_load = input("Type 'read' if you want to load from the PDS or 'load' for local data: ")
        if read_or_load == "read":
            # using start date because we're looking at small amounts of data for this analysis
            # otherwise this will take forever LOL
            df = reading_data(start_year, start_month, level_to_eval)
            break
    
        elif read_or_load == "load":
            df = loading_data(start_date, end_date, level_to_eval)
            break
    
        else:
            print("Please type either 'read' or 'load'")
    csv_save = input("Do you want to save this dataframe as a csv? (Y/N): ")
    if csv_save == "Y":
        print("Note for Prof Davis: I made a place for saving csv files called 'mcs_data/saved_csv_folder' for you in the github.")
        csv_file_location = input("Give me a good file location to put this in: ")
        print("Saving dataframe as csv...")
        data_to_csv(df, csv_file_location, start_year, start_month, start_day, read_or_load)

if __name__ == "__main__":
    main()