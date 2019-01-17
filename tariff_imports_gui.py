#!/usr/bin/env python

from __future__ import print_function
import sys
import os
import re
import requests
import pandas as pd
import ast
import datetime
import Tkinter as tk
import tkMessageBox

INSTRUCTIONS = '''
INSTRUCTIONS:
    
    1. Enter a space-separated list of HTS chapters or individual codes (e.g. 10 = ch10, 1 = ch10-19, 142032180).
    
        1a. Prefix chapters 1-9 with a 0 (e.g. ch1 = 01).
        1b. If you input a single-digit number, the tool will download all chapters beginning with the number 
            (e.g. 1 = chapters 10-19).
        1c. If you input a 10-digit code, the tool will only download that code.
        1d. If left blank, all available HTS codes will be downloaded.
    
    2. Click the <GO> button to begin the download process.
    
    3. Upon completion, there will be a CSV file and an XLSX file on your Desktop.
        3a. The CSV file will contain all of the data and is at the monthly-level.
        3b. The XLSX file contains the same data but will be aggregated by HTS Code and Country and is at the 
            annual-level.
        
    4. ***Please note that the data is 2018 YTD ***

    '''
API_KEY = 'INPUT YOUR API KEY HERE'
API_CALL_ROOT = 'https://api.census.gov/data/timeseries/intltrade/imports/hs?get=I_COMMODITY,I_COMMODITY_SDESC,CTY_CODE,' \
        'CTY_NAME,GEN_VAL_MO,GEN_QY1_MO,UNIT_QY1,GEN_QY2_MO,UNIT_QY2&time=2018&COMM_LVL=HS10&I_COMMODITY=%s&key=%s'

def clean_datetime():
    '''
    Trim colons and periods from datetime.datetime.now(). 
    '''
    return str(datetime.datetime.now().replace(second=0, microsecond=0)).replace(':', '').replace(' ', '_')[:-2]

def save_desktop_path(filename=None, file_type='.txt'):
    '''
    Geneartes file path to save a file to Desktop.
    Args:
        filename = Filename to save data.
        file_type = Extension to save file with.
    '''
    filepath = 'C:/Users/' + str(os.environ['USERPROFILE'].rsplit('\\',1)[-1]) + '/Desktop/'
    if filename == None:
        filename = 'default_fn_' + clean_datetime() + file_type
        print("No filename provided. Using default filename: '" + filename + "'")
        filepath += filename
    else:
        filename += '_' + clean_datetime() + file_type
        print("Saving with filename: '" + filename + "'")
        filepath += filename
    
    return filepath

def clean_content(req):
    """
    Clean the string returned by the API call and transform from string to nested list and then 
    nested list to pandas dataframe.
    Args:
        req = requests response object from .census.gov/data/timeseries/intltrade/imports/hs
    """
    cont = req.content
    cont = cont.replace('\n', '')
    cont_list = ast.literal_eval(cont)
    
    return pd.DataFrame(data=cont_list[1:], columns=cont_list[0]).drop('COMM_LVL', axis=1)

def create_df(nums):
    """
    Call API via GET request for all HTS codes/prefixes and concatenate into pandas dataframe
    Arg:
        nums = User-defined, space-separated list of HTS codes/prefixes
    """
    df = pd.DataFrame()
    for num in nums:
        while True:
            times = 0
            try:
                print('Calling data for HTS codes beginning with: {}'.format(num))
                call = (API_CALL_ROOT) % (str(num) + '*', API_KEY)
                r = requests.get(call)
            except:
                if times == 10:
                    break
                else:
                    times += 1
                    continue
            break

        print('Transforming data into table...')
        try:
            df_current = clean_content(r)
            print('Concatenating to main table...')
            df = pd.concat([df, df_current])
        except:
            print('HTS codes beginning with {} could not be processed.'.format(num))
    
    if df.shape[0] != 0:
        print('All data downloaded and concatenated into 1 table.')
    else:
        sys.exit('No data was downloaded due to an error with the HTS code(s).')
    
    return df.loc[:,~df.columns.duplicated()]

def write_csv(df):
    """
    Write dataframe to CSV
    Args:
        df = pandas dataframe
    """
    print('Writing table to CSV file...')
    df.to_csv(save_desktop_path('tariff_imports', '.csv'), index=False)
    print('Data was written to CSV file on Desktop.')

def group_data(df):
    """
    Group data by HTS code, Country, and other non-numeric fields then write to XLSX
    Args:
        df = pandas dataframe of imports data returned by API call
    """
    df = df.loc[:,~df.columns.duplicated()]
    print('Aggregating numerical values by HTS code and Country in Excel file...')
    groups = ['I_COMMODITY', 'I_COMMODITY_SDESC', 'CTY_CODE', 'CTY_NAME', 'UNIT_QY1', 'UNIT_QY2']
    sums = ['GEN_VAL_MO', 'GEN_QY1_MO', 'GEN_QY2_MO']
    df_group = df.groupby(groups)[sums].apply(lambda x : x.astype(int).sum()).reset_index().rename_axis(None, axis=1)
    df_group = df_group.loc[:,~df_group.columns.duplicated()]
    df_group.to_excel(save_desktop_path('tariff_imports_aggregate', '.xlsx'), index=False)
    print('Aggregated data was written to Excel file on Desktop.')

def tk_quit():
    if os.path.isfile(save_desktop_path('tariff_imports', '.csv')) and \
        os.path.isfile(save_desktop_path('tariff_imports_aggregate', '.xlsx')):
        tkMessageBox.showinfo('Process complete.', 'Files on Desktop.')
    else:
        tkMessageBox.showinfo('ERROR', 'Please check Desktop for files and try again if necessary.')
    root.destroy()

def go():
    print('STARTING DOWNLOAD')
    raw_nums = ''.join(entry.get('1.0', 'end-1c'))
    nums = ''.join(raw_nums.encode('utf-8')).split()
    nums = [re.sub(r'[^A-Za-z0-9]+', '', x) for x in nums]
    if len(nums) == 0:
        nums = map(str, range(10))
    df = create_df(nums)
    write_csv(df)
    group_data(df)
    tk_quit()
	
def main():
    global root
    root = tk.Tk()
    root.title('US Tariff Imports Data')
    root.geometry('600x150')
    tkMessageBox.showinfo('Tariff Imports Download', INSTRUCTIONS)
    ### BOX LABEL
    label_1 = tk.Label(root, text='Enter HTS codes here:')
    label_1.grid(row=0, column=0)
    ### TEXT BOX
    global entry
    entry = tk.Text(root, width=50, height=2)
    entry.pack()
    entry.focus_force()
    entry.grid(row=1, column=1)
    ### BUTTON
    button = tk.Button(root, text='GO', command=go)
    button.grid(row=2,column=1)
    ### MAIN LOOP
    root.mainloop()

if __name__ == '__main__':
    main()
