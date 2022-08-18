import os
import pandas as pd
from tqdm import tqdm
from copy import deepcopy
from datetime import datetime, timedelta
from dep.FileHandlerLib import *

"""
    host = 'sftp-transparency.entsoe.eu'
    port = 22
    user = 'yanis.schaerer@swissnuclear.ch'
    pw = 'Swissnuclear2022!'
"""

server_details = {'host': 'sftp-transparency.entsoe.eu', 'port': 22, 'user': 'yanis.schaerer@swissnuclear.ch', 'pw': 'Swissnuclear2022!'}

custom_order_types = ['Nuclear', 'Hydro Run-of-river and poundage', 'Hydro Water Reservoir', 'Hydro Pumped Storage', 'Solar', 'Wind Onshore']
custom_order_units = ['Kernkraftwerk Gösgen', 'Leibstadt', 'Beznau 1', 'Beznau 2', 'KKM Produktion']

def date_to_str(_date: datetime):
    return f'{_date.year:04d}_{_date.month:02d}'

def main():
    today = datetime.today()
    # Check for missing files by looking for the newest one
    y = max([int(fname) for fname in os.listdir('generation')])
    m = max([int(fname[5:7]) for fname in os.listdir(os.path.join('generation',str(y)))])
    if y != today.year or m != today.month: # This means files are missing  
        today = datetime(y,m,28)
    check_last_month = True # check if last month is already there to avoid a second, unnecessary update
    while today <= datetime.today(): # while loop to update all files up to current date

        if check_last_month == True:
            if today.month == datetime.today().month:
                if today.day < 5 or today.day == 15: # update last month
                    today = today - timedelta(days=today.day)
                    print('\nUpdating last month...')

        print('\n' + 34*'-')
        print('|' + 7*' ' + f'Updating ({today.month:02d}.{today.year:04d})' + 7*' ' + '|')
        print(34*'-')

        # Download and extraction: See FileHandlerLib.py for more details
        Load = FileHandlerLoad(server_details, 'TP_export/ActualTotalLoad_6.1.A', f'{date_to_str(today)}_ActualTotalLoad_6.1.A.csv')
        Flow = FileHandlerFlow(server_details, 'TP_export/PhysicalFlows_12.1.G', f'{date_to_str(today)}_PhysicalFlows_12.1.G.csv')
        Type = FileHandlerType(server_details, 'TP_export/AggregatedGenerationPerType_16.1.B_C', f'{date_to_str(today)}_AggregatedGenerationPerType_16.1.B_C.csv')
        Unit = FileHandlerUnit(server_details, 'TP_export/ActualGenerationOutputPerGenerationUnit_16.1.A', f'{date_to_str(today)}_ActualGenerationOutputPerGenerationUnit_16.1.A.csv')
        Outages = FileHandlerOutages(server_details, 'TP_export/UnavailabilityOfGenerationUnits_15.1.A_B', f'{date_to_str(today)}_UnavailabilityOfGenerationUnits_15.1.A_B.csv')
        
        handles = [Load, Flow, Type, Unit, Outages]

        print('\nFetching files from {host}:'.format(**server_details))
        for h in tqdm(handles):
            h.get_file_from_server()
        print('\tFetched files:')
        for h in handles:
            print(f'\t\t{h.filename}')

        print('\nLoading and saving data:')
        for h in tqdm(handles):
            h.load_data()

        print('\tSaved files:')
        # Generation file
        unit_dict = {k:[] for k in custom_order_units}
        type_dict = {k:[] for k in custom_order_types}

        for _, row in Unit.data.iterrows():
            unit_dict[row['PowerSystemResourceName']].append(row['ActualGenerationOutput'])
        for _, row in Type.data.iterrows():
            type_dict[row['ProductionType']].append(row['ActualGenerationOutput'])

        data = pd.concat([Load.data, Flow.data['FlowValue'].iloc[:len(Load.data.index)]], axis=1) # concatenate Load and Flow (Flow is usually updated faster -> discard newest values to match date and time with Load)
        for p_unit in custom_order_units:
            list_to_insert = unit_dict[p_unit]+[0 for _ in range(len(data.index) - len(unit_dict[p_unit]))] # fill column with 0s (when month is not over yet)
            data.insert(4, p_unit, list_to_insert[:len(data.index)]) # slicing is important because on the current day, the length of indices and list may differ
        for p_type in custom_order_types:
            list_to_insert = type_dict[p_type]+[0 for _ in range(len(data.index) - len(type_dict[p_type]))]
            data.insert(4, p_type, list_to_insert[:len(data.index)])

        dir = os.path.join('generation', f'{today.year:04d}')
        if not os.path.exists(dir):
            os.makedirs(dir)
        filename_gen = os.path.join(dir, f'{date_to_str(today)}_generation.csv')
        data.to_csv(filename_gen, index=False)
        print(f'\t\t{filename_gen}')

        # Outages file
        filename_out = os.path.join('outages',f'{today.year:04d}_outages.csv')
        if os.path.exists(filename_out):
            data = pd.read_csv(filename_out) # delimiter should be comma
            data = pd.concat([data, Outages.data], axis=0)
            data.sort_values(['EndDate','EndTime'], inplace=True, ascending=False)
            data.drop_duplicates(subset=[col for col in list(data.columns) if col not in ['EndDate','EndTime']], inplace=True)
            data.sort_values(['StartDate','StartTime','EndDate','EndTime'], inplace=True)
        else:
            data = Outages.data

        data.to_csv(filename_out, index=False)
        print(f'\t\t{filename_out}')

        print('Removing files:')
        for h in tqdm(handles):
            h.remove_file()
        print('\tRemoved files:')
        for h in handles:
            print(f'\t\t{h.filename}')

        today_check = deepcopy(today)
        while today.month == today_check.month: # Add days until new month is reached
            today += timedelta(days=1)
        check_last_month = False # checking last month not necessary for following months

if __name__ == '__main__':
    main()