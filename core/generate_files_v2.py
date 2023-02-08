"""
Author: Yanis Schärer, yanis.schaerer@swissnuclear.ch
As of: see README.txt
"""
import sys
import os
from datetime import datetime, timedelta
from tqdm import tqdm
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dep.FileMaker import FileMaker
from dep.to_log import to_log

directories = {
    'export': 'Export',
    'base': ['Grafiken', 'Daten'], # order: plots, data files
    'layer1': ['01_Letzte30', '02_Monate', '03_Jahre'], # order: last 30 days, months, years
    'layer2': ['DE', 'FR', 'EN'] # order is not important in this layer
}

params = {
    'fontsize': 20,
    'fontfamily': 'Segoe UI',
    'directories': directories,
    'colormap': ['#e69624', '#9fc8e0', '#e3dc00', '#7a1b1f'], # specified by corporate design
    'line': '#ba6d02',
    'text': '#915500',
    'include_outages': False,
    'color_outages': '#663c00',
    'save_plot': True
}

def get_latest_date(date_idx):
    date_length = 10 # format: 1999-01-04
    # Export/Grafiken/01_Letzte30/DE/....(yyyy-mm-dd)....
    path = os.path.join(directories['export'], directories['base'][0], directories['layer1'][0], directories['layer2'][0])
    latest_date_str = max([int(fnames[date_idx:date_idx+date_length].replace('-', '')) for fnames in os.listdir(path)], default=20220101)
    print(latest_date_str)
    y = int(str(latest_date_str)[0:4])
    m = int(str(latest_date_str)[4:6])
    d = int(str(latest_date_str)[6:8])

    return datetime(y, m, d)


def main():

    to_log(f'Started {os.path.basename(__file__)}...')

    today = datetime.today() - timedelta(days=1) # real date
    # today = datetime(2022,9,7) # custom date
    
    print(f'\n{os.path.basename(__file__)} started at: {today.year}-{today.month:02d}-{today.day:02d} {today.hour:02d}:{today.minute:02d}:{today.second:02d}')

    latest_date = get_latest_date(48) # 48 is the current index where the date starts
    difference_days = (today - latest_date).days

    for d in range(difference_days,0,-1):
        
        current_date = datetime.today() - timedelta(days=d)
        fm = FileMaker(current_date, params)

        fm.make_dirs()

        to_execute = [fm.convert_file, fm.make_last30]
        if current_date.day == 7:
            to_execute.extend([fm.make_month_series, fm.make_month_distribution])
            if current_date.month == 1:
                to_execute.extend([fm.make_year_series, fm.make_year_distribution])

        print(f'\nGenerating files... ({current_date.day:02d}.{current_date.month:02d}.{current_date.year:04d})')

        filenames = []
        for fun in tqdm(to_execute):
            to_log(f'-> Started {fun.__name__}...')
            filenames += fun()
            to_log(f'-> {fun.__name__} executed')

        print('\tGenerated files:')
        for fname in filenames:
            print(f'\t\t{fname}')

    to_log(f'Finished {os.path.basename(__file__)}')
    to_log('', no_time=True)

if __name__ == '__main__':
    main()