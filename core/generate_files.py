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
    'colormap': ['#e69624', '#9fc8e0', '#e3dc00', '#7a1b1f', '#78a014'], # specified by corporate design
    'line': '#ba6d02',
    'text': '#915500',
    'include_outages': True,
    'color_outages': '#663c00',
    'save_plot': True
}

def main():
    to_log(f'Started {os.path.basename(__file__)}...')

    today = datetime.today() - timedelta(days=1) # real date
    # today = datetime(2022,1,6) # custom date
    print(f'\n{os.path.basename(__file__)} started at: {today.year}-{today.month:02d}-{today.day:02d} {today.hour:02d}:{today.minute:02d}:{today.second:02d}')

    fm = FileMaker(today, params)

    fm.make_dirs()

    to_execute = [fm.convert_file, fm.make_last30]
    if today.day == 6:
        to_execute.extend([fm.make_month_series, fm.make_month_distribution])
        if today.month == 1:
            to_execute.extend([fm.make_year_series, fm.make_year_distribution])

    print('\nGenerating files...')

    for fun in tqdm(to_execute):
        fun()
        to_log(f'-> {fun.__name__} executed')

    print('Files generated')

    to_log(f'Finished {os.path.basename(__file__)}')
    to_log('', no_time=True)

if __name__ == '__main__':
    main()