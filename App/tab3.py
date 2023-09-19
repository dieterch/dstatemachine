import os
import pickle
import pandas as pd; pd.options.mode.chained_assignment = None
from datetime import datetime, date
import ipywidgets as widgets
from bokeh.models import Span
from IPython.display import display, HTML
import dmyplant2 as dmp2
import App.common as cm
from pprint import pformat as pf
import logging

#########################################
# tab3
#########################################
class Tab():
    def __init__(self):

        self.title = '3. Results'
        self.dfigsize = cm.V.dfigsize
        self.tab3_out = widgets.Output()
        self.el = widgets.Text(
            value='-', 
            description='selected:', 
            disabled=True, 
            layout=widgets.Layout(width='603px')
        )
        
        self.mo = widgets.SelectMultiple( 
            options=['undefined','OFF','MAN','AUTO'], 
            value=cm.V.modes_value, 
            rows=4, 
            description='modes: ', 
            disabled=False,
            layout=widgets.Layout(width='170px'))
        self.mo.observe(self.mo_observe, 'value')

        self.succ = widgets.SelectMultiple( 
            options=['success','failed','undefined'], 
            value=cm.V.succ_value, 
            rows=4, 
            description='success: ', 
            disabled=False,
            layout=widgets.Layout(width='170px'))        
        self.succ.observe(self.succ_observe, 'value')

        self.alarm_warning = widgets.SelectMultiple( 
            options=['-','Alarms','Warnings'], 
            value=['-'], 
            rows=3, 
            description='A/W', 
            disabled=False,
            layout=widgets.Layout(width='170px'))
        self.alarm_warning.observe(self.alarm_warning_observe, 'value')
        
        self.show_startlist = widgets.Checkbox(
            value=False,
            description="starts list",
            disabled=False,
            indent=False,
            layout=widgets.Layout(width='100px')
        )        
        
        self.list_alarms = widgets.Checkbox(
            value=False,
            description="List Alarms",
            disabled=False,
            indent=False,
            layout=widgets.Layout(width='100px')
        )

        self.list_warnings = widgets.Checkbox(
            value=False,
            description="List Warnings",
            disabled=False,
            indent=False,
            layout=widgets.Layout(width='100px')
        )

        self.selected_engine = widgets.Text(
            value='-', 
            description='selected:', 
            disabled=True, 
            layout=widgets.Layout(width='603px')
        )


        self.timings_button = widgets.Button(
            description='Timings',
            disabled=False, 
            button_style='primary'
        )
        self.timings_button.on_click(self.show_timings)

        ######## from tab6

        self.cb_powerabove = widgets.Checkbox(
            value=False,
            description='PowerAbove',
            disabled=False,
            indent=False,
            layout=widgets.Layout(max_width='110px')
        )
        self.cb_powerabove.observe(self.manage_load_and_spread, 'value')

        self.t_loadcap = widgets.IntText(
            #description='%:',
            value=95,
            layout=widgets.Layout(max_width='60px')
        )

        self.t_loadcaplabel = widgets.Label(
            value="%",
            layout=widgets.Layout(min_width='50px')
        )

        self.cb_powerbelow = widgets.Checkbox(
            value=False,
            description='PowerBelow',
            disabled=False,
            indent=False,
            layout=widgets.Layout(max_width='110px')
        )
        self.cb_powerbelow.observe(self.manage_load_and_spread, 'value')
        
        self.cb_spreadbelow = widgets.Checkbox(
            value=False,
            description='SpreadBelow',
            disabled=False,
            indent=False,
            layout=widgets.Layout(max_width='110px')
        )
        self.cb_spreadbelow.observe(self.manage_load_and_spread, 'value')

        self.t_spreadcap = widgets.IntText(
            #description='%:',
            value=80,
            layout=widgets.Layout(max_width='60px')
        )

        self.t_spreadcaplabel = widgets.Label(
            value="°C",
            layout=widgets.Layout(min_width='50px')
        )

        self.cb_spreadabove = widgets.Checkbox(
            value=False,
            description='SpreadAbove',
            disabled=False,
            indent=False,
            layout=widgets.Layout(max_width='110px')
        )
        self.cb_spreadabove.observe(self.manage_load_and_spread, 'value')

        self.cb_msgfilter = widgets.Checkbox(
            value=False,
            description='Filter msg Nos',
            disabled=False,
            indent=False,
            layout=widgets.Layout(max_width='110px')
        )

        self.msg_no = widgets.Text(
            value='',
            description='',
            layout=widgets.Layout(max_width='200px'))
            #layout=widgets.Layout(max_width='60px'))

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
                    widgets.HBox([
                        self.mo,
                        self.succ, 
                        self.alarm_warning,
                        widgets.VBox([
                            self.list_alarms,
                            self.list_warnings,
                            self.show_startlist
                            ]),
                        widgets.VBox([
                            widgets.HBox([self.cb_powerabove, self.t_loadcap, self.t_loadcaplabel]), 
                            widgets.HBox([self.cb_spreadbelow, self.t_spreadcap, self.t_spreadcaplabel]),
                            widgets.HBox([self.cb_msgfilter, self.msg_no])
                            ]),
                        widgets.VBox([
                            self.cb_powerbelow,
                            self.cb_spreadabove
                            ])
                        ]),
                    widgets.HBox([self.timings_button, self.b_tecjet,self.b_exhaust,self.b_sync,self.b_oil,self.b_stop]),
                    self.tab3_out
                    ],
                    layout=widgets.Layout(min_height=cm.V.hh))

    def mo_observe(self,*args):
        cm.V.modes_value = self.mo.value

    def succ_observe(self,*args):
        cm.V.succ_value = self.succ.value

    def alarm_warning_observe(self,*args):
        cm.V.alarm_warning_value = self.alarm_warning.value

    def selected(self):
        #self.selected_engine.value = cm.V.selected
        with  cm.tabs_out:
            cm.tabs_out.clear_output()
            print(f'tab3 - {cm.V.selected}')

    def cleartab(self):
        self.tab3_out.clear_output() 

    def filter_msg(self, df, mnum):
        mnums = str(mnum).strip().split(',')
        return any([m['msg']['name'] in mnums for m in df['alarms']] + [m['msg']['name'] in mnums for m in df['warnings']])
    
    def manage_load_and_spread(self, *args):
        # print( *args)
        # print(args[0]['name'], args[0]['new'], args[0]['owner'].description)
        if (args[0]['owner'].description == 'PowerAbove' and args[0]['new']):
            self.cb_powerbelow.value = False
        if (args[0]['owner'].description == 'PowerBelow' and args[0]['new']):
            self.cb_powerabove.value = False
        if (args[0]['owner'].description == 'SpreadAbove' and args[0]['new']):
            self.cb_spreadbelow.value = False
        if (args[0]['owner'].description == 'SpreadBelow' and args[0]['new']):
            self.cb_spreadabove.value = False


    def filter_results(self):
        self.rda = cm.V.rdf[:].reset_index(drop='index')
        thefilter = (
            (self.rda['mode'].isin(self.mo.value)) & 
            (self.rda['success'].isin(self.succ.value)) & 
            ((self.rda['W'] > 0) | ('Warnings' not in self.alarm_warning.value)) & 
            ((self.rda['A'] > 0) | ('Alarms' not in self.alarm_warning.value))
        )
        self.rda = self.rda[thefilter]

        if self.cb_msgfilter.value:
            self.rda = self.rda[self.rda.apply(lambda x: self.filter_msg(x, self.msg_no.value), axis=1)] 
        if self.cb_powerabove.value:
            self.rda = self.rda[self.rda['targetload'] > self.t_loadcap.value / 100 * cm.V.fsm._e['Power_PowerNominal']]
        if self.cb_spreadabove.value:
            self.rda = self.rda[self.rda['ExTCylMaxSpread'] > self.t_spreadcap.value]
        if self.cb_powerbelow.value:
            self.rda = self.rda[self.rda['targetload'] < self.t_loadcap.value / 100 * cm.V.fsm._e['Power_PowerNominal']]
        if self.cb_spreadbelow.value:
            self.rda = self.rda[self.rda['ExTCylMaxSpread'] < self.t_spreadcap.value]

        self.rda = self.rda.reset_index(drop='index')
        return self.rda

    #@tab3_out.capture(clear_output=True)
    def show_timings(self,b):
        with self.tab3_out:
            if cm.V.fsm is not None:
                self.tab3_out.clear_output()
                self.filter_results()
                self.rde = self.rda #.fillna('')
                if not self.rde.empty:
                    self.rde['datetime'] = pd.to_datetime(self.rde['starttime'])
                    sdict ={'success':1, 'failed':0, 'undefined':0.5}
                    self.rde['isuccess'] = self.rde.apply(lambda x: sdict[x['success']], axis=1)
                    #vec = ['startpreparation','speedup','idle','synchronize','loadramp','targetload','ramprate','cumstarttime','targetoperation','rampdown','coolrun','runout','isuccess']
                    
                    #dfigsize = (20,10)
                    dset = [
                        {'col':['cumstarttime'],'_ylim':(-600,800), 'color':'darkblue', 'unit':'sec' },
                        {'col':['runout'],'_ylim':(0,100) , 'unit':'sec' },
                        {'col':['targetload'],'_ylim':(-4000,26000) , 'unit':'kW' },
                        {'col':['ramprate'],'_ylim':(-5,7), 'unit':'-' },
                        {'col':['loadramp'],'_ylim':(-150,900), 'color':'red', 'unit':'sec' },
                        {'col':['speedup'],'_ylim':(-100,200), 'color':'orange', 'unit':'sec' },
                        {'col':['synchronize'],'_ylim':(-20,400), 'unit':'sec' },
                        {'col':['oilfilling'],'_ylim':(-1000,800), 'unit':'sec' },
                        {'col':['degasing'],'_ylim':(-1000,800), 'unit':'sec' },
                        {'col':['W','A','isuccess'],'_ylim':(-1,200), 'color':['rgba(255,165,0,0.3)','rgba(255,0,0,0.3)','rgba(0,128,0,0.2)'] , 'unit':'-' },
                        {'col':['no'],'_ylim':(0,1000), 'color':['rgba(0,0,0,0.1)'] , 'unit':'-' },
                        #{'col':['W','A','no'],'ylim':(-1,200), 'color':['rgba(255,165,0,0.3)','rgba(255,0,0,0.3)','rgba(0,0,0,0.1)'] }
                    ]
                     #Checken, ob run2 Resultate im den Daten vorhanden sind und dr2set2 entsprechend anpassen
                    dset_c = [r for r in dset if all(res in list(cm.V.fsm.starts.columns) for res in r['col'])]
                    dset = dmp2.equal_adjust(dset_c, self.rde, do_not_adjust=[-1])
                    ftitle = f"{cm.V.fsm._e}"
                    try:
                        fig = dmp2.dbokeh_chart(self.rde, dset, style='both', figsize=cm.V.dfigsize ,title=ftitle);
                        print()
                        dmp2.bokeh_show(fig)
                    except Exception as err:
                        print('\n','no figure to display, Error: ', str(err))

                    if 'oph' in self.rde:            
                        print
                        dset2 = [
                            {'col':['targetload','maxload'],'ylim':(-4000,26000), 'unit':'kW' },
                            {'col':['idle'],'ylim':(-100,1000), 'color':'dodgerblue', 'unit':'sec' },
                            {'col':['PCDifPress_min'],'ylim':(-3500,500), 'color':'red', 'unit':'mbar' },
                            {'col':['PressBoost_max'],'ylim':(0,10), 'color':'blue', 'unit':'bar' },
                            {'col':['StartCrankCasePressure','StopCrankCasePressure'],'ylim': (-100, 100), 'unit':'mbar'},
                            {'col':['StartRoomTemp','StopRoomTemp'],'ylim': [-20, 60], 'color':['dodgerblue','lightblue'], 'unit':'°C'},
                            {'col':['W','A','isuccess'],'ylim':(-1,200), 'color':['rgba(255,165,0,0.3)','rgba(255,0,0,0.3)','rgba(0,128,0,0.2)'] , 'unit':'-' },
                            {'col':['LOC'],'ylim': [0, 1], 'color':'green', 'unit':'g/kWh'},
                            {'col':['no'],'_ylim':(0,1000), 'color':['rgba(0,0,0,0.1)'] , 'unit':'-' },
                            #{'col':['W','A','no'],'ylim':(-1,200), 'color':['rgba(255,165,0,0.3)','rgba(255,0,0,0.3)','rgba(0,0,0,0.1)'] }
                        ]      
                         #Checken, ob run2 Resultate im den Daten vorhanden sind und dr2set2 entsprechend anpassen
                        dset2_c = [r for r in dset2 if all(res in list(cm.V.fsm.starts.columns) for res in r['col'])]
                        dset2 = dmp2.equal_adjust(dset2_c, self.rde, do_not_adjust=[-1,-2])
                        ftitle = f"{cm.V.fsm._e}"
                        try:
                            fig2 = dmp2.dbokeh_chart(self.rde, dset2, x='oph', style='both', figsize=cm.V.dfigsize ,title=ftitle);
                            print()
                            dmp2.bokeh_show(fig2)
                        except Exception as err:
                            print('\n','no figure to display, Error: ', str(err))
                    else:
                        print("'oph' not found.")
                        
                    vec = cm.V.fsm.results['run2_content']['startstop']
                    print()
                    display(_=self.rde[vec].hist(bins=30,figsize=(20,20)))
                    print()
                    display(self.rde[vec].describe()
                                .style
                                .set_table_styles([
                                    {'selector':'table,td,th', 'props': 'font-size: 0.7rem; '}
                                ])
                                .format(
                            precision=0,
                            na_rep='-',
                            formatter={
                                'starter': "{:.1f}",
                                'idle': "{:.1f}",
                                'PressBoost_max': "{:.2f}",
                                'ramprate':"{:.2f}",
                                'runout': lambda x: f"{x:0.1f}"
                            }
                        ))
                    print()
                    if self.show_startlist.value:
                        display(self.rde[['starttime'] + cm.V.fsm.results['run2_content']['startstop']][::-1]
                                .style
                                .hide()
                                .format(
                            precision=2,
                            na_rep='-',
                            formatter={
                                'starttime': "{:%Y-%m-%d %H:%M:%S %z}",
                                'starter': "{:.1f}",
                                'idle': "{:.1f}",
                                'PressBoost_max': "{:.2f}",
                                'ramprate':"{:.2f}",
                                'runout': lambda x: f"{x:0.1f}"
                            }
                        ))
                    #else:
                    print()
                    if self.list_alarms.value or self.list_warnings.value:
                        self.rde['AW'] = self.rde.apply(lambda x: x['A'] + x['W'] > 0, axis=1)
                        self.rde = self.rde[::-1].reset_index()
                        j = 0; k = 0
                        rowgen = self.rde.iterrows()
                        try:
                            while True:
                                i,row = next(rowgen)
                                if row['AW']:
                                    #if i-k > 0:
                                    #    if not self.show_only_messages.value:
                                    #        display_fmt(self.rde.iloc[k:i])
                                    #if not self.show_only_messages.value:
                                    #    display_fmt(row.to_frame().T)
                                    #else:
                                    #    print('--------------')
                                    #display(HTML("<hr>"))
                                    if self.list_alarms.value:
                                        cm.disp_alwr(row,'alarms',self.cb_msgfilter,self.msg_no.value)
                                    if self.list_warnings.value:
                                        cm.disp_alwr(row,'warnings',self.cb_msgfilter,self.msg_no.value)
                                    k = i + 1
                        except StopIteration:
                            pass

                else:
                    print()
                    print('Empty DataFrame.')

    def show_tecjet(self,b): # tecjet callback
        with self.tab3_out:
            self.tab3_out.clear_output()
            if ((cm.V.fsm is not None) and cm.V.fsm.starts.iloc[0]['run2']):

                rde = self.filter_results()
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
                    dr2set2_c = [r for r in dr2set2 if all(res in list(cm.V.fsm.starts.columns) for res in r['col'])]
 
                    dr2set2 = dmp2.equal_adjust(dr2set2_c, rde, do_not_adjust=['no'], minfactor=0.95, maxfactor=1.2)
                    ftitle = f"{cm.V.fsm._e}"
                    fig2 = dmp2.dbokeh_chart(rde, dr2set2, style='both', figsize=self.dfigsize ,title=ftitle);
                    dmp2.bokeh_show(fig2)

                    #print()
                    #print('Figures below are filtered by targetload & Spread:')
                    print()
                    # if self.cb_loadcap.value:
                    #     rde = rde[rde['targetload'] > self.t_loadcap.value / 100 * cm.V.fsm._e['Power_PowerNominal']]
                    # if self.cb_spreadcap.value:
                    #     rde = rde[rde['ExSpread@Spread'] > self.t_spreadcap.value]

                    rde['bmep'] = rde.apply(lambda x: cm.V.fsm._e._calc_BMEP(x['targetload'], cm.V.fsm._e.Speed_nominal), axis=1)
                    rde['bmep2'] = rde.apply(lambda x: cm.V.fsm._e._calc_BMEP(x['maxload'], cm.V.fsm._e.Speed_nominal), axis=1)
                    dr2set2 = [
                            #{'col':['targetload'],'ylim': [4100, 4700], 'color':'red', 'unit':'kW'},
                            {'col':['bmep2','bmep'],'ylim': [20, 30], 'color':['FireBrick','red'], 'unit':'bar'},
                            {'col':['TJ_GasDiffPressMin'],'ylim': [-20, 80], 'color':'blue', 'unit':'mbar'},
                            {'col':['TJ_Pos_at_Min'],'ylim': [0, 600], 'color':'purple', 'unit':'%'},
                            {'col':['no'],'_ylim':(0,1000), 'color':['rgba(0,0,0,0.05)'] },
                            ]
                    try:
                        dr2set2 = dmp2.equal_adjust(dr2set2, rde, do_not_adjust=['no'], minfactor=1.0, maxfactor=1.1)
                    except Exception as err:
                        print(f'Error: {str(err)}')
                    ntitle = ftitle + ' | BMEP at Start vs TJ Gas Temperature in °C '
                    fig3 = dmp2.dbokeh_chart(rde, dr2set2, x='TJ_GasTemp1_at_Min', style='circle', figsize=self.dfigsize ,title=ntitle);
                    fig3.add_layout(Span(location=cm.V.fsm._e.BMEP,
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
                        dr2set2_c = [r for r in dr2set2 if all(res in list(cm.V.fsm.starts.columns) for res in r['col'])]
                        dr2set2 = dmp2.equal_adjust(dr2set2_c, rde, do_not_adjust=['no'], minfactor=1.0, maxfactor=1.1)
                    except Exception as err:
                        print(f'Error: {str(err)}')
                        
                    ntitle = ftitle + ' | BMEP at Start vs TJ TJ_GasDiffPressMin in mbar '
                    fig4 = dmp2.dbokeh_chart(rde, dr2set2, x='TJ_GasDiffPressMin', style='circle', figsize=self.dfigsize ,title=ntitle);
                    fig4.add_layout(Span(location=cm.V.fsm._e.BMEP,
                            dimension='width',x_range_name='default', y_range_name='0',line_color='red', line_dash='dashed', line_alpha=0.6))
                    #fig3.add_layout(Span(location=20.0,
                    #        dimension='width',x_range_name='default', y_range_name='1',line_color='blue', line_dash='dashed', line_alpha=0.6))

                    dmp2.bokeh_show(fig4)            
                    
                print()
                display(rde[cm.V.fsm.results['run2_content']['tecjet']].describe().style.format(precision=2, na_rep='-'))                
                print()
                display(rde[cm.V.fsm.results['run2_content']['tecjet']][::-1].style.format(precision=2,na_rep='-').hide())
            else:
                print('No Data available.')
    
    def show_temp(self,b): # exhaust callback
        with self.tab3_out:
            self.tab3_out.clear_output()
            if ((cm.V.fsm is not None) and cm.V.fsm.starts.iloc[0]['run2']):
                rde = self.filter_results()
                sdict ={'success':1, 'failed':0, 'undefined':0.5}
                rde['isuccess'] = rde.apply(lambda x: sdict[x['success']], axis=1)
                if not rde.empty:
                    rde['datetime'] = pd.to_datetime(rde['starttime'])                    
                    print()
                    ntitle = f"{cm.V.fsm._e}" + ' | Exhaust Tempertures at Start'
                    dr2set3 = [
                            {'col':['ExTCylMaxSpread'],'_ylim': [0, 100], 'color':['dodgerblue'], 'unit':'°C'},
                            {'col':['ExhTCylMaxTemp'],'_ylim': [4200, 4800], 'color':['FireBrick'], 'unit':'°C'},
                            {'col':['ExTCylMaxTempPos','ExhTCylDevFromAvgNeg_Pos'],'ylim': [1, 24], 'color':['Plum','Crimson'], 'unit':'-'},
                            {'col':['ExhTCylDevFromAvgNeg','ExhTCylDevFromAvgPos'],'ylim': [0, 1000], 'color':['Thistle','Crimson'], 'unit':'°C'},
                            {'col':['W','A','isuccess'],'_ylim':(-1,200), 'color':['rgba(255,165,0,0.3)','rgba(255,0,0,0.3)','rgba(0,128,0,0.2)'] , 'unit':'-' },
                            {'col':['no'],'_ylim':(0,1000), 'color':['rgba(0,0,0,0.05)'] },
                            ]
                    
                    #Checken, ob run2 Resultate im den Daten vorhanden sind und dr2set2 entsprechend anpassen
                    dr2set3_c = [r for r in dr2set3 if all(res in list(cm.V.fsm.starts.columns) for res in r['col'])]

                    dr2set3 = dmp2.equal_adjust(dr2set3_c, rde, do_not_adjust=[5], minfactor=0.95, maxfactor=1.2)
                    fig4 = dmp2.dbokeh_chart(rde, dr2set3, style='both', figsize=self.dfigsize ,title=ntitle);
                    dmp2.bokeh_show(fig4)

                    print()
                    display(rde[cm.V.fsm.results['run2_content']['exhaust']].describe()
                                .style.format(precision=2, na_rep='-'))            

                    print()
                    display(rde[cm.V.fsm.results['run2_content']['exhaust']]
                                .style.format(precision=2,na_rep='-').hide())
            else:
                print('No Data available.')

    def show_sync(self,b): # synch callback
        with self.tab3_out:
            self.tab3_out.clear_output()
            if ((cm.V.fsm is not None) and cm.V.fsm.starts.iloc[0]['run2']):
                rde = self.filter_results()
                if not rde.empty:
                    rde['datetime'] = pd.to_datetime(rde['starttime'])

                    print()                    
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
                    ntitle = f"{cm.V.fsm._e}" + ' | Speed Max, Min & Spread between Speedmax and GC On'
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
                    ntitle = f"{cm.V.fsm._e}" + ' | Speed Max, Min & Spread between Speedmax and GC On'
                    fig4 = dmp2.dbokeh_chart(rde, dr2set3, x='TempOil_rpm_max', style='circle', figsize=self.dfigsize ,title=ntitle);
                    dmp2.bokeh_show(fig4)


                    print()
                    display(rde[cm.V.fsm.results['run2_content']['synchronisation']].describe()
                                .style.format(precision=2, na_rep='-'))
                    print()
                    display(rde[cm.V.fsm.results['run2_content']['synchronisation']]
                                .style.format(precision=2,na_rep='-').hide())
            else:
                print('No Data available.')

    def show_oil(self,b): # oil callback
        with self.tab3_out:
            self.tab3_out.clear_output()
            if ((cm.V.fsm is not None) and cm.V.fsm.starts.iloc[0]['run2']):
                rde = self.filter_results()                
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
                    ntitle = f"{cm.V.fsm._e}" + ' | Oil Pressure Max, Oil Filter DP max & Oil Temp vs Starts'
                    fig4 = dmp2.dbokeh_chart(rde, dr2set3, style='both', figsize=self.dfigsize ,title=ntitle);
                    dmp2.bokeh_show(fig4)

                    print()
                    dr2set3 = [
                        {'col':['PressOilMax'],'_ylim': [0, 20], 'color':'brown', 'unit':'bar'},
                        {'col':['PressOilDifMax'],'_ylim': [0, 20], 'color':'black', 'unit':'bar'},
                        {'col':['W'],'_ylim':(-1,200), 'color':['rgba(255,165,0,0.3)'] },
                        {'col':['no'],'_ylim':(0,1000), 'color':['rgba(0,0,0,0.05)'] }
                    ]
                    dr2set3 = dmp2.equal_adjust(dr2set3, rde, do_not_adjust=['no'], minfactor=0.95, maxfactor=1.2)
                    ntitle = f"{cm.V.fsm._e}" + ' | Speed Max, Min & Spread between Speedmax and GC On'
                    fig4 = dmp2.dbokeh_chart(rde, dr2set3, x='TempOil_min', style='circle', figsize=self.dfigsize ,title=ntitle);
                    dmp2.bokeh_show(fig4)


                    print()
                    display(rde[cm.V.fsm.results['run2_content']['lubrication']].describe()
                                .style.format(precision=2, na_rep='-'))
                    print()
                    display(rde[cm.V.fsm.results['run2_content']['lubrication']]
                                .style.format(precision=2,na_rep='-').hide())
            else:
                print('No Data available.')

    def show_stop(self,b): # stop callback
        with self.tab3_out:
            self.tab3_out.clear_output()
            if ((cm.V.fsm is not None) and cm.V.fsm.starts.iloc[0]['run4']):
                ftitle = f"{cm.V.fsm._e}"
                rde = self.filter_results()            
                if not rde.empty:
                    rde['datetime'] = pd.to_datetime(rde['starttime'])
                    dr2set2 = [
                    {'col':['StopPower'],'ylim': [4200, 5000], 'color':['red'], 'unit':'kW'},
                    {'col':['Stop_Overspeed'],'ylim': [0, 2000], 'color':'blue', 'unit':'rpm'},
                    {'col':['Stop_Throttle'],'ylim': [0, 10], 'color':'gray', 'unit':'%'},
                    {'col':['Idle_CrankcasePressure','StopCrankCasePressure'],'ylim': [-100, 100], 'color':['blue','dodgerblue'], 'unit':'mbar'},
                    {'col':['Stop_PVKDifPress'],'ylim': [0, 100], 'color':'purple', 'unit':'mbar'},
                    {'col':['MaxHexTemp','HexTemp@Power'],'ylim': [0, 700], 'color':['maroon','FireBrick'], 'unit':'°C'},
                    {'col':['oph','starts'],'_ylim': [0, 100], '_color':'black', 'unit':'h'},
                    {'col':['LOC'],'ylim': [0, 0.3], 'color':'green', 'unit':'g/kWh'},
                    {'col':['no'],'_ylim':(0,1000), 'color':['rgba(0,0,0,0.05)'] },
                    ]
                
                    #Checken, ob run2 Resultate im den Daten vorhanden sind und dr2set2 entsprechend anpassen
                    dr2set2_c = [r for r in dr2set2 if all(res in list(cm.V.fsm.starts.columns) for res in r['col'])]
 
                    dr2set2 = dmp2.equal_adjust(dr2set2_c, rde, do_not_adjust=['no'], minfactor=0.95, maxfactor=1.2)
                    ntitle = ftitle + ' | Mix Values at Engine Stop vs. Datetime'
                    fig1 = dmp2.dbokeh_chart(rde, dr2set2, style='circle', figsize=self.dfigsize ,title=ntitle);
                    dmp2.bokeh_show(fig1)

                    ntitle = ftitle + ' | Mix Values at Engine Stop vs. oph'
                    fig2 = dmp2.dbokeh_chart(rde, dr2set2,  x='oph', style='circle', figsize=self.dfigsize ,title=ntitle);
                    dmp2.bokeh_show(fig2)

                    rde['bmep'] = rde.apply(lambda x: cm.V.fsm._e._calc_BMEP(x['targetload'], cm.V.fsm._e.Speed_nominal), axis=1)
                    rde['bmep2'] = rde.apply(lambda x: cm.V.fsm._e._calc_BMEP(x['maxload'], cm.V.fsm._e.Speed_nominal), axis=1)
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

                    ntitle = ftitle + ' |  Mix Values at Engine Stop vs TJ Gas Temperature in °C '
                    fig3 = dmp2.dbokeh_chart(rde, dr2set2, x='TJ_GasTemp1_at_Min', style='circle', figsize=self.dfigsize ,title=ntitle);
                    fig3.add_layout(Span(location=cm.V.fsm._e.BMEP,
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
                            {'col':['Idle_CrankcasePressure'],'ylim': [-100, 100], 'color':'blue', 'unit':'mbar'},
                            {'col':['Stop_Throttle'],'ylim': [0, 10], 'color':'gray', 'unit':'%'},
                            {'col':['Stop_PVKDifPress'],'ylim': [0, 100], 'color':'purple', 'unit':'mbar'},
                            {'col':['no'],'_ylim':(0,1000), 'color':['rgba(0,0,0,0.05)'] },
                            ]
                    try:
                        #Check, ob run2 Resultate im den Daten vorhanden sind und dr2set2 entsprechend anpassen
                        dr2set2_c = [r for r in dr2set2 if all(res in list(cm.V.fsm.starts.columns) for res in r['col'])]
                        dr2set2 = dmp2.equal_adjust(dr2set2_c, rde, do_not_adjust=['no'], minfactor=1.0, maxfactor=1.1)
                    except Exception as err:
                        print(f'Error: {str(err)}')
                        
                    ntitle = ftitle + ' | BMEP at Start & Stop Data vs TJ TJ_GasDiffPressMin in mbar '
                    fig3 = dmp2.dbokeh_chart(rde, dr2set2, x='TJ_GasDiffPressMin', style='circle', figsize=self.dfigsize ,title=ntitle);
                    fig3.add_layout(Span(location=cm.V.fsm._e.BMEP,
                            dimension='width',x_range_name='default', y_range_name='0',line_color='red', line_dash='dashed', line_alpha=0.6))
                    #fig3.add_layout(Span(location=20.0,
                    #        dimension='width',x_range_name='default', y_range_name='1',line_color='blue', line_dash='dashed', line_alpha=0.6))

                    dmp2.bokeh_show(fig3)            
                    
                print()
                display(rde[cm.V.fsm.results['run4_content']['stop']].describe().style.format(precision=2, na_rep='-'))                
                print()
                display(rde[cm.V.fsm.results['run4_content']['stop']][::-1].style.format(precision=2,na_rep='-').hide())
            else:
                print('No Data available.')