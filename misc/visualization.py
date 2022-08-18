import os
from datetime import datetime, timedelta
from make_figs import *

# today = datetime.today() - timedelta(days=1) # real date
today = datetime(2020,1,6) # custom date

directories = {
    'export': 'Export',
    'base': ['Grafiken', 'Daten'],
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

def make_dirs(dirs: dict):
    for b in dir['base']:
        for l1 in dirs['layer1']:
            for l2 in dirs['layer2']:
                p = os.path.join(dirs['export'], b, l1, l2)
                if not os.path.exists(p):
                    os.makedirs(p)

if __name__ == '__main__':
    print('\nCreating graphics...')

    make_dirs(directories)

    make_last30(today, params)
    if today.day == 6:
        make_month_series(today, params)
        make_month_piebar(today, params)
        if today.month == 1:
            make_year_series(today, params)
            make_year_piebar(today, params)
            make_piebar_alltime(today, params)

    print('Done.')
