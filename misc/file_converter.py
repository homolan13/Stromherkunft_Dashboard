import os
import pandas as pd
from datetime import datetime, timedelta
from TextRepositories import *

# today = datetime.today() - timedelta(days=1) # real date
today = datetime(2020,1,6) # custom date

directories = {
    'export': 'Export',
    'base': 'Daten',
    'layer1': ['DE', 'FR', 'EN']
}

def make_dirs(dirs: dict):
    for l1 in dirs['layer1']:
        p = os.path.join(dirs['export'], dirs['base'], l1)
        if not os.path.exists(p):
            os.makedirs(p)


if __name__ == '__main__':

    print('\nConverting data...')

    make_dirs(directories)

    loops = 1
    if today.day < 5 or today.day == 15:
        loops += 1

    # Initialize text repositories
    De = TextRepoDE('datafile', today)
    Fr = TextRepoFR('datafile', today)
    En = TextRepoEN('datafile', today)
    text_repos = [De, Fr, En]

    # Convert data
    for _ in range(loops):
        original_file = os.path.join('generation', f'{today.year}', f'{today.year}_{today.month:02d}_generation.csv')
        data = pd.read_csv(original_file)

        imp = [flow_value if flow_value > 0 else 0 for flow_value in data['FlowValue']]
        rest = [l - n - i if l - n - i > 0 else 0 for l, n, i in zip(data['TotalLoadValue'], data['Nuclear'], imp)]
        data.insert(2, 'Other', rest)

        data.rename(columns={'TotalLoadValue': 'Load', 'FlowValue': 'Import+/Export-', 'KKM Produktion': 'Muehleberg', 'Kernkraftwerk Gösgen': 'Goesgen'}, inplace=True)
        order = ['Date', 'Time', 'Load', 'Nuclear', 'Goesgen', 'Leibstadt', 'Muehleberg', 'Beznau 1', 'Beznau 2', 'Import+/Export-', 'Other'] # drops not mentioned automatically
        data = data[order]
        data = data.round({'Other': 1, 'Import+/Export-': 1})

        for text_repo in text_repos:
            data.to_csv(os.path.join(directories['export'], directories['base'][1], text_repo.filename), index=False)

        today = today - timedelta(days=today.day)

    print('Done.')