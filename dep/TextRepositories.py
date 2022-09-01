"""
Author: Yanis Schärer, yanis.schaerer@swissnuclear.ch
As of: see README.txt
"""
import os
from datetime import datetime, timedelta

class TextRepoDE:
    def __init__(self, figtype: str, today: datetime):
        self.figtype = figtype
        self.today = today
        self.ylabel = 'Leistung [MW]'
        self.labels_stack = ['Kernenergie', 'Wasserkraft & Andere*', 'Solar', 'Import']
        self.labels_load = 'Last'
        self.outage_annotated = 'Erzwungene Abschaltung'
        self.outage_annotations = {'Kernkraftwerk Gösgen': r'$G$: Gösgen', 'Leibstadt': r'$L$: Leibstadt', 'KKM Produktion': r'$M$: Mühleberg', 'Beznau 1': r'$B_{1/2}$: Beznau 1/2', 'Beznau 2': r'$B_{1/2}$: Beznau 1/2'}
        self.roundingerror = 'Mögliche Abweichungen resultieren aus Rundungsdifferenzen.'
        self.annotation = r'$\copyright$'+f' swissnuclear, {datetime.today().year}. Datenquelle: Entso-E\n* Wasserkraft & andere aus Entso-E Daten berechnet'
        self.month_cap = {1: 'Januar', 2: 'Februar', 3: 'März', 4: 'April', 5: 'Mai', 6: 'Juni', 7: 'Juli', 8: 'August', 9: 'September', 10: 'Oktober', 11: 'November', 12: 'Dezember'}
        self.month_low = {k: v.lower() for k,v in self.month_cap.items()}
        self.month_abbr = {1: 'Jan.', 2: 'Febr.', 3: 'März', 4: 'Apr.', 5: 'Mai', 6: 'Juni', 7: 'Juli', 8: 'Aug.', 9: 'Sept.', 10: 'Okt.', 11: 'Nov.', 12: 'Dez.'}

        match self.figtype:
            case 'last30':
                self.title = 'Stromherkunft in der Schweiz während den letzten 30 Tagen'
                if self.today.day < 30:
                    self.xlabel = f'{self.month_cap[(self.today-timedelta(days=29)).month]}/{self.month_cap[self.today.month]}'
                    if self.today.month == 1:
                        self.xlabel = self.xlabel + f' {(self.today-timedelta(days=29)).year}/{str(self.today.year)[2:]}'
                    else:
                        self.xlabel = self.xlabel + f' {self.today.year}'
                else:
                    self.xlabel = f'{self.month_cap[self.today.month]} {self.today.year}'
                self.figname = os.path.join('DE', f'swissnuclear - Stromherkunft CH letzte 30 Tage ({self.today.year}-{self.today.month:02d}-{self.today.day:02d}) - Entso-E.png')

            case 'month_series':
                self.title = f'Stromherkunft in der Schweiz im {self.month_cap[self.today.month]} {self.today.year}'
                self.figname = os.path.join('DE', f'swissnuclear - Stromherkunft CH {self.today.year}-{self.today.month:02d} Zeitreihe - Entso-E.png')

            case 'year_series':
                self.title = f'Stromherkunft in der Schweiz im Jahr {self.today.year}'
                self.figname = os.path.join('DE', f'swissnuclear - Stromherkunft CH {self.today.year} Zeitreihe - Entso-E.png')

            case 'month_distribution':
                self.title = f'Stromherkunft in der Schweiz im {self.month_cap[self.today.month]} {self.today.year}'
                self.labels_pie_small = ['Kernenergie', 'Solar', 'Wasserkraft &\nAndere*']
                self.labels_pie_large = ['Kernenergie', 'Solar', 'Wasserkraft &\nAndere*', 'Import']
                if today.year < 2020:
                    self.labels_bar = ['Gösgen', 'Leibstadt', 'Mühleberg', 'Beznau 1', 'Beznau 2']
                else:
                    self.labels_bar = ['Gösgen', 'Leibstadt', 'Beznau 1', 'Beznau 2']
                self.figname = os.path.join('DE', f'swissnuclear - Stromherkunft CH {self.today.year}-{self.today.month:02d} Verteilung - Entso-E.png')

            case 'year_distribution':
                self.title = f'Stromherkunft in der Schweiz im Jahr {self.today.year}'
                self.labels_pie_small = ['Kernenergie', 'Solar', 'Wasserkraft &\nAndere*']
                self.labels_pie_large = ['Kernenergie', 'Solar', 'Wasserkraft &\nAndere*', 'Import']
                if today.year < 2020:
                    self.labels_bar = ['Gösgen', 'Leibstadt', 'Mühleberg', 'Beznau 1', 'Beznau 2']
                else:
                    self.labels_bar = ['Gösgen', 'Leibstadt', 'Beznau 1', 'Beznau 2']
                self.figname = os.path.join('DE', f'swissnuclear - Stromherkunft CH {self.today.year} Verteilung - Entso-E.png')
                
            case 'alltime_piebar': ### not in use anymore
                self.title = [f'Monatsdurchschnitt Stromherkunft\nim {self.month_cap[m]} seit 2017' for m in range(1,13)]
                self.labels_pie_small = [f'Kernenergie', f'Andere']
                self.labels_pie_large = [f'Kernenergie', f'Andere', f'Import']
                self.labels_bar = ['Gösgen', 'Leibstadt', 'Beznau 1', 'Beznau 2', 'Mühleberg']
                self.figname = [os.path.join('DE', f'swissnuclear - Monatsdurchschnitt Stromherkunft CH {m:02d} - Entso-E.png') for m in range(1,13)]

            case 'line': ### not in use anymore
                self.title = 'Jährlicher Durchschnitt der Stromherkunft'
                self.labels_line = [f'Kernenergie', f'Import', f'Andere']
                self.figname = os.path.join('DE', 'swissnuclear - Jahresdurchschnitt Stromherkunft CH - Entso-E.png')
            
            case 'boxplot': ### not in use anymore
                self.title = f'Verteilung der Stromherkunft nach\nTechnologien seit Jan. 2017 (Stand: {datetime.today().day}. {self.month_abbr[datetime.today().month]} {datetime.today().year})'
                self.xticks = ['Kernenergie', 'Andere']
                self.figname = os.path.join('DE', 'swissnuclear - Verteilung Stromherkunft CH - Entso-E.png')

            case 'datafile':
                self.filename = os.path.join('DE', f'swissnuclear - Stromherkunft CH {today.year}-{today.month:02d} Daten - Entso-E.csv')
            
            case _:
                print('Invalid figure type.')

class TextRepoFR:
    def __init__(self, figtype: str, today: datetime):
        self.figtype = figtype
        self.today = today
        self.ylabel = 'Puissance [MW]'
        self.labels_stack = ['Nucléaire', 'Hydraulique & Autre*', 'Solaire', 'Import']
        self.labels_load = 'Charge'
        self.outage_annotated = 'Arrêt forcé'
        self.outage_annotations = {'Kernkraftwerk Gösgen': r'$G$: Gösgen', 'Leibstadt': r'$L$: Leibstadt', 'KKM Produktion': r'$M$: Mühleberg', 'Beznau 1': r'$B_{1/2}$: Beznau 1/2', 'Beznau 2': r'$B_{1/2}$: Beznau 1/2'}
        self.roundingerror = "Les écarts éventuels proviennent de différences d’arrondissement."
        self.annotation = r'$\copyright$'+f' swissnuclear, {datetime.today().year}. Source: Entso-E\n* Hydraulique & autre calculés à partir des données Entso-E'
        self.month_cap = {1: 'Janvier', 2: 'Février', 3: 'Mars', 4: 'Avril', 5: 'Mai', 6: 'Juin', 7: 'Juillet', 8: 'Août', 9: 'Septembre', 10: 'Octobre', 11: 'Novembre', 12: 'Décembre'}
        self.month_low = {k: v.lower() for k,v in self.month_cap.items()}
        self.month_abbr = {1: 'Janv.', 2: 'Févr.', 3: 'Mars', 4: 'Avr.', 5: 'Mai', 6: 'Juin', 7: 'Juill.', 8: 'Août', 9: 'Sept.', 10: 'Oct.', 11: 'Nov.', 12: 'Déc.'}

        match self.figtype:
            case 'last30':
                self.title = "Origine de l'électricité en Suisse au cours des 30 derniers jours"
                if self.today.day < 30:
                    self.xlabel = f'{self.month_cap[(self.today-timedelta(days=29)).month]}/{self.month_cap[self.today.month]}'
                    if self.today.month == 1:
                        self.xlabel = self.xlabel + f' {(self.today-timedelta(days=29)).year}/{str(self.today.year)[2:]}'
                    else:
                        self.xlabel = self.xlabel + f' {self.today.year}'
                else:
                    self.xlabel = f'{self.month_cap[self.today.month]} {self.today.year}'
                self.figname = os.path.join('FR', f'swissnuclear - Origine de lelectricite CH 30 derniers jours ({self.today.year}-{self.today.month:02d}-{self.today.day:02d}) - Entso-E.png')

            case 'month_series':
                self.title = f"Origine de l'électricité en Suisse en {self.month_low[self.today.month]} {self.today.year}"
                self.figname = os.path.join('FR', f'swissnuclear - Origine de lelectricite CH {self.today.year}-{self.today.month:02d} serie temporelle - Entso-E.png')

            case 'year_series':
                self.title = f"Origine de l'électricité en Suisse en {self.today.year}"
                self.figname = os.path.join('FR', f'swissnuclear - Origine de lelectricite CH {self.today.year} serie temporelle - Entso-E.png')

            case 'month_distribution':
                self.title = f"Origine de l'électricité en Suisse en {self.month_low[self.today.month]} {self.today.year}"
                self.labels_pie_small = ['Nucléaire', 'Solaire', 'Hydraulique &\nAutre*']
                self.labels_pie_large = ['Nucléaire', 'Solaire', 'Hydraulique &\nAutre*', 'Import']
                if today.year < 2020:
                    self.labels_bar = ['Gösgen', 'Leibstadt', 'Mühleberg', 'Beznau 1', 'Beznau 2']
                else:
                    self.labels_bar = ['Gösgen', 'Leibstadt', 'Beznau 1', 'Beznau 2']
                self.figname = os.path.join('FR', f'swissnuclear - Origine de lelectricite CH {self.today.year}-{self.today.month:02d} distribution - Entso-E.png')

            case 'year_distribution':
                self.title = f"Origine de l'électricité en Suisse en {self.today.year}"
                self.labels_pie_small = ['Nucléaire', 'Solaire', 'Hydraulique &\nAutre*']
                self.labels_pie_large = ['Nucléaire', 'Solaire', 'Hydraulique &\nAutre*', 'Import']
                if today.year < 2020:
                    self.labels_bar = ['Gösgen', 'Leibstadt', 'Mühleberg', 'Beznau 1', 'Beznau 2']
                else:
                    self.labels_bar = ['Gösgen', 'Leibstadt', 'Beznau 1', 'Beznau 2']
                self.figname = os.path.join('FR', f'swissnuclear - Origine de lelectricite CH {self.today.year} distribution - Entso-E.png')

            case 'alltime_piebar': ### not in use anymore
                self.title = [f"Moyenne mensuelle de la Origine de l'électricité\nen {self.month_low[m]} depuis 2017" for m in range(1,13)]
                self.labels_pie_small = ['Nucléaire', 'Autre']
                self.labels_pie_large = ['Nucléaire', 'Autre', 'Import']
                self.labels_bar = ['Gösgen', 'Leibstadt', 'Beznau 1', 'Beznau 2', 'Mühleberg']
                self.figname = [os.path.join('FR', f"swissnuclear - Moyenne mensuelle de la Origine de lelectricite CH {m:02d} - Entso-E.png") for m in range(1,13)]

            case 'line': ### not in use anymore
                self.title = "Moyenne annuelle de la Origine de l'électricité"
                self.labels_line = ['Nucléaire', 'Import', 'Autre']
                self.figname = os.path.join('FR', "swissnuclear - Moyenne annuelle de la Origine de lelectricite CH - Entso-E.png")
            
            case 'boxplot': ### not in use anymore
                self.title = f"Distribution de la Origine de l'électricité\npar technologie depuis janv. 2017 (situation au {datetime.today().day} {self.month_abbr[datetime.today().month]} {datetime.today().year})"
                self.xticks = ['Nucléaire', 'Autre']
                self.figname = os.path.join('FR', 'swissnuclear - Distribution de la Origine de lelectricite CH - Entso-E.png')

            case 'datafile':
                self.filename = os.path.join('FR', f'swissnuclear - Origine de lelectricite CH {today.year}-{today.month:02d} donnees - Entso-E.csv')
                
            case _:
                print('Invalid figure type.')

class TextRepoEN:
    def __init__(self, figtype: str, today: datetime):
        self.figtype = figtype
        self.today = today
        self.ylabel = 'Power [MW]'
        self.labels_stack = ['Nuclear', 'Hydro & Other*', 'Solar', 'Imports']
        self.labels_load = 'Load'
        self.outage_annotated = 'Forced outage'
        self.outage_annotations = {'Kernkraftwerk Gösgen': r'$G$: Gösgen', 'Leibstadt': r'$L$: Leibstadt', 'KKM Produktion': r'$M$: Mühleberg', 'Beznau 1': r'$B_{1/2}$: Beznau 1/2', 'Beznau 2': r'$B_{1/2}$: Beznau 1/2'}
        self.roundingerror = 'All sorts of deviations are due to rounding errors.'
        self.annotation = r'$\copyright$'+f' swissnuclear, {datetime.today().year}. Source: Entso-E\n* Hydro & other calculated from Entso-E data'
        self.month_cap = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'Mai', 6: 'June', 7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}
        self.month_low = {k: v.lower() for k,v in self.month_cap.items()}
        self.month_abbr = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'Mai', 6: 'June', 7: 'July', 8: 'Aug', 9: 'Sept', 10: 'Oct', 11: 'Nov', 12: 'Dec'}

        match self.figtype:
            case 'last30':
                self.title = 'Origin of electricity in Switzerland during the last 30 days'
                if self.today.day < 30:
                    self.xlabel = f'{self.month_cap[(self.today-timedelta(days=29)).month]}/{self.month_cap[self.today.month]}'
                    if self.today.month == 1:
                        self.xlabel = self.xlabel + f' {(self.today-timedelta(days=29)).year}/{str(self.today.year)[2:]}'
                    else:
                        self.xlabel = self.xlabel + f' {self.today.year}'
                else:
                    self.xlabel = f'{self.month_cap[self.today.month]} {self.today.year}'
                self.figname = os.path.join('EN', f'swissnuclear - Origin of electricity CH last 30 days ({self.today.year}-{self.today.month:02d}-{self.today.day:02d}) - Entso-E.png')

            case 'month_series':
                self.title = f'Origin of electricity in Switzerland in {self.month_cap[self.today.month]} {self.today.year}'
                self.figname = os.path.join('EN', f'swissnuclear - Origin of electricity CH {self.today.year}-{self.today.month:02d} time series - Entso-E.png')

            case 'year_series':
                self.title = f'Origin of electricity in Switzerland in {self.today.year}'
                self.figname = os.path.join('EN', f'swissnuclear - Origin of electricity CH {self.today.year} time series - Entso-E.png')

            case 'month_distribution':
                self.title = f'Origin of electricity in Switzerland in {self.month_cap[self.today.month]} {self.today.year}'
                self.labels_pie_small = ['Nuclear', 'Solar', 'Hydro &\nOther*']
                self.labels_pie_large = ['Nuclear', 'Solar', 'Hydro &\nOther*', 'Imports']
                if today.year < 2020:
                    self.labels_bar = ['Gösgen', 'Leibstadt', 'Mühleberg', 'Beznau 1', 'Beznau 2']
                else:
                    self.labels_bar = ['Gösgen', 'Leibstadt', 'Beznau 1', 'Beznau 2']
                self.figname = os.path.join('EN', f'swissnuclear - Origin of electricity CH {self.today.year}-{self.today.month:02d} distribution - Entso-E.png')

            case 'year_distribution':
                self.title = f'Origin of electricity in Switzerland in {self.today.year}'
                self.labels_pie_small = ['Nuclear', 'Solar', 'Hydro &\nOther*']
                self.labels_pie_large = ['Nuclear', 'Solar', 'Hydro &\nOther*', f'Imports']
                if today.year < 2020:
                    self.labels_bar = ['Gösgen', 'Leibstadt', 'Mühleberg', 'Beznau 1', 'Beznau 2']
                else:
                    self.labels_bar = ['Gösgen', 'Leibstadt', 'Beznau 1', 'Beznau 2']
                self.figname = os.path.join('EN', f'swissnuclear - Origin of electricity CH {self.today.year} distribution - Entso-E.png')
                
            case 'alltime_piebar': ### not in use anymore
                self.title = [f'Monthly average Origin of electricity\nin {self.month_cap[m]} since 2017' for m in range(1,13)]
                self.labels_pie_small = [f'Nuclear', f'Other']
                self.labels_pie_large = [f'Nuclear', f'Other', f'Imports']
                self.labels_bar = ['Gösgen', 'Leibstadt', 'Beznau 1', 'Beznau 2', 'Mühleberg']
                self.figname = [os.path.join('EN', f'swissnuclear - Monthly average Origin of electricity CH {m:02d} - Entso-E.png') for m in range(1,13)]

            case 'line': ### not in use anymore
                self.title = 'Annual average of Origin of electricity'
                self.labels_line = [f'Nuclear', f'Imports', f'Other']
                self.figname = os.path.join('EN', 'swissnuclear - Annual average Origin of electricity CH - Entso-E.png')
            
            case 'boxplot': ### not in use anymore
                self.title = f'Distribution of Origin of electricity by\ntechnology since Jan. 2017 (as of {self.month_abbr[datetime.today().month]} {datetime.today().day}, {datetime.today().year})'
                self.xticks = ['Nuclear', 'Other']
                self.figname = os.path.join('EN', 'swissnuclear - Distribution of Origin of electricity CH - Entso-E.png')

            case 'datafile':
                self.filename = os.path.join('EN', f'swissnuclear - Origin of electricity CH {today.year}-{today.month:02d} data - Entso-E.csv')
            
            case _:
                print('Invalid figure type.')