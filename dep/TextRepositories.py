"""
Author: Yanis Schärer, yanis.schaerer@swissnuclear.ch
Date of current status: see README.txt
"""
import os
from datetime import datetime, timedelta

class TextRepoDE:
    def __init__(self, figtype: str, today: datetime):
        self.figtype = figtype
        self.today = today
        self.ylabel = 'Leistung [MW]'
        self.labels_stack = ['Kernenergie CH', 'Andere', 'Import', 'Export']
        self.labels_load = 'Last'
        self.planned = 'Geplante Abschaltung'
        self.forced = 'Erzwungene Abschaltung'
        self.outage_annotations = {'Kernkraftwerk Gösgen': r'$G$: Gösgen', 'Leibstadt': r'$L$: Leibstadt', 'KKM Produktion': r'$M$: Mühleberg', 'Beznau 1': r'$B_{1/2}$: Beznau 1/2', 'Beznau 2': r'$B_{1/2}$: Beznau 1/2'}
        self.roundingerror = 'Mögliche Abweichungen resultieren aus Rundungsdifferenzen.'
        self.annotation = r'$\copyright$'+f' swissnuclear, {datetime.today().year}. Datenquelle: Entso-E'
        self.month = {1: 'Januar', 2: 'Februar', 3: 'März', 4: 'April', 5: 'Mai', 6: 'Juni', 7: 'Juli', 8: 'August', 9: 'September', 10: 'Oktober', 11: 'November', 12: 'Dezember'}
        self.month_abbr = {1: 'Jan.', 2: 'Febr.', 3: 'März', 4: 'Apr.', 5: 'Mai', 6: 'Juni', 7: 'Juli', 8: 'Aug.', 9: 'Sept.', 10: 'Okt.', 11: 'Nov.', 12: 'Dez.'}

        match self.figtype:
            case 'last30':
                self.title = 'Nettostromerzeugung in der Schweiz während den letzten 30 Tagen'
                if self.today.day < 30:
                    self.xlabel = f'{self.month[(self.today-timedelta(days=29)).month]}/{self.month[self.today.month]}'
                    if self.today.month == 1:
                        self.xlabel = self.xlabel + f' {(self.today-timedelta(days=29)).year}/{str(self.today.year)[2:]}'
                    else:
                        self.xlabel = self.xlabel + f' {self.today.year}'
                else:
                    self.xlabel = f'{self.month[self.today.month]} {self.today.year}'
                self.figname = os.path.join('DE', f'swissnuclear - Nettostromerzeugung CH letzte 30 Tage ({self.today.year}-{self.today.month:02d}-{self.today.day:02d}) - Entso-E.png')

            case 'month_series':
                self.title = f'Nettostromerzeugung in der Schweiz im {self.month[self.today.month]} {self.today.year}'
                self.figname = os.path.join('DE', f'swissnuclear - Nettostromerzeugung CH {self.today.year}-{self.today.month:02d} Zeitreihe - Entso-E.png')

            case 'year_series':
                self.title = f'Nettostromerzeugung in der Schweiz im Jahr {self.today.year}'
                self.figname = os.path.join('DE', f'swissnuclear - Nettostromerzeugung CH {self.today.year} Zeitreihe - Entso-E.png')

            case 'month_distribution':
                self.title = f'Nettostromerzeugung in der Schweiz im {self.month[self.today.month]} {self.today.year}'
                self.labels_pie_small = [f'Kernenergie CH', f'Andere']
                self.labels_pie_large = [f'Kernenergie CH', f'Andere', f'Import']
                if today.year < 2020:
                    self.labels_bar = ['Gösgen', 'Leibstadt', 'Beznau 1', 'Beznau 2', 'Mühleberg']
                else:
                    self.labels_bar = ['Gösgen', 'Leibstadt', 'Beznau 1', 'Beznau 2']
                self.figname = os.path.join('DE', f'swissnuclear - Nettostromerzeugung CH {self.today.year}-{self.today.month:02d} Verteilung - Entso-E.png')

            case 'year_distribution':
                self.title = f'Nettostromerzeugung in der Schweiz im Jahr {self.today.year}'
                self.labels_pie_small = [f'Kernenergie CH', f'Andere']
                self.labels_pie_large = [f'Kernenergie CH', f'Andere', f'Import']
                if today.year < 2020:
                    self.labels_bar = ['Gösgen', 'Leibstadt', 'Beznau 1', 'Beznau 2', 'Mühleberg']
                else:
                    self.labels_bar = ['Gösgen', 'Leibstadt', 'Beznau 1', 'Beznau 2']
                self.figname = os.path.join('DE', f'swissnuclear - Nettostromerzeugung CH {self.today.year} Verteilung - Entso-E.png')
                
            case 'alltime_piebar':
                self.title = [f'Monatsdurchschnitt Nettostromerzeugung\nim {self.month[m]} seit 2017' for m in range(1,13)]
                self.labels_pie_small = [f'Kernenergie CH', f'Andere']
                self.labels_pie_large = [f'Kernenergie CH', f'Andere', f'Import']
                self.labels_bar = ['Gösgen', 'Leibstadt', 'Beznau 1', 'Beznau 2', 'Mühleberg']
                self.figname = [os.path.join('DE', f'swissnuclear - Monatsdurchschnitt Nettostromerzeugung CH {m:02d} - Entso-E.png') for m in range(1,13)]

            case 'line': ### not in use anymore
                self.title = 'Jährlicher Durchschnitt der Nettostromerzeugung'
                self.labels_line = [f'Kernenergie CH', f'Import', f'Andere']
                self.figname = os.path.join('DE', 'swissnuclear - Jahresdurchschnitt Nettostromerzeugung CH - Entso-E.png')
            
            case 'boxplot': ### not in use anymore
                self.title = f'Verteilung der Nettostromerzeugung nach\nTechnologien seit Jan. 2017 (Stand: {datetime.today().day}. {self.month_abbr[datetime.today().month]} {datetime.today().year})'
                self.xticks = ['Kernenergie CH', 'Andere']
                self.figname = os.path.join('DE', 'swissnuclear - Verteilung Nettostromerzeugung CH - Entso-E.png')

            case 'datafile':
                self.filename = os.path.join('DE', f'swissnuclear - Nettostromerzeugung CH {today.year}-{today.month:02d} Daten - Entso-E.csv')
            
            case _:
                print('Invalid figure type.')

class TextRepoFR:
    def __init__(self, figtype: str, today: datetime):
        self.figtype = figtype
        self.today = today
        self.ylabel = 'Puissance [MW]'
        self.labels_stack = ['Énergie nucléaire CH', 'Autre', 'Importation', 'Exportation']
        self.labels_load = 'Charge'
        self.planned = 'Arrêt planifié'
        self.forced = 'Arrêt forcé'
        self.outage_annotations = {'Kernkraftwerk Gösgen': r'$G$: Gösgen', 'Leibstadt': r'$L$: Leibstadt', 'KKM Produktion': r'$M$: Mühleberg', 'Beznau 1': r'$B_{1/2}$: Beznau 1/2', 'Beznau 2': r'$B_{1/2}$: Beznau 1/2'}
        self.roundingerror = "Les écarts éventuels résultent de différences d'arrondi."
        self.annotation = r'$\copyright$'+f' swissnuclear, {datetime.today().year}. Source: Entso-E'
        self.month = {1: 'Janvier', 2: 'Février', 3: 'Mars', 4: 'Avril', 5: 'Mai', 6: 'Juin', 7: 'Juillet', 8: 'Août', 9: 'Septembre', 10: 'Octobre', 11: 'Novembre', 12: 'Décembre'}
        self.month_abbr = {1: 'Janv.', 2: 'Févr.', 3: 'Mars', 4: 'Avr.', 5: 'Mai', 6: 'Juin', 7: 'Juill.', 8: 'Août', 9: 'Sept.', 10: 'Oct.', 11: 'Nov.', 12: 'Déc.'}

        match self.figtype:
            case 'last30':
                self.title = "Production nette d'électricité en Suisse au cours des 30 derniers jours"
                if self.today.day < 30:
                    self.xlabel = f'{self.month[(self.today-timedelta(days=29)).month]}/{self.month[self.today.month]}'
                    if self.today.month == 1:
                        self.xlabel = self.xlabel + f' {(self.today-timedelta(days=29)).year}/{str(self.today.year)[2:]}'
                    else:
                        self.xlabel = self.xlabel + f' {self.today.year}'
                else:
                    self.xlabel = f'{self.month[self.today.month]} {self.today.year}'
                self.figname = os.path.join('FR', f'swissnuclear - Production nette delectricite CH 30 derniers jours ({self.today.year}-{self.today.month:02d}-{self.today.day:02d}) - Entso-E.png')

            case 'month_series':
                self.title = f"Production nette d'électricité en Suisse en {self.month[self.today.month]} {self.today.year}"
                self.figname = os.path.join('FR', f'swissnuclear - Production nette delectricite CH {self.today.year}-{self.today.month:02d} serie temporelle - Entso-E.png')

            case 'year_series':
                self.title = f"Production nette d'électricité en Suisse en {self.today.year}"
                self.figname = os.path.join('FR', f'swissnuclear - Production nette delectricite CH {self.today.year} serie temporelle - Entso-E.png')

            case 'month_distribution':
                self.title = f"Production nette d'électricité en Suisse en {self.month[self.today.month]} {self.today.year}"
                self.labels_pie_small = ['Énergie nucléaire CH', 'Autre']
                self.labels_pie_large = ['Énergie nucléaire CH', 'Autre', 'Importation']
                if today.year < 2020:
                    self.labels_bar = ['Gösgen', 'Leibstadt', 'Beznau 1', 'Beznau 2', 'Mühleberg']
                else:
                    self.labels_bar = ['Gösgen', 'Leibstadt', 'Beznau 1', 'Beznau 2']
                self.figname = os.path.join('FR', f'swissnuclear - Production nette delectricite CH {self.today.year}-{self.today.month:02d} distribution - Entso-E.png')

            case 'year_distribution':
                self.title = f"Production nette d'électricité en Suisse en {self.today.year}"
                self.labels_pie_small = ['Énergie nucléaire CH', 'Autre']
                self.labels_pie_large = ['Énergie nucléaire CH', 'Autre', 'Importation']
                if today.year < 2020:
                    self.labels_bar = ['Gösgen', 'Leibstadt', 'Beznau 1', 'Beznau 2', 'Mühleberg']
                else:
                    self.labels_bar = ['Gösgen', 'Leibstadt', 'Beznau 1', 'Beznau 2']
                self.figname = os.path.join('FR', f'swissnuclear - Production nette delectricite CH {self.today.year} distribution - Entso-E.png')

            case 'alltime_piebar':
                self.title = [f"Moyenne mensuelle de la production nette d'électricité\nen {self.month[m]} depuis 2017" for m in range(1,13)]
                self.labels_pie_small = ['Énergie nucléaire CH', 'Autre']
                self.labels_pie_large = ['Énergie nucléaire CH', 'Autre', 'Importation']
                self.labels_bar = ['Gösgen', 'Leibstadt', 'Beznau 1', 'Beznau 2', 'Mühleberg']
                self.figname = [os.path.join('FR', f"swissnuclear - Moyenne mensuelle de la production nette delectricite CH {m:02d} - Entso-E.png") for m in range(1,13)]

            case 'line': ### not in use anymore
                self.title = "Moyenne annuelle de la production nette d'électricité"
                self.labels_line = ['Énergie nucléaire CH', 'Importation', 'Autre']
                self.figname = os.path.join('FR', "swissnuclear - Moyenne annuelle de la production nette delectricite CH - Entso-E.png")
            
            case 'boxplot': ### not in use anymore
                self.title = f"Distribution de la production nette d'électricité\npar technologie depuis janv. 2017 (situation au {datetime.today().day} {self.month_abbr[datetime.today().month]} {datetime.today().year})"
                self.xticks = ['Énergie nucléaire CH', 'Autre']
                self.figname = os.path.join('FR', 'swissnuclear - Distribution de la production nette delectricite CH - Entso-E.png')

            case 'datafile':
                self.filename = os.path.join('FR', f'swissnuclear - Production nette delectricite CH {today.year}-{today.month:02d} donnees - Entso-E.csv')
                
            case _:
                print('Invalid figure type.')

class TextRepoEN:
    def __init__(self, figtype: str, today: datetime):
        self.figtype = figtype
        self.today = today
        self.ylabel = 'Power [MW]'
        self.labels_stack = ['Nuclear energy CH', 'Other', 'Import', 'Export']
        self.labels_load = 'Load'
        self.planned = 'Planned outage'
        self.forced = 'Forced outage'
        self.outage_annotations = {'Kernkraftwerk Gösgen': r'$G$: Gösgen', 'Leibstadt': r'$L$: Leibstadt', 'KKM Produktion': r'$M$: Mühleberg', 'Beznau 1': r'$B_{1/2}$: Beznau 1/2', 'Beznau 2': r'$B_{1/2}$: Beznau 1/2'}
        self.roundingerror = 'All sorts of deviations are due to rounding errors.'
        self.annotation = r'$\copyright$'+f' swissnuclear, {datetime.today().year}. Source: Entso-E'
        self.month = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'Mai', 6: 'June', 7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}
        self.month_abbr = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'Mai', 6: 'June', 7: 'July', 8: 'Aug', 9: 'Sept', 10: 'Oct', 11: 'Nov', 12: 'Dec'}

        match self.figtype:
            case 'last30':
                self.title = 'Net electricity generation in Switzerland during the last 30 days'
                if self.today.day < 30:
                    self.xlabel = f'{self.month[(self.today-timedelta(days=29)).month]}/{self.month[self.today.month]}'
                    if self.today.month == 1:
                        self.xlabel = self.xlabel + f' {(self.today-timedelta(days=29)).year}/{str(self.today.year)[2:]}'
                    else:
                        self.xlabel = self.xlabel + f' {self.today.year}'
                else:
                    self.xlabel = f'{self.month[self.today.month]} {self.today.year}'
                self.figname = os.path.join('EN', f'swissnuclear - Net electricity production CH last 30 days ({self.today.year}-{self.today.month:02d}-{self.today.day:02d}) - Entso-E.png')

            case 'month_series':
                self.title = f'Net electricity generation in Switzerland in {self.month[self.today.month]} {self.today.year}'
                self.figname = os.path.join('EN', f'swissnuclear - Net electricity production CH {self.today.year}-{self.today.month:02d} time series - Entso-E.png')

            case 'year_series':
                self.title = f'Net electricity generation in Switzerland in {self.today.year}'
                self.figname = os.path.join('EN', f'swissnuclear - Net electricity production CH {self.today.year} time series - Entso-E.png')

            case 'month_distribution':
                self.title = f'Net electricity generation in Switzerland in {self.month[self.today.month]} {self.today.year}'
                self.labels_pie_small = [f'Nuclear energy CH', f'Other']
                self.labels_pie_large = [f'Nuclear energy CH', f'Other', f'Import']
                if today.year < 2020:
                    self.labels_bar = ['Gösgen', 'Leibstadt', 'Beznau 1', 'Beznau 2', 'Mühleberg']
                else:
                    self.labels_bar = ['Gösgen', 'Leibstadt', 'Beznau 1', 'Beznau 2']
                self.figname = os.path.join('EN', f'swissnuclear - Net electricity production CH {self.today.year}-{self.today.month:02d} distribution - Entso-E.png')

            case 'year_distribution':
                self.title = f'Net electricity generation in Switzerland in {self.today.year}'
                self.labels_pie_small = [f'Nuclear energy CH', f'Other']
                self.labels_pie_large = [f'Nuclear energy CH', f'Other', f'Import']
                if today.year < 2020:
                    self.labels_bar = ['Gösgen', 'Leibstadt', 'Beznau 1', 'Beznau 2', 'Mühleberg']
                else:
                    self.labels_bar = ['Gösgen', 'Leibstadt', 'Beznau 1', 'Beznau 2']
                self.figname = os.path.join('EN', f'swissnuclear - Net electricity production CH {self.today.year} distribution - Entso-E.png')
                
            case 'alltime_piebar':
                self.title = [f'Monthly average net electricity generation\nin {self.month[m]} since 2017' for m in range(1,13)]
                self.labels_pie_small = [f'Nuclear energy CH', f'Other']
                self.labels_pie_large = [f'Nuclear energy CH', f'Other', f'Import']
                self.labels_bar = ['Gösgen', 'Leibstadt', 'Beznau 1', 'Beznau 2', 'Mühleberg']
                self.figname = [os.path.join('EN', f'swissnuclear - Monthly average net electricity generation CH {m:02d} - Entso-E.png') for m in range(1,13)]

            case 'line': ### not in use anymore
                self.title = 'Annual average of net electricity generation'
                self.labels_line = [f'Nuclear energy CH', f'Import', f'Other']
                self.figname = os.path.join('EN', 'swissnuclear - Annual average net electricity generation CH - Entso-E.png')
            
            case 'boxplot': ### not in use anymore
                self.title = f'Distribution of net electricity generation by\ntechnology since Jan. 2017 (as of {self.month_abbr[datetime.today().month]} {datetime.today().day}, {datetime.today().year})'
                self.xticks = ['Nuclear energy CH', 'Other']
                self.figname = os.path.join('EN', 'swissnuclear - Distribution of net electricity generation CH - Entso-E.png')

            case 'datafile':
                self.filename = os.path.join('EN', f'swissnuclear - Net electircity production CH {today.year}-{today.month:02d} data - Entso-E.csv')
            
            case _:
                print('Invalid figure type.')