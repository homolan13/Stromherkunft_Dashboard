import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from datetime import datetime, timedelta

include_outages = False
show_plot = False
save_plot = True

plt.rcParams['font.size'] = 20
plt.rcParams['font.family'] = 'Segoe UI'

logo = plt.imread('swissnuclear logo.png')

color_map = ['#e3001a', 'silver', 'coral', 'lightgreen']
labels_de = ['Nuklear', 'Rest', 'Import', 'Export']

month_short = {'01': 'Jan.', '02': 'Febr.', '03': 'März', '04': 'Apr.', '05': 'Mai', '06': 'Juni', '07': 'Juli', '08': 'Aug.', '09': 'Sept.', '10': 'Okt.', '11': 'Nov.', '12': 'Dez.'}

def get_month(month):
    if type(month) is not int:
        month = int(month)
    match month:
        case 1:
            return 'Januar'
        case 2:
            return 'Februar'
        case 3:
            return 'März'
        case 4:
            return 'April'
        case 5:
            return 'Mai'
        case 6: 
            return 'Juni'
        case 7:
            return 'Juli'
        case 8:
            return 'August'
        case 9:
            return 'Septemper'
        case 10:
            return 'Oktober'
        case 11:
            return 'Novemeber'
        case 12:
            return 'Dezember'
        case _:
            return 'Invalid!'

def main():
    print('\nCreating graphics...')
    # today = datetime.today() - timedelta(days=1) # real date
    today = datetime(2022,1,6) # custom date

    ###############
    ### sliding ###
    ###############
    last_30 = [today - timedelta(days=i) for i in range(30)]
    last_30_my = set([(day.year, day.month) for day in last_30])
    last_30_str = [f'{day.year}-{day.month:02d}-{day.day:02d}' for day in last_30]
    data = []

    for my in last_30_my:
        fname = os.path.join('generation',f'{my[0]}',f'{my[0]}_{my[1]:02d}_generation.csv')
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

    fig_s = plt.figure(figsize=(20,10), dpi=80)
    ax = plt.gca()

    plt.stackplot(range(0,len(data.index)), y, colors=color_map, labels=labels_de, zorder=10)
    plt.plot(data['TotalLoadValue'], color='k', linewidth=2, label='Last', zorder=20)

    plt.title(f'Nettostromerzeugung in der Schweiz in den letzten 30 Tagen', fontsize=34)

    plt.xticks([i for i in range(len(data.index)) if i%24 == 0], ticks[::24], ha='center')
    for i, label in enumerate(ax.xaxis.get_ticklabels()):
        if (i+3)%4:
            label.set_visible(False)
    plt.xlim(0,len(data.index)-1)

    plt.yticks(range(0, int(1.2*stack_max), 2500))
    plt.ylim(0, min(1.2*stack_max, 20000))
    plt.ylabel('Leistung [MW]')

    plt.grid(axis='y', alpha=0.4, zorder=0)
    ax.spines[['top','right','left','bottom']].set_visible(False)
    ax.tick_params(axis='y', length=0, pad=15)
    ax.tick_params(axis='x', direction='out', length=2, color='dimgrey', pad=15)

    plt.legend(loc=9, bbox_to_anchor=(0.5,0.99), ncol=5, frameon=False, columnspacing=3).set_zorder(35)

    plt.annotate(r'$\copyright$'+f' swissnuclear, {datetime.today().year}. Datenquelle: Entso-E', xycoords='figure fraction', xy=(0.70,0.03), fontsize=10)

    imgax = fig_s.add_axes([0.8, 0.94, 0.1, 0.1], anchor='SE')
    imgax.imshow(logo)
    imgax.axis('off')

    if show_plot:
        plt.show()
    if save_plot:
        path_s = os.path.join('plots', 'sliding')
        for f in os.listdir(path_s):
            os.remove(os.path.join(path_s, f))
        fname_s = os.path.join(path_s, f'{today.year}_{today.month:02d}_{today.day:02d}_sliding.png')
        fig_s.savefig(fname_s, dpi='figure', bbox_inches='tight', metadata={'Copyright':f'Swissnuclear, {today.year}', 'Author':'Yanis S.', 'Disclaimer':'Only allowed for private use. Contact Swissnuclear for more information.'})


    #################
    ### per month ###
    #################
    if today.day == 6: # create plot at the 6th of the following month
        month = (today - timedelta(days=28)).month
        year = (today - timedelta(days=28)).year
        f = os.path.join('generation',str(year),f'{year}_{month:02d}_generation.csv')
        data = pd.read_csv(f)
        data.insert(3, 'Export', pd.NA)
        data.insert(3, 'Import', pd.NA)
        data['Import'] = [flow_value if flow_value > 0 else 0 for flow_value in data['FlowValue']]
        data['Export'] = [-flow_value if flow_value < 0 else 0 for flow_value in data['FlowValue']]
        data.drop(columns='FlowValue', inplace=True)

        rest = [load - nuc - imp if load - nuc - imp > 0 else 0 for load, nuc, imp in zip(data['TotalLoadValue'], data['Nuclear'], data['Import'])]
        ticks = [f'{d[-3:-1]}.{d[5:7]}.' for d in data['Date']]

        if include_outages:
            data_out = pd.read_csv(os.path.join('outages',f'{year}_outages.csv'))

        fig_m = plt.figure(figsize=(20,10), dpi=80)
        ax = plt.gca()

        if year < 2020: # include KKM
            y = np.array([data['Kernkraftwerk Gösgen'], data['Leibstadt'], data['KKM Produktion'], data['Beznau 1'], data['Beznau 2'], rest, data['Import'], data['Export']])
            stack_max = max(np.sum(y, axis=0))

            plt.stackplot(range(0,len(data.index)), y, colors=color_map, labels=labels_de, zorder=10)
            plt.plot(data['TotalLoadValue'], color='k', linewidth=2, label='Last', zorder=20)

            plt.title(f'Nettostromerzeugung in der Schweiz im {get_month(month)} {year}', fontsize=34)

            plt.xticks([i for i in range(len(data.index)) if i%24 == 0], ticks[::24])
            for i, label in enumerate(ax.xaxis.get_ticklabels()):
                if (i+2)%5 != 0:
                    label.set_visible(False)
            plt.xlim(0,len(data.index)-1)

            plt.yticks(range(0, int(1.2*stack_max), 2500))
            plt.ylim(0, min(1.2*stack_max, 20000))
            plt.ylabel('Leistung [MW]')

            plt.grid(axis='y', alpha=0.4, zorder=0)
            ax.spines[['top','right','left','bottom']].set_visible(False)
            ax.tick_params(axis='y', length=0, pad=15)
            ax.tick_params(axis='x', direction='in', length=10, color='dimgrey', pad=15)

            h, l = ax.get_legend_handles_labels()     
            if include_outages:
                colorcode = {'Planned': 'b', 'Forced': 'r'} # Colorcode: red: forced, blue: planned
                units = ['Kernkraftwerk Gösgen', 'Leibstadt', 'KKM Produktion', 'Beznau 1', 'Beznau 2']
                markers = {k:v for k,v in zip(units,['$G$', '$L$', '$M$', '$B_1$', '$B_2$'])}
                order = {'Planned': 30, 'Forced': 31}
                history = dict()
                planned_legend, forced_legend = False, False
                for i, outage in data_out.iterrows():
                    x1 = outage['StartDate']
                    x2 = outage['StartTime'][:2]
                    start_day = data[data['Date'] == x1]
                    if start_day.empty:
                        continue
                    start_idx = start_day[start_day['Time'].str[:2] == x2].index[0]
                    if start_idx == 0:
                        continue
                    check_idx = [j for j in  history if j in [start_idx-k for k in range(0, 5*24)]] # To check for weak duplicates
                    if check_idx:
                        history.update({start_idx: outage['UnitName']})
                        if outage['UnitName'] in [history[k] for k in check_idx]:
                            history.update({start_idx: outage['UnitName']})
                            continue
                    else:
                        history.update({start_idx: outage['UnitName']})
                    if not planned_legend:
                        if outage['Type'] == 'Planned':
                            h.append(mlines.Line2D([], [], color=colorcode[outage['Type']], marker=markers[outage['UnitName']], linestyle='None', markersize=15, label='Geplannte Abschaltung'))
                            l.append('Geplannte Abschaltung')
                            planned_legend = True
                    if not forced_legend:
                        if outage['Type'] == 'Forced':
                            h.append(mlines.Line2D([], [], color=colorcode[outage['Type']], marker=markers[outage['UnitName']], linestyle='None', markersize=15, label='Erzwungene Abschaltung'))
                            l.append('Erzwungene Abschaltung')
                            forced_legend = True

                    idx = units.index(outage['UnitName'])
                    x = start_idx
                    y = np.sum(np.array([data[units[unit]][x] for unit in range(idx+1)]), axis=0)
                    
                    plt.scatter(x, y, c=colorcode[outage['Type']], marker=markers[outage['UnitName']], s=120, zorder=order[outage['Type']], clip_on=False)

                h.append(mlines.Line2D([], [], linestyle='None'))
                l.append('$G$ - Gösgen, $L$ - Leibstadt, $M$ - Mühleberg, $B_{1/2}$ - Beznau 1/2')
                for _ in range(2 - sum([planned_legend, forced_legend])):  
                    h.append(mlines.Line2D([], [], linestyle='None'))
                    l.append(' ')
                if 2 - sum([planned_legend, forced_legend]) == 0: # planned and forced included
                    handles = [h[0], h[3], h[6], h[1], h[4], h[7], h[2], h[5], h[8], h[9], h[10], h[11]]
                    labels = [l[0], l[3], l[6], l[1], l[4], l[7], l[2], l[5], l[8], l[9], l[10], l[11]]
                    leg = plt.legend(handles, labels, loc=9, bbox_to_anchor=(0.5,0.99), ncol=(len(handles)+1)//3, frameon=False, columnspacing=4)
                    leg.set_zorder(35)
                    texts = leg.get_texts()
                    texts[-1]._fontproperties = texts[1]._fontproperties.copy()
                    texts[-1].set_size(13)
                elif 2 - sum([planned_legend, forced_legend]) == 1: # only one of both included
                    handles = [h[0], h[3], h[6], h[1], h[4], h[7], h[2], h[5], h[8], h[9], h[10], h[11]]
                    labels = [l[0], l[3], l[6], l[1], l[4], l[7], l[2], l[5], l[8], l[9], l[10], l[11]]
                    leg = plt.legend(handles, labels, loc=9, bbox_to_anchor=(0.5,0.99), ncol=(len(handles)+1)//3, frameon=False, columnspacing=4)
                    leg.set_zorder(35)
                    texts = leg.get_texts()
                    texts[-2]._fontproperties = texts[1]._fontproperties.copy()
                    texts[-2].set_size(13)
                else:
                    handles = [h[0], h[3], h[6], h[1], h[4], h[7], h[2], h[5], h[8]]
                    labels = [l[0], l[3], l[6], l[1], l[4], l[7], l[2], l[5], l[8]]
                    leg = plt.legend(handles, labels, loc=9, bbox_to_anchor=(0.5,0.99), ncol=(len(handles)+1)//3, frameon=False, columnspacing=4)
                    leg.set_zorder(35)                               
            else:
                # handles = [h[0], h[5], h[1], h[6], h[2], h[7], h[3], h[8], h[4]]
                # labels = [l[0], l[5], l[1], l[6], l[2], l[7], l[3], l[8], l[4]]
                # plt.legend(handles, labels, loc=9, bbox_to_anchor=(0.5,0.99), ncol=(len(handles)+1)//2, frameon=False, columnspacing=3).set_zorder(35)
                plt.legend(loc=9, bbox_to_anchor=(0.5,0.99), ncol=5, frameon=False, columnspacing=3).set_zorder(35)

        elif year >= 2020: # exclude KKM
            y = np.array([data['Kernkraftwerk Gösgen'], data['Leibstadt'], data['Beznau 1'], data['Beznau 2'], rest, data['Import'], data['Export']])
            stack_max = max(np.sum(y, axis=0))

            plt.stackplot(range(0,len(data.index)), y, colors=color_map, labels=labels_de, zorder=10)
            plt.plot(data['TotalLoadValue'], color='k', linewidth=2, label='Last', zorder=20)

            plt.title(f'Nettostromerzeugung in der Schweiz im {get_month(month)} {year}', fontsize=34)

            plt.xticks([i for i in range(len(data.index)) if i%24 == 0], ticks[::24])
            for i, label in enumerate(ax.xaxis.get_ticklabels()):
                if (i+2)%5 != 0:
                    label.set_visible(False)
            plt.xlim(0,len(data.index)-1)

            plt.yticks(range(0, int(1.2*stack_max), 2500))
            plt.ylim(0, min(1.2*stack_max, 20000))
            plt.ylabel('Leistung [MW]')

            plt.grid(axis='y', alpha=0.4, zorder=0)
            ax.spines[['top','right','left','bottom']].set_visible(False)
            ax.tick_params(axis='y', length=0, pad=15)
            ax.tick_params(axis='x', direction='in', length=10, color='dimgrey', pad=15)

            h, l = ax.get_legend_handles_labels()
            if include_outages:
                colorcode = {'Planned': 'b', 'Forced': 'r'} # Colorcode: red: forced, blue: planned
                units = ['Kernkraftwerk Gösgen', 'Leibstadt', 'Beznau 1', 'Beznau 2']
                markers = {k:v for k,v in zip(units,['$G$', '$L$', '$B_1$', '$B_2$'])}
                order = {'Planned': 30, 'Forced': 31}
                history = dict()
                planned_legend, forced_legend = False, False
                for i, outage in data_out.iterrows():
                    x1 = outage['StartDate']
                    x2 = outage['StartTime'][:2]
                    start_day = data[data['Date'] == x1]
                    if start_day.empty:
                        continue
                    start_idx = start_day[start_day['Time'].str[:2] == x2].index[0]
                    if start_idx == 0:
                        continue
                    check_idx = [j for j in  history if j in [start_idx-k for k in range(0, 5*24)]] # To check for weak duplicates
                    if check_idx:
                        history.update({start_idx: outage['UnitName']})
                        if outage['UnitName'] in [history[k] for k in check_idx]:
                            history.update({start_idx: outage['UnitName']})
                            continue
                    else:
                        history.update({start_idx: outage['UnitName']})
                    if not planned_legend:
                        if outage['Type'] == 'Planned':
                            h.append(mlines.Line2D([], [], color=colorcode[outage['Type']], marker=markers[outage['UnitName']], linestyle='None', markersize=15, label='Geplannte Abschaltung'))
                            l.append('Geplannte Abschaltung')
                            planned_legend = True
                    if not forced_legend:
                        if outage['Type'] == 'Forced':
                            h.append(mlines.Line2D([], [], color=colorcode[outage['Type']], marker=markers[outage['UnitName']], linestyle='None', markersize=15, label='Erzwungene Abschaltung'))
                            l.append('Erzwungene Abschaltung')
                            forced_legend = True

                    idx = units.index(outage['UnitName'])
                    x = start_idx
                    y = np.sum(np.array([data[units[unit]][x] for unit in range(idx+1)]), axis=0)
                    
                    plt.scatter(x, y, c=colorcode[outage['Type']], marker=markers[outage['UnitName']], s=120, zorder=order[outage['Type']], clip_on=False)

                h.append(mlines.Line2D([], [], linestyle='None'))
                l.append('$G$ - Gösgen, $L$ - Leibstadt, $B_{1/2}$ - Beznau 1/2')
                if 2 - sum([planned_legend, forced_legend]) == 0: # planned and forced included
                    h.append(mlines.Line2D([], [], linestyle='None'))
                    l.append(' ')
                    handles = [h[0], h[1], h[5], h[2], h[3], h[6], h[4], h[7], h[11], h[8], h[9], h[10]]
                    labels = [l[0], l[1], l[5], l[2], l[3], l[6], l[4], l[7], l[11], l[8], l[9], l[10]]
                    leg = plt.legend(handles, labels, loc=9, bbox_to_anchor=(0.5,0.99), ncol=(len(handles)+1)//3, frameon=False, columnspacing=5)
                    leg.set_zorder(35)
                    texts = leg.get_texts()
                    texts[-1]._fontproperties = texts[1]._fontproperties.copy()
                    texts[-1].set_size(13)
                elif 2 - sum([planned_legend, forced_legend]) == 1: # only one of both included
                    handles = [h[0], h[2], h[1], h[3], h[5], h[4], h[6], h[7], h[8], h[9]]
                    labels = [l[0], l[2], l[1], l[3], l[5], l[4], l[6], l[7], l[8], l[9]]
                    leg = plt.legend(handles, labels, loc=9, bbox_to_anchor=(0.5,0.99), ncol=(len(handles)+1)//2, frameon=False, columnspacing=3)
                    leg.set_zorder(35)
                    texts = leg.get_texts()
                    texts[-1]._fontproperties = texts[1]._fontproperties.copy()
                    texts[-1].set_size(13)
                else:
                    handles = [h[0], h[2], h[1], h[3], h[5], h[4], h[6], h[7]]
                    labels = [l[0], l[2], l[1], l[3], l[5], l[4], l[6], l[7]]
                    leg = plt.legend(handles, labels, loc=9, bbox_to_anchor=(0.5,0.99), ncol=(len(handles)+1)//2, frameon=False, columnspacing=3)
                    leg.set_zorder(35)                             
            else:
                # handles = [h[0], h[4], h[1], h[5], h[2], h[6], h[3], h[7]]
                # labels = [l[0], l[4], l[1], l[5], l[2], l[6], l[3], l[7]]
                # plt.legend(handles, labels, loc=9, bbox_to_anchor=(0.5,0.99), ncol=(len(handles)+1)//2, frameon=False, columnspacing=5).set_zorder(35)
                plt.legend(loc=9, bbox_to_anchor=(0.5,0.99), ncol=5, frameon=False, columnspacing=3).set_zorder(35)               

        plt.annotate(r'$\copyright$'+f' swissnuclear, {datetime.today().year}. Datenquelle: Entso-E', xycoords='figure fraction', xy=(0.70,0.03), fontsize=10)

        imgax = fig_m.add_axes([0.8, 0.94, 0.1, 0.1], anchor='SE')
        imgax.imshow(logo)
        imgax.axis('off')

        if show_plot:
            plt.show()
        if save_plot:
            fname_m = os.path.join('plots','month',f'{year}_{month:02d}_overview.png')
            fig_m.savefig(fname_m, dpi='figure', bbox_inches='tight', metadata={'Copyright':f'Swissnuclear, {today.year}', 'Author':'Yanis S.', 'Disclaimer':'Only allowed for private use. Contact Swissnuclear for more information.'})

        ################
        ### per year ###
        ################
        if today.month == 1:
            data_list = []
            year = today.year-1
            path_gen = os.path.join('generation', str(year))
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

            fig_y = plt.figure(figsize=(20,10), dpi=80)
            ax = plt.gca()

            if year < 2020: # include KKM
                y = np.array([data['Kernkraftwerk Gösgen'], data['Leibstadt'], data['KKM Produktion'], data['Beznau 1'], data['Beznau 2'], rest, data['Import'], data['Export']])
                stack_max = max(np.sum(y, axis=0))

                plt.stackplot(range(0,len(data.index)), y, colors=color_map, labels=labels_de, zorder=10)
                plt.plot(data['TotalLoadValue'], color='k', linewidth=1, label='Last', zorder=20)

                plt.title(f'Nettostromerzeugung in der Schweiz im Jahr {year}', fontsize=34)

                plt.xticks([i for i in range(len(data.index)) if i%24 == 0], [month_short[tick[3:5]] for tick in ticks[::24]], ha='left')
                ticklabels = [label.get_text() for label in ax.xaxis.get_ticklabels()]
                set_vis_idx = [ticklabels.index(m) for m in month_short.values()]
                for i, label in enumerate(ax.xaxis.get_ticklabels()):
                    if i not in set_vis_idx:
                        label.set_visible(False)
                plt.xlim(0,len(data.index)-1)

                plt.yticks(range(0, int(1.2*stack_max), 2500))
                plt.ylim(0, min(1.2*stack_max, 20000))
                plt.ylabel('Leistung [MW]')

                plt.grid(axis='y', alpha=0.4, zorder=0)
                ax.spines[['top','right','left','bottom']].set_visible(False)
                ax.tick_params(axis='y', length=0, pad=15)
                ax.tick_params(axis='x', direction='in', length=0, color='dimgrey', pad=15)

                h, l = ax.get_legend_handles_labels()
                if include_outages:
                    colorcode = {'Planned': 'b', 'Forced': 'r'} # Colorcode: red: forced, blue: planned
                    units = ['Kernkraftwerk Gösgen', 'Leibstadt', 'KKM Produktion', 'Beznau 1', 'Beznau 2']
                    markers = {k:v for k,v in zip(units,['$G$', '$L$', '$M$', '$B_1$', '$B_2$'])}
                    order = {'Planned': 30, 'Forced': 31}
                    history = dict()
                    planned_legend, forced_legend = False, False
                    for i, outage in data_out.iterrows():
                        x1 = outage['StartDate']
                        x2 = outage['StartTime'][:2]
                        start_day = data[data['Date'] == x1]
                        start_idx = start_day[start_day['Time'].str[:2] == x2].index[0]
                        if start_idx == 0:
                            continue
                        check_idx = [j for j in  history if j in [start_idx-k for k in range(0, 5*24)]] # To check for weak duplicates
                        if check_idx:
                            history.update({start_idx: outage['UnitName']})
                            if outage['UnitName'] in [history[k] for k in check_idx]:
                                history.update({start_idx: outage['UnitName']})
                                continue
                        else:
                            history.update({start_idx: outage['UnitName']})
                        if not planned_legend:
                            if outage['Type'] == 'Planned':
                                h.append(mlines.Line2D([], [], color=colorcode[outage['Type']], marker=markers[outage['UnitName']], linestyle='None', markersize=15, label='Geplannte Abschaltung'))
                                l.append('Geplannte Abschaltung')
                                planned_legend = True
                        if not forced_legend:
                            if outage['Type'] == 'Forced':
                                h.append(mlines.Line2D([], [], color=colorcode[outage['Type']], marker=markers[outage['UnitName']], linestyle='None', markersize=15, label='Erzwungene Abschaltung'))
                                l.append('Erzwungene Abschaltung')
                                forced_legend = True

                        idx = units.index(outage['UnitName'])
                        x = start_idx
                        y = np.sum(np.array([data[units[unit]][x] for unit in range(idx+1)]), axis=0)
                        
                        plt.scatter(x, y, c=colorcode[outage['Type']], marker=markers[outage['UnitName']], s=120, zorder=order[outage['Type']], clip_on=False)
                        
                    h.append(mlines.Line2D([], [], linestyle='None'))
                    l.append('$G$ - Gösgen, $L$ - Leibstadt, $M$ - Mühleberg, $B_{1/2}$ - Beznau 1/2')
                    for _ in range(2 - sum([planned_legend, forced_legend])):
                        h.append(mlines.Line2D([], [], linestyle='None'))
                        l.append(' ')
                    if 2 - sum([planned_legend, forced_legend]) == 0: # planned and forced included
                        handles = [h[0], h[3], h[6], h[1], h[4], h[7], h[2], h[5], h[8], h[9], h[10], h[11]]
                        labels = [l[0], l[3], l[6], l[1], l[4], l[7], l[2], l[5], l[8], l[9], l[10], l[11]]
                        leg = plt.legend(handles, labels, loc=9, bbox_to_anchor=(0.5,0.99), ncol=(len(handles)+1)//3, frameon=False, columnspacing=4)
                        leg.set_zorder(35)
                        texts = leg.get_texts()
                        texts[-1]._fontproperties = texts[1]._fontproperties.copy()
                        texts[-1].set_size(13)
                    elif 2 - sum([planned_legend, forced_legend]) == 1: # only one of both included
                        handles = [h[0], h[3], h[6], h[1], h[4], h[7], h[2], h[5], h[8], h[9], h[10], h[11]]
                        labels = [l[0], l[3], l[6], l[1], l[4], l[7], l[2], l[5], l[8], l[9], l[10], l[11]]
                        leg = plt.legend(handles, labels, loc=9, bbox_to_anchor=(0.5,0.99), ncol=(len(handles)+1)//3, frameon=False, columnspacing=4)
                        leg.set_zorder(35)
                        texts = leg.get_texts()
                        texts[-2]._fontproperties = texts[1]._fontproperties.copy()
                        texts[-2].set_size(13)
                    else:
                        handles = [h[0], h[3], h[6], h[1], h[4], h[7], h[2], h[5], h[8]]
                        labels = [l[0], l[3], l[6], l[1], l[4], l[7], l[2], l[5], l[8]]
                        leg = plt.legend(handles, labels, loc=9, bbox_to_anchor=(0.5,0.99), ncol=(len(handles)+1)//3, frameon=False, columnspacing=4)
                        leg.set_zorder(35)                              
                else:
                    # handles = [h[0], h[5], h[1], h[6], h[2], h[7], h[3], h[8], h[4]]
                    # labels = [l[0], l[5], l[1], l[6], l[2], l[7], l[3], l[8], l[4]]
                    # plt.legend(handles, labels, loc=9, bbox_to_anchor=(0.5,0.99), ncol=(len(handles)+1)//2, frameon=False, columnspacing=3).set_zorder(35)
                    plt.legend(loc=9, bbox_to_anchor=(0.5,0.99), ncol=5, frameon=False, columnspacing=3).set_zorder(35)

            elif year >= 2020:
                y = np.array([data['Kernkraftwerk Gösgen'], data['Leibstadt'], data['Beznau 1'], data['Beznau 2'], rest, data['Import'], data['Export']])
                stack_max = max(np.sum(y, axis=0))

                plt.stackplot(range(0,len(data.index)), y, colors=color_map, labels=labels_de, zorder=10)
                plt.plot(data['TotalLoadValue'], color='k', linewidth=1, label='Last', zorder=20)

                plt.title(f'Nettostromerzeugung in der Schweiz im Jahr {year}', fontsize=34)

                plt.xticks([i for i in range(len(data.index)) if i%24 == 0], [month_short[tick[3:5]] for tick in ticks[::24]], ha='left')
                ticklabels = [label.get_text() for label in ax.xaxis.get_ticklabels()]
                set_vis_idx = [ticklabels.index(m) for m in month_short.values()]
                for i, label in enumerate(ax.xaxis.get_ticklabels()):
                    if i not in set_vis_idx:
                        label.set_visible(False)
                plt.xlim(0,len(data.index)-1)

                plt.yticks(range(0, int(1.2*stack_max), 2500))
                plt.ylim(0, min(1.2*stack_max, 20000))
                plt.ylabel('Leistung [MW]')

                plt.grid(axis='y', alpha=0.4, zorder=0)
                ax.spines[['top','right','left','bottom']].set_visible(False)
                ax.tick_params(axis='y', length=0, pad=15)
                ax.tick_params(axis='x', direction='in', length=0, color='dimgrey', pad=15)

                h, l = ax.get_legend_handles_labels()
                if include_outages:
                    colorcode = {'Planned': 'b', 'Forced': 'r'} # Colorcode: red: forced, blue: planned
                    units = ['Kernkraftwerk Gösgen', 'Leibstadt', 'Beznau 1', 'Beznau 2']
                    markers = {k:v for k,v in zip(units,['$G$', '$L$', '$B_1$', '$B_2$'])}
                    order = {'Planned': 30, 'Forced': 31}
                    history = dict()
                    planned_legend, forced_legend = False, False
                    for i, outage in data_out.iterrows():
                        x1 = outage['StartDate']
                        x2 = outage['StartTime'][:2]
                        start_day = data[data['Date'] == x1]
                        start_idx = start_day[start_day['Time'].str[:2] == x2].index[0]
                        if start_idx == 0:
                            continue
                        check_idx = [j for j in  history if j in [start_idx-k for k in range(0, 5*24)]] # To check for weak duplicates
                        if check_idx:
                            history.update({start_idx: outage['UnitName']})
                            if outage['UnitName'] in [history[k] for k in check_idx]:
                                history.update({start_idx: outage['UnitName']})
                                continue
                        else:
                            history.update({start_idx: outage['UnitName']})
                        if not planned_legend:
                            if outage['Type'] == 'Planned':
                                h.append(mlines.Line2D([], [], color=colorcode[outage['Type']], marker=markers[outage['UnitName']], linestyle='None', markersize=15, label='Geplannte Abschaltung'))
                                l.append('Geplannte Abschaltung')
                                planned_legend = True
                        if not forced_legend:
                            if outage['Type'] == 'Forced':
                                h.append(mlines.Line2D([], [], color=colorcode[outage['Type']], marker=markers[outage['UnitName']], linestyle='None', markersize=15, label='Erzwungene Abschaltung'))
                                l.append('Erzwungene Abschaltung')
                                forced_legend = True

                        idx = units.index(outage['UnitName'])
                        x = start_idx
                        y = np.sum(np.array([data[units[unit]][x] for unit in range(idx+1)]), axis=0)
                        
                        plt.scatter(x, y, c=colorcode[outage['Type']], marker=markers[outage['UnitName']], s=120, zorder=order[outage['Type']], clip_on=False)
                        
                    h.append(mlines.Line2D([], [], linestyle='None'))
                    l.append('$G$ - Gösgen, $L$ - Leibstadt, $B_{1/2}$ - Beznau 1/2')
                    if 2 - sum([planned_legend, forced_legend]) == 0: # planned and forced included
                        h.append(mlines.Line2D([], [], linestyle='None'))
                        l.append(' ')
                        handles = [h[0], h[1], h[5], h[2], h[3], h[6], h[4], h[7], h[11], h[8], h[9], h[10]]
                        labels = [l[0], l[1], l[5], l[2], l[3], l[6], l[4], l[7], l[11], l[8], l[9], l[10]]
                        leg = plt.legend(handles, labels, loc=9, bbox_to_anchor=(0.5,0.99), ncol=(len(handles)+1)//3, frameon=False, columnspacing=5)
                        leg.set_zorder(35)
                        texts = leg.get_texts()
                        texts[-1]._fontproperties = texts[1]._fontproperties.copy()
                        texts[-1].set_size(13)
                    elif 2 - sum([planned_legend, forced_legend]) == 1: # only one of both included
                        handles = [h[0], h[2], h[1], h[3], h[5], h[4], h[6], h[7], h[8], h[9]]
                        labels = [l[0], l[2], l[1], l[3], l[5], l[4], l[6], l[7], l[8], l[9]]
                        leg = plt.legend(handles, labels, loc=9, bbox_to_anchor=(0.5,0.99), ncol=(len(handles)+1)//2, frameon=False, columnspacing=3)
                        leg.set_zorder(35)
                        texts = leg.get_texts()
                        texts[-1]._fontproperties = texts[1]._fontproperties.copy()
                        texts[-1].set_size(13)
                    else:
                        handles = [h[0], h[2], h[1], h[3], h[5], h[4], h[6], h[7]]
                        labels = [l[0], l[2], l[1], l[3], l[5], l[4], l[6], l[7]]
                        leg = plt.legend(handles, labels, loc=9, bbox_to_anchor=(0.5,0.99), ncol=(len(handles)+1)//2, frameon=False, columnspacing=3)
                        leg.set_zorder(35)                               
                else:
                    # handles = [h[0], h[4], h[1], h[5], h[2], h[6], h[3], h[7]]
                    # labels = [l[0], l[4], l[1], l[5], l[2], l[6], l[3], l[7]]
                    # plt.legend(handles, labels, loc=9, bbox_to_anchor=(0.5,0.99), ncol=(len(handles)+1)//2, frameon=False, columnspacing=5).set_zorder(35)
                    plt.legend(loc=9, bbox_to_anchor=(0.5,0.99), ncol=5, frameon=False, columnspacing=3).set_zorder(35)

            plt.annotate(r'$\copyright$'+f' swissnuclear, {datetime.today().year}. Datenquelle: Entso-E', xycoords='figure fraction', xy=(0.70,0.03), fontsize=10)

            imgax = fig_y.add_axes([0.8, 0.94, 0.1, 0.1], anchor='SE')
            imgax.imshow(logo)
            imgax.axis('off')

            if show_plot:
                plt.show()
            if save_plot:
                fname_y = os.path.join('plots','year',f'{year}_overview.png')
                fig_y.savefig(fname_y, dpi='figure', bbox_inches='tight', metadata={'Copyright':f'Swissnuclear, {today.year}', 'Author':'Yanis S.', 'Disclaimer':'Only allowed for private use. Contact Swissnuclear for more information.'})

    print('\nDone')

            
if __name__ == '__main__':
    main()