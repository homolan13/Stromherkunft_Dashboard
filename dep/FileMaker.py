"""
Author: Yanis Schärer, yanis.schaerer@swissnuclear.ch
As of: see README.txt
"""
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
        self.units = ['Kernkraftwerk Gösgen', 'Leibstadt', 'KKM Produktion', 'Beznau 1', 'Beznau 2']
        self.names = ['Gösgen', 'Leibstadt', 'Mühleberg', 'Beznau 1', 'Beznau 2']
        self.names_dict = {k:v for k,v in zip(self.units,self.names)}

    def _get_outages(self, data: pd.DataFrame, today: datetime):
        return_list = [] # one entry: (unit, x, y, marker, color)
        marker_type = {k:v for k,v in zip(self.units,['$G$', '$L$', '$M$', '$B_1$', '$B_2$'])}
        history = {k:[] for k in self.units} # values are of type ('planned/forced', idx)

        outages = pd.read_csv(os.path.join('core', 'outages',f'{today.year}_outages.csv'))
        outages = outages[outages['Type'] == 'Forced'] # keep forced outages only
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
            
            idx = self.units.index(outage['UnitName'])
            return_list.append((outage['UnitName'], start_idx, np.sum(np.array([data[self.units[unit]][start_idx] for unit in range(idx+1)]), axis=0), marker_type[outage['UnitName']]))

        return return_list

    def _csp(self, data, outage_idx, min_dist):
        """
        Returns index to position annotation labels using a constraint satisfaction problem
        """
        unit_idx = {k: None for k in self.units} # initialise dict
        for u in self.units:
            indices = list(data[data[u] > 250].index)
            mask = [True for _ in indices]
            for o_idx in outage_idx:
                for i, idx in enumerate(indices):
                    if abs(idx-o_idx) < min_dist:
                        mask[i] = False # inplace removing makes problems as indices are skipped, thus use masking

            indices = [idx for i,idx in enumerate(indices) if mask[i]]
            if indices:
                unit_idx[u] = indices

        data_len = len(data.index)
        best_option = data_len//2

        unit_len = {k: (len(unit_idx[k]) if type(unit_idx[k]) is list else data_len+1) for k in self.units}
        while any(x < data_len+1 for x in list(unit_len.values())):
            min_unit = min(unit_len, key=unit_len.get)
            unit_idx[min_unit] = min(unit_idx[min_unit], key=lambda x:abs(x-best_option))
            ### start of rule: at least min_distance between annotations ###
            for v in unit_idx.values():
                if type(v) is list:
                    active_loop = True
                    while active_loop:
                        vmin = min(v, key=lambda x:abs(x-unit_idx[min_unit]))
                        if abs(vmin - unit_idx[min_unit]) < min_dist and len(v) > 1:
                            v.remove(vmin)
                        else:
                            active_loop = False
            ### end of rule ###
            unit_len = {k: (len(unit_idx[k]) if type(unit_idx[k]) is list else data_len+1) for k in self.units}

        return unit_idx
        
    def make_dirs(self):
        """ Makes necessary directories if not already existing """
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
        last_30_ym = set([(day.year, day.month) for day in last_30])
        last_30_str = [f'{day.year}-{day.month:02d}-{day.day:02d}' for day in last_30]

        data = []
        fnames = set([os.path.join('core','generation',f'{y}',f'{y}_{m:02d}_generation.csv') for y,m in last_30_ym]) # get all necessary file names
        for fname in fnames:
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

        rest = [load + exp - nuc - sol - imp if load + exp - nuc - sol - imp > 0 else 0 for load, nuc, sol, imp, exp in zip(data['TotalLoadValue'], data['Nuclear'], data['Solar'], data['Import'], data['Export'])]
        ticks = [f'{d[-3:-1]}.{d[5:7]}.' for d in data['Date']]

        y = np.array([data['Nuclear'], rest, data['Solar'], data['Import']])
        stack_max = max(np.sum(y, axis=0))

        ### Create figures
        logo = plt.imread(os.path.join('res', 'swissnuclear logo.png'))
        return_list = []
        for text_repo in text_repos:
            fig = plt.figure(figsize=(20,10), dpi=300)
            ax = plt.gca()

            plt.stackplot(range(0,len(data.index)), y, colors=self.params['colormap'], labels=text_repo.labels_stack, zorder=10)
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

            plt.legend(loc=9, bbox_to_anchor=(0.5,0.99), ncol=len(text_repo.labels_stack)+1, frameon=False, columnspacing=2).set_zorder(35)

            plt.annotate(text_repo.annotation, xycoords='figure fraction', xy=(0.65,0.05), fontsize=10, va='top') # add copyright

            imgax = fig.add_axes([0.8, 0.94, 0.1, 0.1], anchor='SE') # add swissnuclear logo
            imgax.imshow(logo)
            imgax.axis('off')


            if self.params['save_plot']:
                fname = os.path.join(path, text_repo.figname)
                fig.savefig(fname, dpi='figure', bbox_inches='tight', metadata={'Copyright':f'Swissnuclear, {today.year}', 'Author':'Yanis S.', 'Disclaimer':'Only allowed for private use. Contact Swissnuclear for more information.'})
                return_list.append(fname)
            plt.close()

        return return_list

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

        rest = [load + exp - nuc - sol - imp if load + exp - nuc - sol - imp > 0 else 0 for load, nuc, sol, imp, exp in zip(data['TotalLoadValue'], data['Nuclear'], data['Solar'], data['Import'], data['Export'])]
        ticks = [f'{d[-3:-1]}.{d[5:7]}.' for d in data['Date']]

        ### Create figures
        logo = plt.imread(os.path.join('res', 'swissnuclear logo.png'))
        return_list = []
        for text_repo in text_repos:
            fig = plt.figure(figsize=(20,10), dpi=300)
            ax = plt.gca()

            outage_idx = []
            if self.params['include_outages']:
                outages = self._get_outages(data, today)
                annotated = True
                if outages:
                    outage_legend = set()
                    for outage in outages:
                        outage_legend.add(text_repo.outage_annotations[outage[0]])
                        outage_idx.append(outage[1])
                        plt.scatter(outage[1], outage[2], marker=outage[3], s=120, c=self.params['color_outages'], clip_on=False, zorder=20)
                        if annotated:
                            plt.annotate(text_repo.outage_annotated, (outage[1]-4, outage[2]+500), color=self.params['color_outages'], fontsize=14, rotation=90, zorder=25, bbox={'edgecolor': 'w', 'linewidth': 0, 'facecolor': 'w', 'alpha': 0.4, 'boxstyle': 'round'})
                            annotated = False
                    plt.annotate(', '.join(outage_legend), xycoords='figure fraction', xy=(0.07,0.05), fontsize=10, va='top')

            annotation_idx = self._csp(data, outage_idx, 50)
            y = np.array([data['Nuclear'], rest, data['Solar'], data['Import']])
            plt.stackplot(range(0,len(data.index)), y, colors=self.params['colormap'], labels=text_repo.labels_stack, zorder=10)
            accumulated = pd.concat([data[unit] for unit in self.units], axis=1).cumsum(axis=1)
            for unit, idx in annotation_idx.items():
                if idx is not None:
                    plt.plot(range(0,len(data.index)), accumulated[unit], color=self.params['line'], lw=1.5, zorder=12)
                    plt.scatter(idx, accumulated[unit].iloc[idx], c=self.params['text'], s=50, zorder=13, clip_on=False)
                    plt.annotate(self.names_dict[unit], xy=(idx, accumulated[unit].iloc[idx]+300), color=self.params['text'], fontsize=14, ha='center', va='center', annotation_clip=False, zorder=14)

            stack_max = max(np.sum(y, axis=0))

            plt.plot(data['TotalLoadValue'], color='k', linewidth=2, label=text_repo.labels_load, zorder=11)
              
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

            plt.legend(loc=9, bbox_to_anchor=(0.5,0.99), ncol=len(text_repo.labels_stack)+1, frameon=False, columnspacing=2).set_zorder(35)          

            plt.annotate(text_repo.annotation, xycoords='figure fraction', xy=(0.65,0.05), fontsize=10, va='top')

            imgax = fig.add_axes([0.8, 0.94, 0.1, 0.1], anchor='SE')
            imgax.imshow(logo)
            imgax.axis('off')

            if self.params['save_plot']:
                fname = os.path.join(path, text_repo.figname)
                fig.savefig(fname, dpi='figure', bbox_inches='tight', metadata={'Copyright':f'Swissnuclear, {today.year}', 'Author':'Yanis S.', 'Disclaimer':'Only allowed for private use. Contact Swissnuclear for more information.'})
                return_list.append(fname)
            plt.close()

        return return_list

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

        rest = [load + exp - nuc - sol - imp if load + exp - nuc - sol - imp > 0 else 0 for load, nuc, sol, imp, exp in zip(data['TotalLoadValue'], data['Nuclear'], data['Solar'], data['Import'], data['Export'])]
        ticks = [f'{d[-3:-1]}.{d[5:7]}.' for d in data['Date']]

        ### Create figures
        logo = plt.imread(os.path.join('res', 'swissnuclear logo.png'))
        return_list = []
        for text_repo in text_repos:
            fig = plt.figure(figsize=(20,10), dpi=300)
            ax = plt.gca()

            outage_idx = []
            if self.params['include_outages']:
                outages = self._get_outages(data, today)
                annotated = True
                if outages:
                    outage_legend = set()
                    for outage in outages:
                        outage_legend.add(text_repo.outage_annotations[outage[0]])
                        outage_idx.append(outage[1])
                        plt.scatter(outage[1], outage[2], marker=outage[3], s=120, c=self.params['color_outages'], clip_on=False, zorder=20)
                        if annotated:
                            plt.annotate(text_repo.outage_annotated, (outage[1]-40, outage[2]+500), color=self.params['color_outages'], fontsize=14, rotation=90, zorder=25, bbox={'edgecolor': 'w', 'linewidth': 0, 'facecolor': 'w', 'alpha': 0.4, 'boxstyle': 'round'})
                            annotated = False
                    plt.annotate(', '.join(outage_legend), xycoords='figure fraction', xy=(0.07,0.05), fontsize=10, va='top')

            annotation_idx = self._csp(data, outage_idx, 500)
            y = np.array([data['Nuclear'], rest, data['Solar'], data['Import']])
            plt.stackplot(range(0,len(data.index)), y, colors=self.params['colormap'], labels=text_repo.labels_stack, zorder=10)
            accumulated = pd.concat([data[unit] for unit in self.units], axis=1).cumsum(axis=1)
            for unit, idx in annotation_idx.items():
                if idx is not None:
                    plt.plot(range(0,len(data.index)), accumulated[unit], color=self.params['line'], lw=1.5, zorder=12)
                    plt.scatter(idx, accumulated[unit].iloc[idx], c=self.params['text'], s=50, zorder=13, clip_on=False)
                    plt.annotate(self.names_dict[unit], xy=(idx, accumulated[unit].iloc[idx]+300), color=self.params['text'], fontsize=14, ha='center', va='center', annotation_clip=False, zorder=14)
            
            stack_max = max(np.sum(y, axis=0))

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

            plt.legend(loc=9, bbox_to_anchor=(0.5,0.99), ncol=len(text_repo.labels_stack)+1, frameon=False, columnspacing=2).set_zorder(35)               

            plt.annotate(text_repo.annotation, xycoords='figure fraction', xy=(0.65,0.05), fontsize=10, va='top')

            imgax = fig.add_axes([0.8, 0.94, 0.1, 0.1], anchor='SE')
            imgax.imshow(logo)
            imgax.axis('off')

            if self.params['save_plot']:
                fname = os.path.join(path, text_repo.figname)
                fig.savefig(fname, dpi='figure', bbox_inches='tight', metadata={'Copyright':f'Swissnuclear, {today.year}', 'Author':'Yanis S.', 'Disclaimer':'Only allowed for private use. Contact Swissnuclear for more information.'})
                return_list.append(fname)
            plt.close()

        return return_list

    def make_month_distribution(self):
        today = self.today - timedelta(days=28)

        plt.rcParams['font.size'] = self.params['fontsize']+2
        plt.rcParams['font.family'] = self.params['fontfamily']

        d = self.params['directories']
        path = os.path.join(d['export'], d['base'][0], d['layer1'][1])

        ### Initialize text repository
        De = TextRepoDE('month_distribution', today)
        Fr = TextRepoFR('month_distribution', today)
        En = TextRepoEN('month_distribution', today)
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
        rest = [load + exp - nuc - sol - imp if load + exp - nuc - sol - imp > 0 else 0 for load, nuc, sol, imp, exp in zip(data['TotalLoadValue'], data['Nuclear'], data['Solar'], data['Import'], data['Export'])]
        data.insert(5, 'Rest', rest)

        sums = [data['Nuclear'].sum(), data['Rest'].sum(), data['Solar'].sum(), data['Import'].sum()]

        ### Create figures
        logo = plt.imread(os.path.join('res', 'swissnuclear logo.png'))
        return_list = []
        for text_repo in text_repos:
            fig, (ax1, ax2) = plt.subplots(1,2,figsize=(20,10))
            fig.subplots_adjust(wspace=0)
            fig.suptitle(text_repo.title, fontsize=34)

            # pie chart
            if sums[-1] == 0: # import is 0
                pie_ratios = sums[:-1]/sum(sums)
                explode = [0.1] + (len(sums)-2)*[0]
                angle = 360*(1-pie_ratios[0]/2) # 0° is start --> (counter-clockwise) 360° - half of important slice
                wedges, *_ = ax1.pie(pie_ratios,  autopct='%1.1f%%', startangle=angle, labels=text_repo.labels_pie_small, explode=explode, colors=self.params['colormap'])
            else:
                pie_ratios = sums/sum(sums)
                explode = [0.1] + (len(sums)-1)*[0]
                angle = 360*(1-pie_ratios[0]/2)
                wedges, *_ = ax1.pie(pie_ratios,  autopct='%1.1f%%', startangle=angle, labels=text_repo.labels_pie_large, explode=explode, colors=self.params['colormap'])

            # bar chart
            if today.year < 2020:
                bar_ratios = [data[unit].sum() for unit in self.units] / data['Nuclear'].sum()
                bottom, width = 1, 0.1
                for j, (height, label) in enumerate(reversed([*zip(bar_ratios, text_repo.labels_bar)])):
                    bottom -= height
                    bc = ax2.bar(0, height, width, bottom=bottom, color='#e69624', label=label, alpha=0.2+0.2*j)
                    pct = pie_ratios[0]*height
                    ax2.bar_label(bc, labels=[f'{pct:.1%}'], label_type='center')
            else:
                bar_ratios = [data[unit].sum() for unit in self.units if unit != 'KKM Produktion'] / data['Nuclear'].sum()
                bottom, width = 1, 0.1
                for j, (height, label) in enumerate(reversed([*zip(bar_ratios, text_repo.labels_bar)])):
                    bottom -= height
                    bc = ax2.bar(0, height, width, bottom=bottom, color='#e69624', label=label, alpha=0.25+0.25*j)
                    pct = pie_ratios[0]*height
                    ax2.bar_label(bc, labels=[f'{pct:.1%}'], label_type='center')
                
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

            plt.annotate(text_repo.roundingerror, xycoords='figure fraction', xy=(0.07,0.05), fontsize=10, va='top')
            plt.annotate(text_repo.annotation, xycoords='figure fraction', xy=(0.60,0.05), fontsize=10, va='top')

            imgax = fig.add_axes([0.8, 0.94, 0.1, 0.1], anchor='SE')
            imgax.imshow(logo)
            imgax.axis('off')

            if self.params['save_plot']:
                fname = os.path.join(path, text_repo.figname)
                fig.savefig(fname, dpi='figure', bbox_inches='tight', metadata={'Copyright':f'Swissnuclear, {today.year}', 'Author':'Yanis S.', 'Disclaimer':'Only allowed for private use. Contact Swissnuclear for more information.'})
                return_list.append(fname)
            plt.close()

        return return_list

    def make_year_distribution(self):
        today = self.today - timedelta(days=365)

        plt.rcParams['font.size'] = self.params['fontsize']+2
        plt.rcParams['font.family'] = self.params['fontfamily']
        d = self.params['directories']
        path = os.path.join(d['export'], d['base'][0], d['layer1'][2])

        ### Initialize text repository
        De = TextRepoDE('year_distribution', today)
        Fr = TextRepoFR('year_distribution', today)
        En = TextRepoEN('year_distribution', today)
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
        rest = [load + exp - nuc - sol - imp if load + exp - nuc - sol - imp > 0 else 0 for load, nuc, sol, imp, exp in zip(data['TotalLoadValue'], data['Nuclear'], data['Solar'], data['Import'], data['Export'])]
        data.insert(5, 'Rest', rest)

        sums = [data['Nuclear'].sum(), data['Rest'].sum(), data['Solar'].sum(), data['Import'].sum()]

        ### Create figures
        logo = plt.imread(os.path.join('res', 'swissnuclear logo.png'))
        return_list = []
        for text_repo in text_repos:
            fig, (ax1, ax2) = plt.subplots(1,2,figsize=(20,10))
            fig.subplots_adjust(wspace=0)
            fig.suptitle(text_repo.title, fontsize=34)

            # pie chart
            if sums[-1] == 0: # import is 0
                pie_ratios = sums[:-1]/sum(sums)
                explode = [0.1] + (len(sums)-2)*[0]
                angle = 360*(1-pie_ratios[0]/2)
                wedges, *_ = ax1.pie(pie_ratios,  autopct='%1.1f%%', startangle=angle, labels=text_repo.labels_pie_small, explode=explode, colors=self.params['colormap'])
            else:
                pie_ratios = sums/sum(sums)
                explode = [0.1] + (len(sums)-1)*[0]
                angle = 360*(1-pie_ratios[0]/2)
                wedges, *_ = ax1.pie(pie_ratios,  autopct='%1.1f%%', startangle=angle, labels=text_repo.labels_pie_large, explode=explode, colors=self.params['colormap'])

            # bar chart
            if today.year < 2020:
                bar_ratios = [data[unit].sum() for unit in self.units] / data['Nuclear'].sum()
                bottom, width = 1, 0.1
                for j, (height, label) in enumerate(reversed([*zip(bar_ratios, text_repo.labels_bar)])):
                    bottom -= height
                    bc = ax2.bar(0, height, width, bottom=bottom, color='#e69624', label=label, alpha=0.2+0.2*j)
                    pct = pie_ratios[0]*height
                    ax2.bar_label(bc, labels=[f'{pct:.1%}'], label_type='center')

            else:
                bar_ratios = [data[unit].sum() for unit in self.units if unit != 'KKM Produktion'] / data['Nuclear'].sum()
                bottom, width = 1, 0.1
                for j, (height, label) in enumerate(reversed([*zip(bar_ratios, text_repo.labels_bar)])):
                    bottom -= height
                    bc = ax2.bar(0, height, width, bottom=bottom, color='#e69624', label=label, alpha=0.25+0.25*j)
                    pct = pie_ratios[0]*height
                    ax2.bar_label(bc, labels=[f'{pct:.1%}'], label_type='center')
                
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

            plt.annotate(text_repo.roundingerror, xycoords='figure fraction', xy=(0.07,0.05), fontsize=10, va='top')
            plt.annotate(text_repo.annotation, xycoords='figure fraction', xy=(0.60,0.05), fontsize=10, va='top')

            imgax = fig.add_axes([0.8, 0.94, 0.1, 0.1], anchor='SE')
            imgax.imshow(logo)
            imgax.axis('off')

            if self.params['save_plot']:
                fname = os.path.join(path, text_repo.figname)
                fig.savefig(fname, dpi='figure', bbox_inches='tight', metadata={'Copyright':f'Swissnuclear, {today.year}', 'Author':'Yanis S.', 'Disclaimer':'Only allowed for private use. Contact Swissnuclear for more information.'})
                return_list.append(fname)
            plt.close()

        return return_list

    def convert_file(self):
        today = self.today
        dirs = self.params['directories']

        loops = 1
        if today.day < 5 or today.day == 15:
            loops += 1

        # Convert data
        return_list = []
        for _ in range(loops):
            original_file = os.path.join('core','generation', f'{today.year}', f'{today.year}_{today.month:02d}_generation.csv')
            data = pd.read_csv(original_file)

            imp = [flow_value if flow_value > 0 else 0 for flow_value in data['FlowValue']]
            rest = [l - n - s - i if l - n - s - i > 0 else 0 for l, n, s, i in zip(data['TotalLoadValue'], data['Nuclear'], data['Solar'], imp)]
            data.insert(2, 'Hydro & other', rest)

            data.rename(columns={'TotalLoadValue': 'Load', 'FlowValue': 'Import+/Export-', 'KKM Produktion': 'Muehleberg', 'Kernkraftwerk Gösgen': 'Goesgen'}, inplace=True)
            order = ['Date', 'Time', 'Load', 'Nuclear', 'Goesgen', 'Leibstadt', 'Muehleberg', 'Beznau 1', 'Beznau 2', 'Hydro & other', 'Solar', 'Import+/Export-'] # drops not mentioned automatically
            data = data[order]
            data = data.round({'Hydro & other': 1, 'Import+/Export-': 1})

            # Initialize text repositories
            De = TextRepoDE('datafile', today)
            Fr = TextRepoFR('datafile', today)
            En = TextRepoEN('datafile', today)
            text_repos = [De, Fr, En]

            for text_repo in text_repos:
                fname = os.path.join(dirs['export'], dirs['base'][1], text_repo.filename)
                data.to_csv(fname, index=False)
                return_list.append(fname)

            today = today - timedelta(days=today.day)

        return return_list

