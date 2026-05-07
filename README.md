# mcstools+
Tools to read, process, and plot Mars Climate Sounder (MCS) data.
This is an extension of the software created by Marek Slipski
(See https://github.com/Cloudspotting-on-Mars/mcstools/tree/main/mcstools)

### Setup
Create a virtual enviroment with
```
conda create -n my_env python=3.10
conda activate my_env
```

Clone the "mcstools-plus" repository:
```
git clone https://github.com/julialynn5/mcstools-plus
```

Install dependencies:
In the directory with `pyproject.toml` and your virtual environment activated, use:
```
python -m pip install .
```

### Running program
The code can be entirely run through `main.py`, which uses command line input and brings in functions from the following files:
`data_loader.py`: Loads in MCS data using the reader() and loader() functions from mcstools. Can also export the data from a user-inputted pressure level as a .csv file.
`analysis.py`: Determines the mean, min, and max temperature, dust opacity, and water ice opacity data at the chosen pressure level. Also provides a testing function (validate_binning_stats) that determines if these values are accurate.
`plotting.py`: Creates plots of the MCS data to help analyze the Martian atmosphere.
`storm_detection.py`: Determines if a regional-scale dust storm is happening by using the criterion defined by previous literature (temperatures surpassing 200 K at 50 Pa or dust column optical depth surpassing 0.1).

To run the code, cd into the directory with `main.py` and simply type:
```
python3 main.py
```
The code will take you step by step through the process.

### Note for Prof. Davis:
Test 1 (storm detection) takes a very long time (~10 mins) to go through because it's loading many days of MCS data. I am deleting all other plots created for this project when testing, but if you don't want to sit for 10 mins, you can access the outputted plots in `mcstoolsplus/mcstools_plus/mcstools_plus_plots/test1_plots`