import os
import pickle
import pandas as pd; pd.options.mode.chained_assignment = None
from datetime import datetime, date
import ipywidgets as widgets
#from ipywidgets import AppLayout, Button, Text, Select, Tab, Layout, VBox, HBox, Label, HTML, interact, interact_manual, interactive, IntSlider, Output
from bokeh.models import Span
from IPython.display import display
import dmyplant2 as dmp2
from App.common import loading_bar, V, tabs_out

#########################################
# tab6 - playground
#########################################
class Tab():
    def __init__(self):

        self.title = '6. Run2/4 Results'
        self.dfigsize = V.dfigsize
        self.tab6_out = widgets.Output()

        self.cb_loadcap = widgets.Checkbox(
            value=True,
            description='forget starts with power below',
            disabled=False,
            indent=False,
            layout=widgets.Layout(max_width='320px')
        )

        self.t_loadcap = widgets.IntText(
            #description='%:',
            value=95,
            layout=widgets.Layout(max_width='120px')
        )

        self.t_loadcaplabel = widgets.Label(
            value="%"
        )
        
        self.cb_spreadcap = widgets.Checkbox(
            value=False,
            description='forget starts with Exhaust spread below',
            disabled=False,
            indent=False,
            layout=widgets.Layout(max_width='320px')
        )

        self.t_spreadcap = widgets.IntText(
            #description='%:',
            value=80,
            layout=widgets.Layout(max_width='120px')
        )

        self.t_spreadcaplabel = widgets.Label(
            value="°C"
        )

        self.b_tecjet = widgets.Button(
            description='TecJet Results',
            disabled=False,
            button_style='primary',
            tooltip='Show TecJet Results collected in Run2',
        )
        self.b_tecjet.on_click(self.show_tecjet)

        self.b_exhaust = widgets.Button(
            description='Exh Temp Results',
            disabled=False,
            button_style='primary',
            tooltip='Show Exhaust Temp Results collected in Run2',
        )
        self.b_exhaust.on_click(self.show_temp)

        self.b_sync = widgets.Button(
            description='Sync Results',
            disabled=False,
            button_style='primary',
            tooltip='Show Snchronization Results collected in Run2',
        )
        self.b_sync.on_click(self.show_sync)

        self.b_oil = widgets.Button(
            description='Oil Circuit Results',
            disabled=False,
            button_style='primary',
            tooltip='Show Oil Circuit measurements at start Results collected in Run2',
        )
        self.b_oil.on_click(self.show_oil)

        self.b_stop = widgets.Button(
            description='Stop Results',
            disabled=False,
            button_style='primary',
            tooltip='Show Stop Results collected in Run4',
        )
        self.b_stop.on_click(self.show_stop)

    @property
    def tab(self):
        return widgets.VBox([
            widgets.HBox([self.cb_loadcap, self.t_loadcap, self.t_loadcaplabel]),
            widgets.HBox([self.cb_spreadcap, self.t_spreadcap, self.t_spreadcaplabel]),
            widgets.HBox([self.b_tecjet,self.b_exhaust,self.b_sync,self.b_oil,self.b_stop]),
            self.tab6_out],
            layout=widgets.Layout(min_height=V.hh))

    def selected(self):
        with tabs_out:
            tabs_out.clear_output()
            print('tab6')

    def cleartab(self):
        self.tab6_out.clear_output() 

    def show_tecjet(self,b): # tecjet callback
        with self.tab6_out:
            self.tab6_out.clear_output()
            if ((V.fsm is not None) and V.fsm.starts.iloc[0]['run2']):
                rda = V.fsm.starts.reset_index(drop='index')
                thefilter = (
                    (rda['mode'].isin(V.modes_value)) & 
                    (rda['success'].isin(V.succ_value)) & 
                    ((rda['W'] > 0) | ('Warnings' not in V.alarm_warning_value)) & 
                    ((rda['A'] > 0) | ('Alarms' not in V.alarm_warning_value))
                )
                rda = rda[thefilter].reset_index(drop='index')
                #rdb = rda
                rde = rda #.fillna('')
                if not rde.empty:
                    rde['datetime'] = pd.to_datetime(rde['starttime'])
                    dr2set2 = [
                    {'col':['maxload','targetload'],'ylim': [4200, 5000], 'color':['FireBrick','red'], 'unit':'kW'},
                    {'col':['TJ_GasDiffPressMin'],'ylim': [0, 100], 'color':'orange', 'unit':'mbar'},
                    {'col':['TJ_Pos_at_Min'],'ylim': [0, 100], 'color':'purple', 'unit':'°C'},
                    {'col':['TJ_GasPress1_at_Min'],'ylim': [700, 1200], 'color':'brown', 'unit':'mbar'},
                    {'col':['TJ_GasTemp1_at_Min'],'ylim': [0, 100], 'color':'dodgerblue', 'unit':'°C'},
                    {'col':['TJ_Lambda_min','TJ_Lambda_max'],'ylim': [0, 3], 'color':'rgba(255,165,0,0.4)', 'unit':'-'},
                    {'col':['no'],'_ylim':(0,1000), 'color':['rgba(0,0,0,0.05)'] },
                    ]
                    
                    #Checken, ob run2 Resultate im den Daten vorhanden sind und dr2set2 entsprechend anpassen
                    dr2set2_c = [r for r in dr2set2 if all(res in list(V.fsm.starts.columns) for res in r['col'])]
 
                    dr2set2 = dmp2.equal_adjust(dr2set2_c, rde, do_not_adjust=['no'], minfactor=0.95, maxfactor=1.2)
                    ftitle = f"{V.fsm._e}"
                    fig2 = dmp2.dbokeh_chart(rde, dr2set2, style='both', figsize=self.dfigsize ,title=ftitle);
                    dmp2.bokeh_show(fig2)

                    print()
                    print('Figures below are filtered by targetload & Spread:')
                    print()
                    if self.cb_loadcap.value:
                        rde = rde[rde['targetload'] > self.t_loadcap.value / 100 * V.fsm._e['Power_PowerNominal']]
                    if self.cb_spreadcap.value:
                        rde = rde[rde['ExSpread@Spread'] > self.t_spreadcap.value]

                    rde['bmep'] = rde.apply(lambda x: V.fsm._e._calc_BMEP(x['targetload'], V.fsm._e.Speed_nominal), axis=1)
                    rde['bmep2'] = rde.apply(lambda x: V.fsm._e._calc_BMEP(x['maxload'], V.fsm._e.Speed_nominal), axis=1)
                    dr2set2 = [
                            #{'col':['targetload'],'ylim': [4100, 4700], 'color':'red', 'unit':'kW'},
                            {'col':['bmep2','bmep'],'ylim': [20, 30], 'color':['FireBrick','red'], 'unit':'bar'},
                            {'col':['TJ_GasDiffPressMin'],'ylim': [-20, 80], 'color':'blue', 'unit':'mbar'},
                            {'col':['TJ_Pos_at_Min'],'ylim': [0, 600], 'color':'purple', 'unit':'%'},
                            #{'col':['TJ_GasPress1_at_Min'],'ylim': [800, 1300], 'color':'dodgerblue', 'unit':'mbar'},
                            #{'col':['TJ_GasTemp1_at_Min'],'ylim': [0, 100], 'color':'red', 'unit':'°C'},
                            {'col':['no'],'_ylim':(0,1000), 'color':['rgba(0,0,0,0.05)'] },
                            ]
                    try:
                        dr2set2 = dmp2.equal_adjust(dr2set2, rde, do_not_adjust=['no'], minfactor=1.0, maxfactor=1.1)
                    except Exception as err:
                        print(f'Error: {str(err)}')
                    ntitle = ftitle + ' | BMEP at Start vs TJ Gas Temperature in °C '
                    fig3 = dmp2.dbokeh_chart(rde, dr2set2, x='TJ_GasTemp1_at_Min', style='circle', figsize=self.dfigsize ,title=ntitle);
                    fig3.add_layout(Span(location=V.fsm._e.BMEP,
                            dimension='width',x_range_name='default', y_range_name='0',line_color='red', line_dash='dashed', line_alpha=0.6))
                    fig3.add_layout(Span(location=20.0,
                            dimension='width',x_range_name='default', y_range_name='1',line_color='blue', line_dash='dashed', line_alpha=0.6))

                    dmp2.bokeh_show(fig3)
                    
                    dr2set2 = [
                            {'col':['targetload'],'ylim': [4100, 4700], 'color':'red', 'unit':'kW'},
                            {'col':['bmep2','bmep'],'ylim': [20, 30], 'color':['FireBrick','red'], 'unit':'bar'},
                            {'col':['TJ_Lambda_min','TJ_Lambda_max'],'ylim': [0, 4], 'color':'rgba(255,165,0,0.4)', 'unit':'-'},
                            {'col':['TJ_Pos_at_Min'],'ylim': [0, 600], 'color':'purple', 'unit':'%'},
                            #{'col':['TJ_GasPress1_at_Min'],'ylim': [800, 1300], 'color':'dodgerblue', 'unit':'mbar'},
                            {'col':['TJ_GasTemp1_at_Min'],'ylim': [0, 100], 'color':'dodgerblue', 'unit':'°C'},
                            {'col':['no'],'_ylim':(0,1000), 'color':['rgba(0,0,0,0.05)'] },
                            ]
                    try:
                        #Check, ob run2 Resultate im den Daten vorhanden sind und dr2set2 entsprechend anpassen
                        dr2set2_c = [r for r in dr2set2 if all(res in list(V.fsm.starts.columns) for res in r['col'])]
                        dr2set2 = dmp2.equal_adjust(dr2set2_c, rde, do_not_adjust=['no'], minfactor=1.0, maxfactor=1.1)
                    except Exception as err:
                        print(f'Error: {str(err)}')
                        
                    ntitle = ftitle + ' | BMEP at Start vs TJ TJ_GasDiffPressMin in mbar '
                    fig3 = dmp2.dbokeh_chart(rde, dr2set2, x='TJ_GasDiffPressMin', style='circle', figsize=self.dfigsize ,title=ntitle);
                    fig3.add_layout(Span(location=V.fsm._e.BMEP,
                            dimension='width',x_range_name='default', y_range_name='0',line_color='red', line_dash='dashed', line_alpha=0.6))
                    #fig3.add_layout(Span(location=20.0,
                    #        dimension='width',x_range_name='default', y_range_name='1',line_color='blue', line_dash='dashed', line_alpha=0.6))

                    dmp2.bokeh_show(fig3)            
                    
                print()
                display(rde[V.fsm.results['run2_content']['tecjet']].describe().style.format(precision=2, na_rep='-'))                
                print()
                display(rde[V.fsm.results['run2_content']['tecjet']][::-1].style.format(precision=2,na_rep='-').hide())
            else:
                print('No Data available.')
    
    def show_temp(self,b): # exhaust callback
        with self.tab6_out:
            self.tab6_out.clear_output()
            if ((V.fsm is not None) and V.fsm.starts.iloc[0]['run2']):
                rda = V.fsm.starts.reset_index(drop='index')
                thefilter = (
                    (rda['mode'].isin(V.modes_value)) & 
                    (rda['success'].isin(V.succ_value)) & 
                    ((rda['W'] > 0) | ('Warnings' not in V.alarm_warning_value)) & 
                    ((rda['A'] > 0) | ('Alarms' not in V.alarm_warning_value))
                )
                rda = rda[thefilter].reset_index(drop='index')
                #rdb = rda
                rde = rda #.fillna('')
                if not rde.empty:
                    rde['datetime'] = pd.to_datetime(rde['starttime'])
                    
                    print()
                    print('Figures below are filtered by targetload & Spread:')
                    print()
                    if self.cb_loadcap.value:
                        rde = rde[rde['targetload'] > self.t_loadcap.value / 100 * V.fsm._e['Power_PowerNominal']]
                    if self.cb_spreadcap.value:
                        rde = rde[rde['ExSpread@Spread'] > self.t_spreadcap.value]

                    ntitle = f"{V.fsm._e}" + ' | Exhaust Temperture at Start, Max, Min & Spread (@ Max Spread)'
                    if self.cb_loadcap.value:
                        rde = rde[rde['targetload'] > self.t_loadcap.value / 100 * V.fsm._e['Power_PowerNominal']]
                    dr2set4 = [
                            {'col':['ExSpread@Spread'],'_ylim': [0, 100], 'color':['dodgerblue'], 'unit':'°C'},
                            {'col':['ExSpread@MaxTemp','ExSpread@MinTemp'],'_ylim': [4200, 4800], 'color':['FireBrick','Crimson'], 'unit':'°C'},
                            {'col':['ExSpread@MaxPos','ExSpread@MinPos'],'_ylim': [1, 24], 'color':['Thistle','Plum'], 'unit':'-'},
                            {'col':['ExSpread@PWR'],'_ylim': [0, 100], 'color':['red'], 'unit':'kW'},
                            {'col':['synchronize'],'_ylim':(-20,400), 'color':'brown', 'unit':'sec'},
                            {'col':['W','A','isuccess'],'_ylim':(-1,200), 'color':['rgba(255,165,0,0.3)','rgba(255,0,0,0.3)','rgba(0,128,0,0.2)'] , 'unit':'-' },
                            #{'col':['startpreparation'],'_ylim':(-1000,800), 'unit':'sec'},
                            {'col':['no'],'_ylim':(0,1000), 'color':['rgba(0,0,0,0.05)'] },
                            ]
                    dr2set4 = dmp2.equal_adjust(dr2set4, rde, do_not_adjust=[5], minfactor=0.95, maxfactor=1.2)
                    fig5 = dmp2.dbokeh_chart(rde, dr2set4, style='both', figsize=self.dfigsize ,title=ntitle);
                    dmp2.bokeh_show(fig5)

                    print()
                    ntitle = f"{V.fsm._e}" + ' | Exhaust Temperture at Start, Max, Min & Spread (@ Max Temp)'
                    dr2set3 = [
                            {'col':['ExTCylMax@Spread'],'_ylim': [0, 100], 'color':['dodgerblue'], 'unit':'°C'},
                            {'col':['ExTCylMax@MaxTemp','ExTCylMax@MinTemp'],'_ylim': [4200, 4800], 'color':['FireBrick','Crimson'], 'unit':'°C'},
                            {'col':['ExTCylMax@MaxPos','ExTCylMax@MinPos'],'_ylim': [1, 24], 'color':['Thistle','Plum'], 'unit':'-'},
                            {'col':['ExTCylMax@PWR'],'_ylim': [0, 100], 'color':['red'], 'unit':'kW'},
                            {'col':['synchronize'],'_ylim':(-20,400), 'color':'brown', 'unit':'sec'},
                            {'col':['W','A','isuccess'],'_ylim':(-1,200), 'color':['rgba(255,165,0,0.3)','rgba(255,0,0,0.3)','rgba(0,128,0,0.2)'] , 'unit':'-' },
                            #{'col':['startpreparation'],'_ylim':(-1000,800), 'unit':'sec'},
                            {'col':['no'],'_ylim':(0,1000), 'color':['rgba(0,0,0,0.05)'] },
                            ]
                    dr2set3 = dmp2.equal_adjust(dr2set3, rde, do_not_adjust=[5], minfactor=0.95, maxfactor=1.2)
                    fig4 = dmp2.dbokeh_chart(rde, dr2set3, style='both', figsize=self.dfigsize ,title=ntitle);
                    dmp2.bokeh_show(fig4)

                    print()
                    display(rde[V.fsm.results['run2_content']['exhaust']].describe()
                                .style.format(precision=2, na_rep='-'))            

                    print()
                    display(rde[V.fsm.results['run2_content']['exhaust']]
                                .style.format(precision=2,na_rep='-').hide())
            else:
                print('No Data available.')

    def show_sync(self,b): # synch callback
        with self.tab6_out:
            self.tab6_out.clear_output()
            if ((V.fsm is not None) and V.fsm.starts.iloc[0]['run2']):
                rda = V.fsm.starts.reset_index(drop='index')
                thefilter = (
                    (rda['mode'].isin(V.modes_value)) & 
                    (rda['success'].isin(V.succ_value)) & 
                    ((rda['W'] > 0) | ('Warnings' not in V.alarm_warning_value)) & 
                    ((rda['A'] > 0) | ('Alarms' not in V.alarm_warning_value))
                )
                rda = rda[thefilter].reset_index(drop='index')
                global rdb
                rdb = rda
                rde = rda #.fillna('')
                # ['rpm_dmax','rpm_dmin','rpm_spread', 'Lambda_rpm_max', 'TempOil_rpm_max', 'TempCoolWat_rpm_max']
                if not rde.empty:
                    rde['datetime'] = pd.to_datetime(rde['starttime'])

                    print()
                    print('Figures below are filtered by targetload & Spread:')
                    print()
                    if self.cb_loadcap.value:
                        rde = rde[rde['targetload'] > self.t_loadcap.value / 100 * V.fsm._e['Power_PowerNominal']]
                    if self.cb_spreadcap.value:
                        rde = rde[rde['ExSpread@Spread'] > self.t_spreadcap.value]
                    
                    dr2set3 = [
                        {'col':['rpm_dmax'],'_ylim': [4200, 4800], 'color':'red', 'unit':'rpm'},
                        {'col':['rpm_dmin'],'_ylim': [0, 100], 'color':'blue', 'unit':'rpm'},
                        {'col':['rpm_spread'],'_ylim': [0, 100], 'color':'orange', 'unit':'rpm'},
                        {'col':['synchronize'],'_ylim':(-20,400), 'color':'brown', 'unit':'sec'},
                        {'col':['Lambda_rpm_max'],'_ylim': [0, 100], 'color':'purple', 'unit':'a/f'},
                        #{'col':['TempOil_rpm_max','TempCoolWat_rpm_max'],'_ylim': [0, 100], 'color':['crimson','dodgerblue'], 'unit':'mbar'},
                        {'col':['TempOil_rpm_max'],'_ylim': [0, 100], 'color':'crimson', 'unit':'°C'},
                        {'col':['TempCoolWat_rpm_max'],'_ylim': [0, 100], 'color':'dodgerblue', 'unit':'-'},
                        {'col':['W'],'_ylim':(-1,200), 'color':['rgba(255,165,0,0.3)'] },
                        {'col':['no'],'_ylim':(0,1000), 'color':['rgba(0,0,0,0.05)'] }
                    ]
                    dr2set3 = dmp2.equal_adjust(dr2set3, rde, do_not_adjust=['no'], minfactor=0.95, maxfactor=1.2)
                    ntitle = f"{V.fsm._e}" + ' | Speed Max, Min & Spread between Speedmax and GC On'
                    fig4 = dmp2.dbokeh_chart(rde, dr2set3, style='both', figsize=self.dfigsize ,title=ntitle);
                    dmp2.bokeh_show(fig4)

                    dr2set3 = [
                        {'col':['rpm_dmax'],'_ylim': [4200, 4800], 'color':'red', 'unit':'rpm'},
                        {'col':['rpm_dmin'],'_ylim': [0, 100], 'color':'blue', 'unit':'rpm'},
                        {'col':['rpm_spread'],'_ylim': [0, 100], 'color':'orange', 'unit':'rpm'},
                        {'col':['synchronize'],'_ylim':(-20,400), 'color':'brown', 'unit':'sec'},
                        {'col':['Lambda_rpm_max'],'_ylim': [0, 100], 'color':'purple', 'unit':'a/f'},
                        #{'col':['TempOil_rpm_max','TempCoolWat_rpm_max'],'_ylim': [0, 100], 'color':['crimson','dodgerblue'], 'unit':'mbar'},
                        #{'col':['TempOil_rpm_max'],'_ylim': [0, 100], 'color':'crimson', 'unit':'mbar'},
                        {'col':['TempCoolWat_rpm_max'],'_ylim': [0, 100], 'color':'dodgerblue', 'unit':'°C'},
                        {'col':['W'],'_ylim':(-1,200), 'color':['rgba(255,165,0,0.3)'] },
                        {'col':['no'],'_ylim':(0,1000), 'color':['rgba(0,0,0,0.05)'] },
                    ]
                    dr2set3 = dmp2.equal_adjust(dr2set3, rde, do_not_adjust=['no'], minfactor=0.95, maxfactor=1.2)
                    ntitle = f"{V.fsm._e}" + ' | Speed Max, Min & Spread between Speedmax and GC On'
                    fig4 = dmp2.dbokeh_chart(rde, dr2set3, x='TempOil_rpm_max', style='circle', figsize=self.dfigsize ,title=ntitle);
                    dmp2.bokeh_show(fig4)


                    print()
                    display(rde[V.fsm.results['run2_content']['synchronisation']].describe()
                                .style.format(precision=2, na_rep='-'))
                    print()
                    display(rde[V.fsm.results['run2_content']['synchronisation']]
                                .style.format(precision=2,na_rep='-').hide())
            else:
                print('No Data available.')

    def show_oil(self,b): # oil callback
        with self.tab6_out:
            self.tab6_out.clear_output()
            if ((V.fsm is not None) and V.fsm.starts.iloc[0]['run2']):
                rda = V.fsm.starts.reset_index(drop='index')
                thefilter = (
                    (rda['mode'].isin(V.modes_value)) & 
                    (rda['success'].isin(V.succ_value)) & 
                    ((rda['W'] > 0) | ('Warnings' not in V.alarm_warning_value)) & 
                    ((rda['A'] > 0) | ('Alarms' not in V.alarm_warning_value))
                )
                rda = rda[thefilter].reset_index(drop='index')
                global rdb
                rdb = rda
                rde = rda #.fillna('')
                # ['PressOilMax','PressOilDifMax','TempOil_min']
                if not rde.empty:
                    rde['datetime'] = pd.to_datetime(rde['starttime'])
                    dr2set3 = [
                        {'col':['PressOilMax'],'_ylim': [0, 20], 'color':'brown', 'unit':'bar'},
                        {'col':['PressOilDifMax'],'_ylim': [0, 20], 'color':'black', 'unit':'bar'},
                        {'col':['TempOil_min'],'_ylim': [0, 100], 'color':'#2171b5', 'unit':'°C'},
                        {'col':['W'],'_ylim':(-1,200), 'color':['rgba(255,165,0,0.3)'] },
                        {'col':['no'],'_ylim':(0,1000), 'color':['rgba(0,0,0,0.05)'] }
                    ]
                    dr2set3 = dmp2.equal_adjust(dr2set3, rde, do_not_adjust=['no'], minfactor=0.95, maxfactor=1.2)
                    ntitle = f"{V.fsm._e}" + ' | Oil Pressure Max, Oil Filter DP max & Oil Temp vs Starts'
                    fig4 = dmp2.dbokeh_chart(rde, dr2set3, style='both', figsize=self.dfigsize ,title=ntitle);
                    dmp2.bokeh_show(fig4)

                    print()
                    print('Figures below are filtered by targetload & Spread:')
                    print()
                    if self.cb_loadcap.value:
                        rde = rde[rde['targetload'] > self.t_loadcap.value / 100 * V.fsm._e['Power_PowerNominal']]
                    if self.cb_spreadcap.value:
                        rde = rde[rde['ExSpread@Spread'] > self.t_spreadcap.value]

                    dr2set3 = [
                        {'col':['PressOilMax'],'_ylim': [0, 20], 'color':'brown', 'unit':'bar'},
                        {'col':['PressOilDifMax'],'_ylim': [0, 20], 'color':'black', 'unit':'bar'},
                        {'col':['W'],'_ylim':(-1,200), 'color':['rgba(255,165,0,0.3)'] },
                        {'col':['no'],'_ylim':(0,1000), 'color':['rgba(0,0,0,0.05)'] }
                    ]
                    dr2set3 = dmp2.equal_adjust(dr2set3, rde, do_not_adjust=['no'], minfactor=0.95, maxfactor=1.2)
                    ntitle = f"{V.fsm._e}" + ' | Speed Max, Min & Spread between Speedmax and GC On'
                    fig4 = dmp2.dbokeh_chart(rde, dr2set3, x='TempOil_min', style='circle', figsize=self.dfigsize ,title=ntitle);
                    dmp2.bokeh_show(fig4)


                    print()
                    display(rde[V.fsm.results['run2_content']['lubrication']].describe()
                                .style.format(precision=2, na_rep='-'))
                    print()
                    display(rde[V.fsm.results['run2_content']['lubrication']]
                                .style.format(precision=2,na_rep='-').hide())
            else:
                print('No Data available.')

    def show_stop(self,b): # stop callback
        with self.tab6_out:
            self.tab6_out.clear_output()
            if ((V.fsm is not None) and V.fsm.starts.iloc[0]['run4']):
                rda = V.fsm.starts.reset_index(drop='index')
                thefilter = (
                    (rda['mode'].isin(V.modes_value)) & 
                    (rda['success'].isin(V.succ_value)) & 
                    ((rda['W'] > 0) | ('Warnings' not in V.alarm_warning_value)) & 
                    ((rda['A'] > 0) | ('Alarms' not in V.alarm_warning_value))
                )
                rda = rda[thefilter].reset_index(drop='index')
                #rdb = rda
                rde = rda #.fillna('')
                if not rde.empty:
                    rde['datetime'] = pd.to_datetime(rde['starttime'])
                    dr2set2 = [
                    {'col':['maxload','targetload'],'ylim': [4200, 5000], 'color':['FireBrick','red'], 'unit':'kW'},
                    {'col':['coolrun'],'ylim':[0,100], 'color': 'black', 'unit':'sec' },
                    {'col':['runout'],'ylim':[0,100], 'color': 'orange', 'unit':'sec' },
                    {'col':['Stop_Overspeed'],'ylim': [0, 2000], 'color':'blue', 'unit':'rpm'},
                    {'col':['Stop_Throttle'],'ylim': [0, 10], 'color':'gray', 'unit':'%'},
                    {'col':['Stop_PVKDifPress'],'ylim': [0, 100], 'color':'purple', 'unit':'mbar'},
                    {'col':['no'],'_ylim':(0,1000), 'color':['rgba(0,0,0,0.05)'] },
                    ]
                
                    #Checken, ob run2 Resultate im den Daten vorhanden sind und dr2set2 entsprechend anpassen
                    dr2set2_c = [r for r in dr2set2 if all(res in list(V.fsm.starts.columns) for res in r['col'])]
 
                    dr2set2 = dmp2.equal_adjust(dr2set2_c, rde, do_not_adjust=['no'], minfactor=0.95, maxfactor=1.2)
                    ftitle = f"{V.fsm._e}"
                    fig2 = dmp2.dbokeh_chart(rde, dr2set2, style='both', figsize=self.dfigsize ,title=ftitle);
                    dmp2.bokeh_show(fig2)

                    
                    if self.cb_loadcap.value:
                        rde = rde[rde['targetload'] > self.t_loadcap.value / 100 * V.fsm._e['Power_PowerNominal']]
                    rde['bmep'] = rde.apply(lambda x: V.fsm._e._calc_BMEP(x['targetload'], V.fsm._e.Speed_nominal), axis=1)
                    rde['bmep2'] = rde.apply(lambda x: V.fsm._e._calc_BMEP(x['maxload'], V.fsm._e.Speed_nominal), axis=1)
                    dr2set2 = [
                            #{'col':['targetload'],'ylim': [4100, 4700], 'color':'red', 'unit':'kW'},
                            {'col':['bmep2','bmep'],'ylim': [20, 30], 'color':['FireBrick','red'], 'unit':'bar'},
                            {'col':['coolrun'],'ylim':[0,100], 'color': 'black', 'unit':'sec' },
                            {'col':['runout'],'ylim':[0,100], 'color': 'orange', 'unit':'sec' },
                            {'col':['Stop_Overspeed'],'ylim': [0, 2000], 'color':'blue', 'unit':'rpm'},
                            {'col':['Stop_Throttle'],'ylim': [0, 10], 'color':'gray', 'unit':'%'},
                            {'col':['Stop_PVKDifPress'],'ylim': [0, 100], 'color':'purple', 'unit':'mbar'},
                            {'col':['no'],'_ylim':(0,1000), 'color':['rgba(0,0,0,0.05)'] },
                            ]
                    try:
                        dr2set2 = dmp2.equal_adjust(dr2set2, rde, do_not_adjust=['no'], minfactor=1.0, maxfactor=1.1)
                    except Exception as err:
                        print(f'Error: {str(err)}')
                    ntitle = ftitle + ' | BMEP at Start & Stop Data vs TJ Gas Temperature in °C '
                    fig3 = dmp2.dbokeh_chart(rde, dr2set2, x='TJ_GasTemp1_at_Min', style='circle', figsize=self.dfigsize ,title=ntitle);
                    fig3.add_layout(Span(location=V.fsm._e.BMEP,
                            dimension='width',x_range_name='default', y_range_name='0',line_color='red', line_dash='dashed', line_alpha=0.6))
                    #fig3.add_layout(Span(location=20.0,
                    #        dimension='width',x_range_name='default', y_range_name='1',line_color='blue', line_dash='dashed', line_alpha=0.6))

                    dmp2.bokeh_show(fig3)
                    
                    dr2set2 = [
                            {'col':['targetload'],'ylim': [4100, 4700], 'color':'red', 'unit':'kW'},
                            {'col':['bmep2','bmep'],'ylim': [20, 30], 'color':['FireBrick','red'], 'unit':'bar'},
                            {'col':['coolrun'],'ylim':[0,100], 'color': 'black', 'unit':'sec' },
                            {'col':['runout'],'ylim':[0,100], 'color': 'orange', 'unit':'sec' },
                            {'col':['Stop_Overspeed'],'ylim': [0, 2000], 'color':'blue', 'unit':'rpm'},
                            {'col':['Stop_Throttle'],'ylim': [0, 10], 'color':'gray', 'unit':'%'},
                            {'col':['Stop_PVKDifPress'],'ylim': [0, 100], 'color':'purple', 'unit':'mbar'},
                            {'col':['no'],'_ylim':(0,1000), 'color':['rgba(0,0,0,0.05)'] },
                            ]
                    try:
                        #Check, ob run2 Resultate im den Daten vorhanden sind und dr2set2 entsprechend anpassen
                        dr2set2_c = [r for r in dr2set2 if all(res in list(V.fsm.starts.columns) for res in r['col'])]
                        dr2set2 = dmp2.equal_adjust(dr2set2_c, rde, do_not_adjust=['no'], minfactor=1.0, maxfactor=1.1)
                    except Exception as err:
                        print(f'Error: {str(err)}')
                        
                    ntitle = ftitle + ' | BMEP at Start & Stop Data vs TJ TJ_GasDiffPressMin in mbar '
                    fig3 = dmp2.dbokeh_chart(rde, dr2set2, x='TJ_GasDiffPressMin', style='circle', figsize=self.dfigsize ,title=ntitle);
                    fig3.add_layout(Span(location=V.fsm._e.BMEP,
                            dimension='width',x_range_name='default', y_range_name='0',line_color='red', line_dash='dashed', line_alpha=0.6))
                    #fig3.add_layout(Span(location=20.0,
                    #        dimension='width',x_range_name='default', y_range_name='1',line_color='blue', line_dash='dashed', line_alpha=0.6))

                    dmp2.bokeh_show(fig3)            
                    
                print()
                display(rde[V.fsm.results['run4_content']['stop']].describe().style.format(precision=2, na_rep='-'))                
                print()
                display(rde[V.fsm.results['run4_content']['stop']][::-1].style.format(precision=2,na_rep='-').hide())
            else:
                print('No Data available.')