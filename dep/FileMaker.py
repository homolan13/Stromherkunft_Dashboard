import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import ConnectionPatch
from datetime import datetime, timedelta
from dep.TextRepositories import *

class FileMaker:
    def __init__(self, today: datetime, params: dict):
        self.today = today
        self.params = params

    def _get_outages(self, data: pd.DataFrame):
        return_list = [] # one entry: (x, y, marker, color)
        units = ['Kernkraftwerk Gösgen', 'Leibstadt', 'KKM Produktion', 'Beznau 1', 'Beznau 2']
        marker_type = {k:v for k,v in zip(units,['$G$', '$L$', '$M$', '$B_1$', '$B_2$'])}
        history = {k:[] for k in units} # values are of type ('planned/forced', idx)

        outages = pd.read_csv(os.path.join('core', 'outages',f'{self.today.year}_outages.csv'))
        for _, outage in outages.iterrows():
            x1 = outage['StartDate']
            x2 = outage['StartTime'][:2]
            start_day = data[data['Date'] == x1]
            if start_day.empty: # start of outage is not in plot limits
                continue
            start_idx = start_day[start_day['Time'].str[:2] == x2].index[0]
            if start_idx == 0: # no new marker at start for outages of last month/year
                continue
            if start_idx in history[outage['UnitName']]: # outage is already captured
                continue
            history[outage['UnitName']] = history[outage['UnitName']] + [start_idx+k for k in range(5*24)] # update captured outages
            
            idx = units.index(outage['UnitName'])
            return_list.append((start_idx, np.sum(np.array([data[units[unit]][start_idx] for unit in range(idx+1)]), axis=0), marker_type[outage['UnitName']], self.self.params[outage['Type']]))

        return return_list

    def make_dirs(self):
        dirs = self.params['directories']
        for l1 in dirs['layer1']:
            for l2 in dirs['layer2']:
                p = os.path.join(dirs['export'], dirs['base'][0], l1, l2)
                if not os.path.exists(p):
                    os.makedirs(p)
        for l2 in dirs['layer2']:
            p = os.path.join(dirs['export'], dirs['base'][1], l2)
            if not os.path.exists(p):
                os.makedirs(p)

    def make_last30(self):
        today = self.today

        plt.rcParams['font.size'] = self.params['fontsize']
        plt.rcParams['font.family'] = self.params['fontfamily']
        d = self.params['directories']

        if self.params['save_plot']:
            path = os.path.join(d['export'], d['base'][0], d['layer1'][0])
            for dir in os.listdir(path):
                for f in os.listdir(os.path.join(path, dir)):
                    os.remove(os.path.join(path, dir, f))

        ### Initialize text repository
        De = TextRepoDE('last30', today)
        Fr = TextRepoFR('last30', today)
        En = TextRepoEN('last30', today)
        text_repos = [De, Fr, En]

        ### Prepare data
        last_30 = [today - timedelta(days=i) for i in range(30)]
        last_30_my = set([(day.year, day.month) for day in last_30])
        last_30_str = [f'{day.year}-{day.month:02d}-{day.day:02d}' for day in last_30]

        data = []
        for my in last_30_my:
            fname = os.path.join('core','generation',f'{my[0]}',f'{my[0]}_{my[1]:02d}_generation.csv')
            f_data = pd.read_csv(fname)
            data.extend([f_data[f_data['Date'].str.contains(date_str)] for date_str in last_30_str])
        data = pd.concat(data, axis=0)
        data.sort_values(['Date','Time'], inplace=True)
        data.reset_index(drop=True, inplace=True)
        data.insert(3, 'Export', pd.NA)
        data.insert(3, 'Import', pd.NA)
        data['Import'] = [flow_value if flow_value > 0 else 0 for flow_value in data['FlowValue']]
        data['Export'] = [-flow_value if flow_value < 0 else 0 for flow_value in data['FlowValue']]
        data.drop(columns='FlowValue', inplace=True)

        rest = [load - nuc - imp if load - nuc - imp > 0 else 0 for load, nuc, imp in zip(data['TotalLoadValue'], data['Nuclear'], data['Import'])]
        ticks = [f'{d[-3:-1]}.{d[5:7]}.' for d in data['Date']]

        y = np.array([data['Nuclear'], rest, data['Import'], data['Export']])
        stack_max = max(np.sum(y, axis=0))

        ### Create figures
        logo = plt.imread(os.path.join('res', 'swissnuclear logo.png'))
        for text_repo in text_repos:
            fig = plt.figure(figsize=(20,10), dpi=300)
            ax = plt.gca()

            plt.stackplot(range(0,len(data.index)), y, colors=self.params['colormap_last30'], labels=text_repo.labels_stack, zorder=10)
            plt.plot(data['TotalLoadValue'], color='k', linewidth=2, label=text_repo.labels_load, zorder=20)

            plt.title(text_repo.title, fontsize=34)

            plt.xticks([i for i in range(len(data.index)) if i%24 == 0], [int(tick[:2]) for tick in ticks[::24]], ha='left')
            plt.xlim(0,len(data.index)-1)
            plt.xlabel(text_repo.xlabel)

            plt.yticks(range(0, int(1.2*stack_max), 2500))
            plt.ylim(0, min(1.2*stack_max, 20000))
            plt.ylabel(text_repo.ylabel)

            plt.grid(axis='y', alpha=0.4, zorder=0)
            plt.box(on=False)
            ax.tick_params(axis='y', length=0, pad=15)
            ax.tick_params(axis='x', direction='in', length=0, color='dimgrey', pad=15)

            plt.legend(loc=9, bbox_to_anchor=(0.5,0.99), ncol=5, frameon=False, columnspacing=3).set_zorder(35)

            plt.annotate(text_repo.annotation, xycoords='figure fraction', xy=(0.70,0.03), fontsize=10)

            imgax = fig.add_axes([0.8, 0.94, 0.1, 0.1], anchor='SE')
            imgax.imshow(logo)
            imgax.axis('off')


            if self.params['save_plot']:
                fname = os.path.join(path, text_repo.figname)
                fig.savefig(fname, dpi='figure', bbox_inches='tight', metadata={'Copyright':f'Swissnuclear, {today.year}', 'Author':'Yanis S.', 'Disclaimer':'Only allowed for private use. Contact Swissnuclear for more information.'})
            plt.close()

    def make_month_series(self):
        today = self.today - timedelta(days=28)

        plt.rcParams['font.size'] = self.params['fontsize']
        plt.rcParams['font.family'] = self.params['fontfamily']
        d = self.params['directories']
        path = os.path.join(d['export'], d['base'][0], d['layer1'][1])

        ### Initialize text repository
        De = TextRepoDE('month_series', today)
        Fr = TextRepoFR('month_series', today)
        En = TextRepoEN('month_series', today)
        text_repos = [De, Fr, En]
        
        ### Prepare data
        month = today.month
        year = today.year
        f = os.path.join('core','generation',str(year),f'{year}_{month:02d}_generation.csv')
        data = pd.read_csv(f)
        data.insert(3, 'Export', pd.NA)
        data.insert(3, 'Import', pd.NA)
        data['Import'] = [flow_value if flow_value > 0 else 0 for flow_value in data['FlowValue']]
        data['Export'] = [-flow_value if flow_value < 0 else 0 for flow_value in data['FlowValue']]
        data.drop(columns='FlowValue', inplace=True)

        rest = [load - nuc - imp if load - nuc - imp > 0 else 0 for load, nuc, imp in zip(data['TotalLoadValue'], data['Nuclear'], data['Import'])]
        ticks = [f'{d[-3:-1]}.{d[5:7]}.' for d in data['Date']]

        ### Create figures
        logo = plt.imread(os.path.join('res', 'swissnuclear logo.png'))
        for text_repo in text_repos:
            fig = plt.figure(figsize=(20,10), dpi=300)
            ax = plt.gca()

            if year < 2020: # include KKM
                stacked_data = [data['Kernkraftwerk Gösgen'], data['Kernkraftwerk Gösgen']+data['Leibstadt'], data['Kernkraftwerk Gösgen']+data['Leibstadt']+data['KKM Produktion'], data['Kernkraftwerk Gösgen']+data['Leibstadt']+data['KKM Produktion']+data['Beznau 1'], data['Kernkraftwerk Gösgen']+data['Leibstadt']+data['KKM Produktion']+data['Beznau 1']+data['Beznau 2']]
                y = np.array([data['Kernkraftwerk Gösgen'], data['Leibstadt'], data['KKM Produktion'], data['Beznau 1'], data['Beznau 2'], rest, data['Import'], data['Export']])
                plt.stackplot(range(0,len(data.index)), y, colors=self.params['colormap_pre2020'], labels=[None, None, None, None]+text_repo.labels_stack, zorder=10)
                plt.plot(range(0,len(data.index)), stacked_data[0], self.params['line'], lw=0.5, zorder=11)
                plt.plot(range(0,len(data.index)), stacked_data[1], self.params['line'], lw=0.5, zorder=11)
                plt.plot(range(0,len(data.index)), stacked_data[2], self.params['line'], lw=0.5, zorder=11)
                plt.plot(range(0,len(data.index)), stacked_data[3], self.params['line'], lw=0.5, zorder=11)
                plt.plot(range(0,len(data.index)), stacked_data[4], self.params['line'], lw=0.5, zorder=11)
                plt.annotate('Gösgen',    (len(data.index)-160, stacked_data[0].iloc[len(data.index)-160]+100), color=self.params['text'], fontsize=14, rotation=45, zorder=12)
                plt.annotate('Leibstadt', (len(data.index)-130, stacked_data[1].iloc[len(data.index)-130]+100), color=self.params['text'], fontsize=14, rotation=45, zorder=12)
                plt.annotate('Mühleberg', (len(data.index)-100, stacked_data[2].iloc[len(data.index)-100]+100), color=self.params['text'], fontsize=14, rotation=45, zorder=12)
                plt.annotate('Beznau 1',  (len(data.index)-70,  stacked_data[3].iloc[len(data.index)-70]+100),  color=self.params['text'],  fontsize=14, rotation=45, zorder=12)
                plt.annotate('Beznau 2',  (len(data.index)-40,  stacked_data[4].iloc[len(data.index)-40]+100),  color=self.params['text'], fontsize=14, rotation=45, zorder=12)
            else: # exclude KKM
                stacked_data = [data['Kernkraftwerk Gösgen'], data['Kernkraftwerk Gösgen']+data['Leibstadt'], data['Kernkraftwerk Gösgen']+data['Leibstadt']+data['Beznau 1'], data['Kernkraftwerk Gösgen']+data['Leibstadt']+data['Beznau 1']+data['Beznau 2']]
                y = np.array([data['Kernkraftwerk Gösgen'], data['Leibstadt'], data['Beznau 1'], data['Beznau 2'], rest, data['Import'], data['Export']])
                plt.stackplot(range(0,len(data.index)), y, colors=self.params['colormap_post2020'], labels=[None, None, None]+text_repo.labels_stack, zorder=10)
                plt.plot(range(0,len(data.index)), stacked_data[0], self.params['line'], lw=0.5, zorder=11)
                plt.plot(range(0,len(data.index)), stacked_data[1], self.params['line'], lw=0.5, zorder=11)
                plt.plot(range(0,len(data.index)), stacked_data[2], self.params['line'], lw=0.5, zorder=11)
                plt.plot(range(0,len(data.index)), stacked_data[3], self.params['line'], lw=0.5, zorder=11)
                plt.annotate('Gösgen',    (len(data.index)-130, stacked_data[0].iloc[len(data.index)-130]+100), color=self.params['text'], fontsize=14, rotation=45, zorder=12)
                plt.annotate('Leibstadt', (len(data.index)-100, stacked_data[1].iloc[len(data.index)-100]+100), color=self.params['text'], fontsize=14, rotation=45, zorder=12)
                plt.annotate('Beznau 1',  (len(data.index)-70,  stacked_data[2].iloc[len(data.index)-70]+100),  color=self.params['text'],  fontsize=14, rotation=45, zorder=12)
                plt.annotate('Beznau 2',  (len(data.index)-40,  stacked_data[3].iloc[len(data.index)-40]+100),  color=self.params['text'], fontsize=14, rotation=45, zorder=12)
            stack_max = max(np.sum(y, axis=0))

            plt.plot(data['TotalLoadValue'], color='k', linewidth=2, label=text_repo.labels_load, zorder=20)

            if self.params['include_outages']:
                outages = self._get_outages(data)
                planned, forced = False, False
                if outages:
                    if today.year < 2020:
                        plt.annotate(text_repo.unit_annotation_pre2020, xycoords='figure fraction', xy=(0.07,0.03), fontsize=10)
                    else:
                        plt.annotate(text_repo.unit_annotation_post2020, xycoords='figure fraction', xy=(0.07,0.03), fontsize=10)
                    for outage in outages:
                        plt.scatter(outage[0], outage[1], marker=outage[2], s=120, c=outage[3], clip_on=False, zorder=20)
                        if not planned:
                            if outage[3] == self.params['Planned']:
                                plt.annotate(text_repo.planned, (outage[0]-4, outage[1]+500), color=self.params['Planned'], fontsize=14, rotation=90, zorder=25, bbox={'edgecolor': 'w', 'linewidth': 0, 'facecolor': 'w', 'alpha': 0.4, 'boxstyle': 'round'})
                                planned = True
                        if not forced:
                            if outage[3] == self.params['Forced']:                
                                plt.annotate(text_repo.forced, (outage[0]-4, outage[1]+500), color=self.params['Forced'], fontsize=14, rotation=90, zorder=25, bbox={'edgecolor': 'w', 'linewidth': 0, 'facecolor': 'w', 'alpha': 0.4, 'boxstyle': 'round'})
                                forced = True
                    
                    

            plt.title(text_repo.title, fontsize=34)

            plt.xticks([i for i in range(len(data.index)) if i%24 == 0], [int(tick[:2]) for tick in ticks[::24]], ha='left')
            plt.xlim(0,len(data.index)-1)

            plt.yticks(range(0, int(1.2*stack_max), 2500))
            plt.ylim(0, min(1.2*stack_max, 20000))
            plt.ylabel(text_repo.ylabel)

            plt.grid(axis='y', alpha=0.4, zorder=0)
            plt.box(on=False)
            ax.tick_params(axis='y', length=0, pad=15)
            ax.tick_params(axis='x', direction='in', length=0, color='dimgrey', pad=15)

            plt.legend(loc=9, bbox_to_anchor=(0.5,0.99), ncol=5, frameon=False, columnspacing=3).set_zorder(35)          

            plt.annotate(text_repo.annotation, xycoords='figure fraction', xy=(0.70,0.03), fontsize=10)

            imgax = fig.add_axes([0.8, 0.94, 0.1, 0.1], anchor='SE')
            imgax.imshow(logo)
            imgax.axis('off')

            if self.params['save_plot']:
                fname = os.path.join(path, text_repo.figname)
                fig.savefig(fname, dpi='figure', bbox_inches='tight', metadata={'Copyright':f'Swissnuclear, {today.year}', 'Author':'Yanis S.', 'Disclaimer':'Only allowed for private use. Contact Swissnuclear for more information.'})
            plt.close()

    def make_year_series(self):
        today = self.today - timedelta(days=365)

        plt.rcParams['font.size'] = self.params['fontsize']
        plt.rcParams['font.family'] = self.params['fontfamily']
        d = self.params['directories']
        path = os.path.join(d['export'], d['base'][0], d['layer1'][2])

        ### Initialize text repository
        De = TextRepoDE('year_series', today)
        Fr = TextRepoFR('year_series', today)
        En = TextRepoEN('year_series', today)
        text_repos = [De, Fr, En]
        
        ### Prepare data
        data_list = []
        year = today.year
        path_gen = os.path.join('core','generation', str(year))
        for f in os.listdir(path_gen):
            data_list.append(pd.read_csv(os.path.join(path_gen, f)))
        data = pd.concat(data_list, axis=0)
        data.reset_index(drop=True, inplace=True)
        data.insert(3, 'Export', pd.NA)
        data.insert(3, 'Import', pd.NA)
        data['Import'] = [flow_value if flow_value > 0 else 0 for flow_value in data['FlowValue']]
        data['Export'] = [-flow_value if flow_value < 0 else 0 for flow_value in data['FlowValue']]
        data.drop(columns='FlowValue', inplace=True)

        rest = [load - nuc - imp if load - nuc - imp > 0 else 0 for load, nuc, imp in zip(data['TotalLoadValue'], data['Nuclear'], data['Import'])]
        ticks = [f'{d[-3:-1]}.{d[5:7]}.' for d in data['Date']]

        ### Create figures
        logo = plt.imread(os.path.join('res', 'swissnuclear logo.png'))
        for text_repo in text_repos:
            fig = plt.figure(figsize=(20,10), dpi=300)
            ax = plt.gca()

            if year < 2020: # include KKM
                stacked_data = [data['Kernkraftwerk Gösgen'], data['Kernkraftwerk Gösgen']+data['Leibstadt'], data['Kernkraftwerk Gösgen']+data['Leibstadt']+data['KKM Produktion'], data['Kernkraftwerk Gösgen']+data['Leibstadt']+data['KKM Produktion']+data['Beznau 1'], data['Kernkraftwerk Gösgen']+data['Leibstadt']+data['KKM Produktion']+data['Beznau 1']+data['Beznau 2']]
                y = np.array([data['Kernkraftwerk Gösgen'], data['Leibstadt'], data['KKM Produktion'], data['Beznau 1'], data['Beznau 2'], rest, data['Import'], data['Export']])
                plt.stackplot(range(0,len(data.index)), y, colors=self.params['colormap_pre2020'], labels=[None, None, None, None]+text_repo.labels_stack, zorder=10)
                plt.plot(range(0,len(data.index)), stacked_data[0], self.params['line'], lw=0.5, zorder=11)
                plt.plot(range(0,len(data.index)), stacked_data[1], self.params['line'], lw=0.5, zorder=11)
                plt.plot(range(0,len(data.index)), stacked_data[2], self.params['line'], lw=0.5, zorder=11)
                plt.plot(range(0,len(data.index)), stacked_data[3], self.params['line'], lw=0.5, zorder=11)
                plt.plot(range(0,len(data.index)), stacked_data[4], self.params['line'], lw=0.5, zorder=11)
                plt.annotate('Gösgen',    (len(data.index)-1600, stacked_data[0].iloc[len(data.index)-1600]+120), color=self.params['text'], rotation=45, fontsize=14, zorder=12)
                plt.annotate('Leibstadt', (len(data.index)-1300, stacked_data[1].iloc[len(data.index)-1300]+120), color=self.params['text'], rotation=45, fontsize=14, zorder=12)
                plt.annotate('Mühleberg', (len(data.index)-1000, stacked_data[2].iloc[len(data.index)-1000]+120), color=self.params['text'], rotation=45, fontsize=14, zorder=12)
                plt.annotate('Beznau 1',  (len(data.index)-700,  stacked_data[3].iloc[len(data.index)-700]+120),  color=self.params['text'], rotation=45, fontsize=14, zorder=12)
                plt.annotate('Beznau 2',  (len(data.index)-400,  stacked_data[4].iloc[len(data.index)-400]+120),  color=self.params['text'], rotation=45, fontsize=14, zorder=12)
            else: # exclude KKM
                stacked_data = [data['Kernkraftwerk Gösgen'], data['Kernkraftwerk Gösgen']+data['Leibstadt'], data['Kernkraftwerk Gösgen']+data['Leibstadt']+data['Beznau 1'], data['Kernkraftwerk Gösgen']+data['Leibstadt']+data['Beznau 1']+data['Beznau 2']]
                y = np.array([data['Kernkraftwerk Gösgen'], data['Leibstadt'], data['Beznau 1'], data['Beznau 2'], rest, data['Import'], data['Export']])
                plt.stackplot(range(0,len(data.index)), y, colors=self.params['colormap_post2020'], labels=[None, None, None]+text_repo.labels_stack, zorder=10)
                plt.plot(range(0,len(data.index)), stacked_data[0], self.params['line'], lw=0.5, zorder=11)
                plt.plot(range(0,len(data.index)), stacked_data[1], self.params['line'], lw=0.5, zorder=11)
                plt.plot(range(0,len(data.index)), stacked_data[2], self.params['line'], lw=0.5, zorder=11)
                plt.plot(range(0,len(data.index)), stacked_data[3], self.params['line'], lw=0.5, zorder=11)
                plt.annotate('Gösgen',    (len(data.index)-1300, stacked_data[0].iloc[len(data.index)-1300]+120), color=self.params['text'], rotation=45, fontsize=14, zorder=12)
                plt.annotate('Leibstadt', (len(data.index)-1000, stacked_data[1].iloc[len(data.index)-1000]+120), color=self.params['text'], rotation=45, fontsize=14, zorder=12)
                plt.annotate('Beznau 1',  (len(data.index)-700,  stacked_data[2].iloc[len(data.index)-700]+120),  color=self.params['text'], rotation=45, fontsize=14, zorder=12)
                plt.annotate('Beznau 2',  (len(data.index)-400,  stacked_data[3].iloc[len(data.index)-400]+120),  color=self.params['text'], rotation=45, fontsize=14, zorder=12)
            stack_max = max(np.sum(y, axis=0))

            if self.params['include_outages']:
                outages = self._get_outages(data)
                planned, forced = False, False
                if outages:
                    if today.year < 2020:
                        plt.annotate(text_repo.unit_annotation_pre2020, xycoords='figure fraction', xy=(0.07,0.03), fontsize=10)
                    else:
                        plt.annotate(text_repo.unit_annotation_post2020, xycoords='figure fraction', xy=(0.07,0.03), fontsize=10)
                    for outage in outages:
                        plt.scatter(outage[0], outage[1], marker=outage[2], s=120, c=outage[3], clip_on=False, zorder=20)
                        if not planned:
                            if outage[3] == self.params['Planned']:
                                plt.annotate(text_repo.planned, (outage[0]-35, outage[1]+500), color=self.params['Planned'], fontsize=14, rotation=90, zorder=25, bbox={'edgecolor': 'w', 'linewidth': 0, 'facecolor': 'w', 'alpha': 0.4, 'boxstyle': 'round'})
                                planned = True
                        if not forced:
                            if outage[3] == self.params['Forced']:                
                                plt.annotate(text_repo.forced, (outage[0]-35, outage[1]+500), color=self.params['Forced'], fontsize=14, rotation=90, zorder=25, bbox={'edgecolor': 'w', 'linewidth': 0, 'facecolor': 'w', 'alpha': 0.4, 'boxstyle': 'round'})
                                forced = True

            plt.title(text_repo.title, fontsize=34)

            plt.xticks([i for i in range(len(data.index)) if i%24 == 0], [text_repo.month_abbr[int(tick[3:5])] for tick in ticks[::24]], ha='left')
            ticklabels = [label.get_text() for label in ax.xaxis.get_ticklabels()]
            set_vis_idx = [ticklabels.index(m) for m in text_repo.month_abbr.values()]
            for i, label in enumerate(ax.xaxis.get_ticklabels()):
                if i not in set_vis_idx:
                    label.set_visible(False)
            plt.xlim(0,len(data.index)-1)

            plt.yticks(range(0, int(1.2*stack_max), 2500))
            plt.ylim(0, min(1.2*stack_max, 20000))
            plt.ylabel(text_repo.ylabel)

            plt.grid(axis='y', alpha=0.4, zorder=0)
            plt.box(on=False)
            ax.tick_params(axis='y', length=0, pad=15)
            ax.tick_params(axis='x', direction='in', length=10, color='dimgrey', pad=15)

            plt.legend(loc=9, bbox_to_anchor=(0.5,0.99), ncol=5, frameon=False, columnspacing=3).set_zorder(35)               

            plt.annotate(text_repo.annotation, xycoords='figure fraction', xy=(0.70,0.03), fontsize=10)

            imgax = fig.add_axes([0.8, 0.94, 0.1, 0.1], anchor='SE')
            imgax.imshow(logo)
            imgax.axis('off')

            if self.params['save_plot']:
                fname = os.path.join(path, text_repo.figname)
                fig.savefig(fname, dpi='figure', bbox_inches='tight', metadata={'Copyright':f'Swissnuclear, {today.year}', 'Author':'Yanis S.', 'Disclaimer':'Only allowed for private use. Contact Swissnuclear for more information.'})
            plt.close()

    def make_month_piebar(self):
        today = self.today - timedelta(days=28)

        plt.rcParams['font.size'] = self.params['fontsize']+6
        plt.rcParams['font.family'] = self.params['fontfamily']

        d = self.params['directories']
        path = os.path.join(d['export'], d['base'][0], d['layer1'][1])

        ### Initialize text repository
        De = TextRepoDE('month_piebar', today)
        Fr = TextRepoFR('month_piebar', today)
        En = TextRepoEN('month_piebar', today)
        text_repos = [De, Fr, En]

        ### Prepare data
        month = today.month
        year = today.year
        f = os.path.join('core','generation',str(year),f'{year}_{month:02d}_generation.csv')
        data = pd.read_csv(f)
        data.insert(3, 'Export', pd.NA)
        data.insert(3, 'Import', pd.NA)
        data['Import'] = [flow_value if flow_value > 0 else 0 for flow_value in data['FlowValue']]
        data['Export'] = [-flow_value if flow_value < 0 else 0 for flow_value in data['FlowValue']]
        data.drop(columns='FlowValue', inplace=True)
        rest = [load - nuc - imp if load - nuc - imp > 0 else 0 for load, nuc, imp in zip(data['TotalLoadValue'], data['Nuclear'], data['Import'])]
        data.insert(5, 'Rest', rest)

        sums = [data['Nuclear'].sum(), data['Rest'].sum(), data['Import'].sum()]

        ### Create figures
        logo = plt.imread(os.path.join('res', 'swissnuclear logo.png'))
        for text_repo in text_repos:
            fig, (ax1, ax2) = plt.subplots(1,2,figsize=(22,10))
            fig.subplots_adjust(wspace=0)
            fig.suptitle(text_repo.title, fontsize=34)

            # pie chart
            if sums[2] == 0: # import is 0
                pie_ratios = sums[:2]/sum(sums)
                explode = [0.1, 0]
                angle = -225*pie_ratios[0]
                wedges, *_ = ax1.pie(pie_ratios,  autopct='%1.0f%%', startangle=angle, labels=text_repo.labels_pie_small, explode=explode, colors=['#e69624', '#C8C8C8'])
            else:
                pie_ratios = sums/sum(sums)
                explode = [0.1, 0, 0]
                angle = -225*pie_ratios[0]
                wedges, *_ = ax1.pie(pie_ratios,  autopct='%1.0f%%', startangle=angle, labels=text_repo.labels_pie_large, explode=explode, colors=['#e69624', '#C8C8C8', '#7a1b1f'])

            # bar chart
            if today.year < 2020:
                bar_ratios = [data['Kernkraftwerk Gösgen'].sum(), data['Leibstadt'].sum(), data['Beznau 1'].sum(), data['Beznau 2'].sum(), data['KKM Produktion'].sum()] / data['Nuclear'].sum()
                bottom, width = 1, 0.1
                for j, (height, label) in enumerate(reversed([*zip(bar_ratios, text_repo.labels_bar)])):
                    bottom -= height
                    bc = ax2.bar(0, height, width, bottom=bottom, color='#e69624', label=label, alpha=0.1+0.2*j)
                    ax2.bar_label(bc, labels=[f'{height:.0%}'], label_type='center')

            else:
                bar_ratios = [data['Kernkraftwerk Gösgen'].sum(), data['Leibstadt'].sum(), data['Beznau 1'].sum(), data['Beznau 2'].sum()] / data['Nuclear'].sum()
                bottom, width = 1, 0.1
                for j, (height, label) in enumerate(reversed([*zip(bar_ratios, text_repo.labels_bar)])):
                    bottom -= height
                    bc = ax2.bar(0, height, width, bottom=bottom, color='#e69624', label=label, alpha=0.1+0.25*j)
                    ax2.bar_label(bc, labels=[f'{height:.0%}'], label_type='center')
                
            ax2.legend(loc=7)
            ax2.axis('off')
            ax2.set_xlim(- 2 * width, 3 * width)

            theta1, theta2 = wedges[0].theta1, wedges[0].theta2
            center, r = wedges[0].center, wedges[0].r
            bar_height = sum(bar_ratios)
            x = r * np.cos(np.pi / 180 * theta2) + center[0]
            y = r * np.sin(np.pi / 180 * theta2) + center[1]
            con = ConnectionPatch(xyA=(-width / 2, bar_height), coordsA=ax2.transData,
                                xyB=(x, y), coordsB=ax1.transData)
            con.set_color('#e69624')
            con.set_linewidth(2)
            ax2.add_artist(con)
            x = r * np.cos(np.pi / 180 * theta1) + center[0]
            y = r * np.sin(np.pi / 180 * theta1) + center[1]
            con = ConnectionPatch(xyA=(-width / 2, 0), coordsA=ax2.transData,
                                xyB=(x, y), coordsB=ax1.transData)
            con.set_color('#e69624')
            ax2.add_artist(con)
            con.set_linewidth(2)

            plt.annotate(text_repo.annotation, xycoords='figure fraction', xy=(0.62,0.03), fontsize=10)

            imgax = fig.add_axes([0.8, 0.94, 0.1, 0.1], anchor='SE')
            imgax.imshow(logo)
            imgax.axis('off')

            if self.params['save_plot']:
                fname = os.path.join(path, text_repo.figname)
                fig.savefig(fname, dpi='figure', bbox_inches='tight', metadata={'Copyright':f'Swissnuclear, {today.year}', 'Author':'Yanis S.', 'Disclaimer':'Only allowed for private use. Contact Swissnuclear for more information.'})
            plt.close()

    def make_year_piebar(self):
        today = self.today - timedelta(days=365)

        plt.rcParams['font.size'] = self.params['fontsize']+6
        plt.rcParams['font.family'] = self.params['fontfamily']
        d = self.params['directories']
        path = os.path.join(d['export'], d['base'][0], d['layer1'][2])

        ### Initialize text repository
        De = TextRepoDE('year_piebar', today)
        Fr = TextRepoFR('year_piebar', today)
        En = TextRepoEN('year_piebar', today)
        text_repos = [De, Fr, En]

        ### Prepare data
        data_list = []
        year = today.year
        path_gen = os.path.join('core','generation', str(year))
        for f in os.listdir(path_gen):
            data_list.append(pd.read_csv(os.path.join(path_gen, f)))
        data = pd.concat(data_list, axis=0)
        data.reset_index(drop=True, inplace=True)
        data.insert(3, 'Export', pd.NA)
        data.insert(3, 'Import', pd.NA)
        data['Import'] = [flow_value if flow_value > 0 else 0 for flow_value in data['FlowValue']]
        data['Export'] = [-flow_value if flow_value < 0 else 0 for flow_value in data['FlowValue']]
        data.drop(columns='FlowValue', inplace=True)
        rest = [load - nuc - imp if load - nuc - imp > 0 else 0 for load, nuc, imp in zip(data['TotalLoadValue'], data['Nuclear'], data['Import'])]
        data.insert(5, 'Rest', rest)

        sums = [data['Nuclear'].sum(), data['Rest'].sum(), data['Import'].sum()]

        ### Create figures
        logo = plt.imread(os.path.join('res', 'swissnuclear logo.png'))
        for text_repo in text_repos:
            fig, (ax1, ax2) = plt.subplots(1,2,figsize=(22,10))
            fig.subplots_adjust(wspace=0)
            fig.suptitle(text_repo.title, fontsize=34)

            # pie chart
            if sums[2] == 0: # import is 0
                pie_ratios = sums[:2]/sum(sums)
                explode = [0.1, 0]
                angle = -225*pie_ratios[0]
                wedges, *_ = ax1.pie(pie_ratios,  autopct='%1.0f%%', startangle=angle, labels=text_repo.labels_pie_small, explode=explode, colors=['#e69624', '#C8C8C8'])
            else:
                pie_ratios = sums/sum(sums)
                explode = [0.1, 0, 0]
                angle = -225*pie_ratios[0]
                wedges, *_ = ax1.pie(pie_ratios,  autopct='%1.0f%%', startangle=angle, labels=text_repo.labels_pie_large, explode=explode, colors=['#e69624', '#C8C8C8', '#7a1b1f'])

            # bar chart
            if today.year < 2020:
                bar_ratios = [data['Kernkraftwerk Gösgen'].sum(), data['Leibstadt'].sum(), data['Beznau 1'].sum(), data['Beznau 2'].sum(), data['KKM Produktion'].sum()] / data['Nuclear'].sum()
                bottom, width = 1, 0.1
                for j, (height, label) in enumerate(reversed([*zip(bar_ratios, text_repo.labels_bar)])):
                    bottom -= height
                    bc = ax2.bar(0, height, width, bottom=bottom, color='#e69624', label=label, alpha=0.1+0.2*j)
                    ax2.bar_label(bc, labels=[f'{height:.0%}'], label_type='center')

            else:
                bar_ratios = [data['Kernkraftwerk Gösgen'].sum(), data['Leibstadt'].sum(), data['Beznau 1'].sum(), data['Beznau 2'].sum()] / data['Nuclear'].sum()
                bottom, width = 1, 0.1
                for j, (height, label) in enumerate(reversed([*zip(bar_ratios, text_repo.labels_bar)])):
                    bottom -= height
                    bc = ax2.bar(0, height, width, bottom=bottom, color='#e69624', label=label, alpha=0.1+0.25*j)
                    ax2.bar_label(bc, labels=[f'{height:.0%}'], label_type='center')
                
            ax2.legend(loc=7)
            ax2.axis('off')
            ax2.set_xlim(- 2 * width, 3 * width)

            theta1, theta2 = wedges[0].theta1, wedges[0].theta2
            center, r = wedges[0].center, wedges[0].r
            bar_height = sum(bar_ratios)
            x = r * np.cos(np.pi / 180 * theta2) + center[0]
            y = r * np.sin(np.pi / 180 * theta2) + center[1]
            con = ConnectionPatch(xyA=(-width / 2, bar_height), coordsA=ax2.transData,
                                xyB=(x, y), coordsB=ax1.transData)
            con.set_color('#e69624')
            con.set_linewidth(2)
            ax2.add_artist(con)
            x = r * np.cos(np.pi / 180 * theta1) + center[0]
            y = r * np.sin(np.pi / 180 * theta1) + center[1]
            con = ConnectionPatch(xyA=(-width / 2, 0), coordsA=ax2.transData,
                                xyB=(x, y), coordsB=ax1.transData)
            con.set_color('#e69624')
            ax2.add_artist(con)
            con.set_linewidth(2)

            plt.annotate(text_repo.annotation, xycoords='figure fraction', xy=(0.62,0.03), fontsize=10)

            imgax = fig.add_axes([0.8, 0.94, 0.1, 0.1], anchor='SE')
            imgax.imshow(logo)
            imgax.axis('off')

            if self.params['save_plot']:
                fname = os.path.join(path, text_repo.figname)
                fig.savefig(fname, dpi='figure', bbox_inches='tight', metadata={'Copyright':f'Swissnuclear, {today.year}', 'Author':'Yanis S.', 'Disclaimer':'Only allowed for private use. Contact Swissnuclear for more information.'})
            plt.close()

    def make_alltime_piebar(self):
        today = self.today

        plt.rcParams['font.size'] = self.params['fontsize']+6
        plt.rcParams['font.family'] = self.params['fontfamily']
        d = self.params['directories']
        path = os.path.join(d['export'], d['base'][0], d['layer1'][3])
        months = list(range(1,13))

        ### Initialize text repository
        De = TextRepoDE('alltime_piebar', today)
        Fr = TextRepoFR('alltime_piebar', today)
        En = TextRepoEN('alltime_piebar', today)
        text_repos = [De, Fr, En]

        ### Prepare data
        base = os.path.join('core','generation')
        years = os.listdir(base)
        years.remove(str(datetime.today().year))
        data = {y: {m: None for m in months} for y in years}
        for y in years:
            for i, f in enumerate(os.listdir(os.path.join(base, y))):
                data[y][i+1] = pd.read_csv(os.path.join(base,y,f))
                data[y][i+1].insert(len(data[y][i+1].columns), 'Rest', data[y][i+1]['TotalLoadValue'] - data[y][i+1]['Nuclear'] - data[y][i+1]['FlowValue'])
        monthly_avg = {m: None for m in months}
        for m in months:
            month_data = []
            for y in years:
                month_data.append(data[y][m])
            month_data = pd.concat(month_data, axis=0)
            monthly_avg[m] = month_data.mean(axis=0, numeric_only=True)
            if monthly_avg[m]['FlowValue'] < 0:
                monthly_avg[m]['FlowValue'] = 0

        ### Create figures
        logo = plt.imread(os.path.join('res', 'swissnuclear logo.png'))
        for text_repo in text_repos:
            for m, v in monthly_avg.items():
                fig, (ax1, ax2) = plt.subplots(1,2,figsize=(22,10))
                fig.subplots_adjust(wspace=0)
                fig.suptitle(text_repo.title[m-1], fontsize=34)

                # pie chart
                if v['FlowValue'] == 0:
                    pie_ratios = [v['Nuclear'], v['Rest']] / (v['TotalLoadValue']+v['Nuclear'])
                    explode = [0.1, 0]
                    angle = -225*pie_ratios[0]
                    wedges, *_ = ax1.pie(pie_ratios,  autopct='%1.0f%%', startangle=angle, labels=text_repo.labels_pie_small, explode=explode, colors=['#e69624', '#C8C8C8'])
                else:
                    pie_ratios = [v['Nuclear'], v['FlowValue'], v['Rest']] / (v['TotalLoadValue']+v['FlowValue']+v['Nuclear'])
                    explode = [0.1, 0, 0]
                    angle = -225*pie_ratios[0]
                    wedges, *_ = ax1.pie(pie_ratios, autopct='%1.0f%%', startangle=angle, labels=text_repo.labels_pie_large, explode=explode, colors=['#e69624', '#7a1b1f', '#C8C8C8'])

                # bar chart
                bar_ratios = [v['Kernkraftwerk Gösgen'], v['Leibstadt'], v['Beznau 1'], v['Beznau 2'], v['KKM Produktion']] / v['Nuclear']
                bottom, width = 1, 0.1
                for j, (height, label) in enumerate(reversed([*zip(bar_ratios, text_repo.labels_bar)])):
                    bottom -= height
                    bc = ax2.bar(0, height, width, bottom=bottom, color='#e69624', label=label, alpha=0.1+0.2*j)
                    ax2.bar_label(bc, labels=[f'{height:.0%}'], label_type='center')
                ax2.legend(loc=7)
                ax2.axis('off')
                ax2.set_xlim(- 2 * width, 3 * width)

                theta1, theta2 = wedges[0].theta1, wedges[0].theta2
                center, r = wedges[0].center, wedges[0].r
                bar_height = sum(bar_ratios)
                x = r * np.cos(np.pi / 180 * theta2) + center[0]
                y = r * np.sin(np.pi / 180 * theta2) + center[1]
                con = ConnectionPatch(xyA=(-width / 2, bar_height), coordsA=ax2.transData,
                                    xyB=(x, y), coordsB=ax1.transData)
                con.set_color('#e69624')
                con.set_linewidth(2)
                ax2.add_artist(con)
                x = r * np.cos(np.pi / 180 * theta1) + center[0]
                y = r * np.sin(np.pi / 180 * theta1) + center[1]
                con = ConnectionPatch(xyA=(-width / 2, 0), coordsA=ax2.transData,
                                    xyB=(x, y), coordsB=ax1.transData)
                con.set_color('#e69624')
                ax2.add_artist(con)
                con.set_linewidth(2)

                plt.annotate(text_repo.annotation, xycoords='figure fraction', xy=(0.62,0.03), fontsize=10)

                imgax = fig.add_axes([0.8, 0.94, 0.1, 0.1], anchor='SE')
                imgax.imshow(logo)
                imgax.axis('off')

                if self.params['save_plot']:
                    fname = os.path.join(path, text_repo.figname[m-1])
                    fig.savefig(fname, dpi='figure', bbox_inches='tight', metadata={'Copyright':f'Swissnuclear, {today.year}', 'Author':'Yanis S.', 'Disclaimer':'Only allowed for private use. Contact Swissnuclear for more information.'})
                plt.close()

    def convert_file(self):
        today = self.today
        dirs = self.params['directories']

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
            original_file = os.path.join('core','generation', f'{today.year}', f'{today.year}_{today.month:02d}_generation.csv')
            data = pd.read_csv(original_file)

            imp = [flow_value if flow_value > 0 else 0 for flow_value in data['FlowValue']]
            rest = [l - n - i if l - n - i > 0 else 0 for l, n, i in zip(data['TotalLoadValue'], data['Nuclear'], imp)]
            data.insert(2, 'Other', rest)

            data.rename(columns={'TotalLoadValue': 'Load', 'FlowValue': 'Import+/Export-', 'KKM Produktion': 'Muehleberg', 'Kernkraftwerk Gösgen': 'Goesgen'}, inplace=True)
            order = ['Date', 'Time', 'Load', 'Nuclear', 'Goesgen', 'Leibstadt', 'Muehleberg', 'Beznau 1', 'Beznau 2', 'Import+/Export-', 'Other'] # drops not mentioned automatically
            data = data[order]
            data = data.round({'Other': 1, 'Import+/Export-': 1})

            for text_repo in text_repos:
                data.to_csv(os.path.join(dirs['export'], dirs['base'][1], text_repo.filename), index=False)

            today = today - timedelta(days=today.day)