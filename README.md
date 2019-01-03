# tariffs

### Overview
Download 2018 imports data from the US Census Bureau International Trade data for 2018. You will be prompted to input the HTS codes for which you want to download data. You can bypass this by hitting **Enter** to download data for all available HTS codes. The data will be downloaded to your Desktop as 2 files:
  1. The CSV file will contain all of the data at a monthly level. Depending on the number of HTS codes, this may be too large to open in Excel.
  2. The XLSX file will contain all of the data from the CSV file aggregated at a YTD annual level for each HTS code and Country.

Endpoint = https://api.census.gov/data/timeseries/intltrade/imports/hs
<br>
Place the script in your working directory and simply run with `python tariff_imports_dl_v3.py`.

### GUI
The 'tariff_imports_gui.py' script works the same as 'tariffs_imports_dl_v3.py', however, it makes use of a simple Tkinter GUI. It is a good alternative for those who do not want to use the command line.
