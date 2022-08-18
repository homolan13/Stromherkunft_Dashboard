import sys
import os
from datetime import datetime, timedelta
from tqdm import tqdm
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dep.FileMaker import FileMaker

# today = datetime.today() - timedelta(days=1) # real date
today = datetime(2020,1,6) # custom date

directories = {
    'export': 'Export',
    'base': ['Grafiken', 'Daten'], # order: plots, data files
    'layer1': ['01_Letzte30', '02_Monate', '03_Jahre', '04_Durchgehend'], # order: last 30 days, months, years, alltime
    'layer2': ['DE', 'FR', 'EN']
}

params = {
    'fontsize': 20,
    'fontfamily': 'Segoe UI',
    'directories': directories,
    'colormap_last30': ['#e69624', '#C8C8C8', '#7a1b1f', '#78a014'], # specified by corporate design
    'colormap_pre2020': ['#e69624', '#e69624', '#e69624', '#e69624', '#e69624', '#C8C8C8', '#7a1b1f', '#78a014'],
    'colormap_post2020': ['#e69624', '#e69624', '#e69624', '#e69624', '#C8C8C8', '#7a1b1f', '#78a014'],
    'line': '#ba6d02',
    'text': '#915500',
    'include_outages': False,
    'Planned': '#663c00', # Do not change key
    'Forced': '#210900', # Do not change key
    'save_plot': True
}

def main():
    fm = FileMaker(today, params)

    fm.make_dirs()

    to_execute = [fm.convert_file, fm.make_last30]
    if today.day == 6:
        to_execute.extend([fm.make_month_series, fm.make_month_piebar])
        if today.month == 1:
            to_execute.extend([fm.make_year_series, fm.make_year_piebar, fm.make_alltime_piebar])

    print('\nGenerating files...')

    for fun in tqdm(to_execute):
        fun()

    print('Files generated')

if __name__ == '__main__':
    main()