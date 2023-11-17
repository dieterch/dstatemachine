#Version 1.2

from bokeh.io import push_notebook, show, output_notebook, save
from bokeh.plotting import figure, output_file, show
from bokeh.models import LinearAxis, Range1d, HoverTool
from bokeh.layouts import column, row, gridplot, layout
from bokeh.models import ColumnDataSource, Div
from bokeh.models.widgets import Panel, Tabs
import bokeh

from itertools import cycle
import dmyplant2
from dmyplant2.dPlot import bokeh_chart, datastr_to_dict, expand_cylinder, shrink_cylinder, load_pltcfg_from_excel,show_val_stats
import arrow


import pandas as pd
import numpy as np
import math
import traceback
import matplotlib
import sys
import warnings
import logging
import datetime
import pytz
import os 
dir_path = os.path.dirname(os.path.realpath(__file__))

warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)

logging.basicConfig(
    filename='dmyplant.log',
    filemode='w',
    format='%(asctime)s %(levelname)s, %(message)s',
    level=logging.INFO
)
logging.captureWarnings(True)
hdlr = logging.StreamHandler(sys.stdout)
logging.getLogger().addHandler(hdlr)

dmyplant2.cred()
mp = dmyplant2.MyPlant(0)
from urllib3.exceptions import NewConnectionError
import urllib
import socket

try:
    class myEngine(dmyplant2.Engine):
        @ property
        def dash(self):
            _dash = dict()
            _dash['Name'] = self.Name
            _dash['serialNumber'] = self.serialNumber
            _dash['Site'] = self.get_property('IB Site Name') 
            _dash['Engine ID'] = self.get_property('Engine ID')
            _dash['Design Number'] = self.get_property('Design Number')
            _dash['Engine Type'] = self.get_property('Engine Type')
            _dash['Engine Version'] = self.get_property('Engine Version')
            _dash['Gas type'] = self.get_property('Gas Type')
            _dash['Country'] = self.get_property('Country')
            _dash['OPH Engine'] = self.Count_OpHour
            _dash['OPH Validation'] = self.oph_parts
            _dash['P_nom'] = self.Pmech_nominal
            _dash['BMEP'] = self.BMEP
            _dash['LOC'] = self.get_dataItem(
                'RMD_ListBuffMAvgOilConsume_OilConsumption')
            return _dash

    dval=dmyplant2.Validation.load_def_excel(dir_path+'\Input_validation_dashboard.xlsx', 'Engines', mp) #Loading of validation engine data from excel
    vl = dmyplant2.Validation(mp, dval, lengine=myEngine, cui_log=False)
    enginelist=vl.engines
    logging.info('Engine properties loaded')

except Exception as e:
    print(e)
    if str(e)=="'Engine' object has no attribute 'asset'":
        print ('Possible cause: No internet connection')
    #traceback.print_tb(e.__traceback__)
    sys.exit(1)
  
finally:
    hdlr.close()
    logging.getLogger().removeHandler(hdlr)

    #Loading of Variables from Excel automatic creation of variables


df_var=pd.read_excel(dir_path+'\Input_validation_dashboard.xlsx', sheet_name='Variables', usecols=['Variable', 'Value']) #loading of relevant excel sheet in DataFrame
df_var.dropna(inplace=True)
for i in range(len(df_var)):
    globals()[df_var.Variable.iloc[i]]=df_var.Value.iloc[i]

validation_name=str(validation_name)
###check output,
#check for cylinder list
if display_all_cylinders:
    rel_cyl=all
else:
    try: #see if variable rel_cyl initiated
        rel_cyl=[int(y) for y in rel_cyl.split(',')]
    except:
        try:
            rel_cyl=[int(rel_cyl)]
        except:
            rel_cyl=all

tablist=[]
LOC_average_last=[]
loadrange=pd.DataFrame(columns=['<20%', '[20%, 40%)', '[40%, 90%)', '>=90%'])
starts_oph=pd.DataFrame(columns=['OPH', 'Starts', 'OPH/ Start'])

if use_filter:
    filterstring=(f'Filter treshold {treshold}%')
else:
    filterstring=''#No filter applied'

for eng_count, eng in enumerate(enginelist): 
    pltcfg, plt_titles=load_pltcfg_from_excel()

    title=eng.Name

    if load_all_cylinders==True:
        cyl_to_load=all
    else:
        cyl_to_load=rel_cyl
    datastr=[]
    for cfg in pltcfg:
        for y in cfg:
            y=expand_cylinder(y, cyl_to_load, engi=eng)
            datastr += y['col']


    datastr += ['Operating hours engine','Starts',#manually add interesting dataitems, for specific calculation or x-axis #eventually method with calls if tems requested (for mean, LOC, filter...)
    'Power current','Power nominal',#for filter
    'Exhaust temperature cyl. average', #for delta values if string has Exhaust temperature delta
    'Speed current', #For BMEP
    'Starts', #for Starts validation
    #Add custom variable: Mention all required values either here or in the definition excel
        x_axes] #for value of x_axes

    if 'Exhaust temperature delta' in '\#'.join(datastr): datastr += ['Exhaust temperature'] #Add item if exhaust temperature delta wished
    
    ans=datastr_to_dict(datastr)
    dat=ans[0]

    if start_at_valstart:
        starttime=eng.val_start
    else:
        try:
            starttime=time_download_start
        except:
            starttime=eng.val_start
    if get_recent_data:
        endtime=arrow.utcnow()
    else:
        try:
            endtime=arrow.get(time_download_end)
        except:
            endtime=arrow.utcnow()
    starttime=arrow.get(starttime).to('Europe/Vienna')
    endtime=endtime.to('Europe/Vienna')

    print ('Downloading data for '+title)
    df = eng.hist_data(
            itemIds=dat,
            p_from=starttime,
            p_to=endtime,
            timeCycle=timecycle)#, slot=eng_count)

    ##Change Dataframe - make calculations
    df.rename(columns = ans[1], inplace = True)
    df = df.set_index('datetime')

    #Add Column 'Operating hours validation'
    df['Operating hours validation'] = df['Operating hours engine'] - eng.oph_start

    #Add Column 'Starts validation'
    df['Starts validation'] = df['Starts'] - eng.starts_start

    #Add BMEP
    if 'BMEP' in '\#'.join(datastr):
        df['BMEP'] = (1200*df['Power current']/eng.Generator_Efficiency)/(eng.engvol*df['Speed current'])
    #Leistungsfaktor cos phi nicht berücksichtigt?

    #Add custom value: Make calculation with syntax equal to examples above
    #e.g. df['newName']=df['Operating hours engine]/df['Starts]
    ####
    ####
    ####


    #Calculate EGT delta
    if 'Exhaust temperature delta' in '\#'.join(datastr):
        for col in df.columns:
            if 'Exhaust temperature' in col and any(map(str.isdigit, col)) and not 'delta' in col:
                df[f'Exhaust temperature delta cyl. {col[-2:]}']=df[col].sub(df['Exhaust temperature cyl. average'])

    #Add LOC_average, LOC_raw
    if 'LOC' in '\#'.join(datastr):
        dfres=eng.timestamp_LOC(starttime, endtime, windowsize=average_hours_LOC, return_OPH=True)
        
        df.sort_index(inplace=True) #additional sorting of index
        df=pd.merge_asof(df, dfres, left_index=True, right_index=True)

        duplicated=df.duplicated(subset=['LOC_average'])
        df.loc[duplicated, ['LOC_average']] = np.NaN
        df['LOC_average'] = df['LOC_average'].interpolate()

        if interpolate_raw_LOC:
            duplicated_raw=df.duplicated(subset=['LOC_raw'])
            df.loc[duplicated_raw, ['LOC_raw']] = np.NaN
            df['LOC_raw'] = df['LOC_raw'].interpolate()

    #Add column '%nominal load'
    df['%nominal load']=df['Power current']/df['Power nominal']

    #Export data for each engine
    if export_data:
        df_exp = df[df['%nominal load'] > treshold] #filter
        df_exp = df_exp.reindex(sorted(df.columns), axis=1)
        starttime_df=df.index[0].strftime('%y_%m_%d %H_%M')
        endtime_df=df.index[-1].strftime('%y_%m_%d %H_%M')
        with pd.ExcelWriter(f'{dir_path}\{title} ({starttime_df} - {endtime_df}).xlsx') as writer:  
            df_exp.to_excel(writer, float_format="%.3f")

    #Change time to be plotted (Logic: if plottime=downloadtime-> use that, otherwise see if thereis a date given)
    if start_plot_at_downloadstart:
        calc_time_plot_start=starttime.datetime
    else:
        try:
            calc_time_plot_start=time_plot_start
        except:
            calc_time_plot_start=starttime.datetime
    if end_plot_at_downloadend:
        calc_time_plot_end=endtime.datetime
    else:
        try:
            calc_time_plot_end=time_plot_end
        except:
            calc_time_plot_end=endtime.datetime  
    calc_time_plot_start=calc_time_plot_start.replace(tzinfo=None)
    calc_time_plot_end=calc_time_plot_end.replace(tzinfo=None)
    mask = (df.index > calc_time_plot_start) & (df.index <= calc_time_plot_end)
    df=df.loc[mask]

    #Power load
    loadprofile=[]
    loadprofile.append((df['%nominal load'] < 0.2).sum()/len(df.index))
    loadprofile.append(((df['%nominal load'] >= 0.2) & (df['%nominal load'] < 0.4)).sum()/len(df.index))# and (df['%nominal load'] < 0.4)
    loadprofile.append(((df['%nominal load'] >= 0.4) & (df['%nominal load'] < 0.9)).sum()/len(df.index))
    loadprofile.append((df['%nominal load'] >= 0.9).sum()/len(df.index))
    loadrange.loc[len(loadrange)]=loadprofile
    loadrange.rename({loadrange.index[-1]: eng.Name}, inplace=True)

    #OPH/ Start
    ophlist=[]
    ophlist.append(df['Operating hours engine'].iloc[-1]-df['Operating hours engine'].iloc[0])
    ophlist.append((df['Starts'].iloc[-1]-df['Starts'].iloc[0]).astype(int))
    ophlist.append(ophlist[0]/ophlist[1])
    starts_oph.loc[len(starts_oph)]=ophlist
    starts_oph.rename({starts_oph.index[-1]: eng.Name}, inplace=True)

    #Ignore values with too litte load with filter
    if use_filter:
        df = df[df['%nominal load'] > treshold] #filter

    #Select interesting cylinders
    if load_all_cylinders==True and rel_cyl!=all:
        for cfg in pltcfg:
            for y in cfg:
                y=shrink_cylinder(y, rel_cyl)

    #Change resolution
    if change_timecycle_displayed:
        try: #try if variable timecycle displayed created
            stepsize=max(round(timecycle_displayed/timecycle),1)
            df=df.iloc[::stepsize]
        except:
            pass

    #Store last LOC data values for data table at beginning of notebook
    if 'LOC_average' in df.columns:
        LOC_average_last.append(df['LOC_average'][-1])
    else:
        LOC_average_last.append(np.nan)

    #Create ColumnDataSource (use CDS for connecting plots)
    source = ColumnDataSource(df)

    #Generate plots in Loop
    plots=[]
    x_dash=None
    for i, cfg in enumerate(pltcfg):
        if share_x_axes==True and i==1: #Setup shared x-axis or not
            x_dash=plots[0].x_range
            
        plots.append(bokeh_chart(source, cfg, x_ax=x_axes, x_range=x_dash, title=plt_titles[i]))
        

    #Remove plots without renderers
    to_remove=[]
    for fig in plots:
        if not fig.renderers:
            print(f'{fig.title.text} plot has no data, not shown in the dashboard')
            to_remove.append(fig)
    plots = [e for e in plots if e not in to_remove]

    ##Add timezone to times
    berlin = pytz.timezone('Europe/Berlin')
    starttime_disp=df.index[0].replace(tzinfo=pytz.utc).astimezone(berlin)
    endtime_disp=df.index[-1].replace(tzinfo=pytz.utc).astimezone(berlin)

    if make_tabs==True: #append to tabs or save in file
        text1=Div(text='<h2>'+title+' ('+eng.serialNumber+'): '+starttime_disp.strftime('%Y-%m-%d %H:%M')+' - '+endtime_disp.strftime('%Y-%m-%d %H:%M')+'</h2>')
        lay=layout(children=[text1,[plots]], sizing_mode='stretch_width')
        tablist.append(Panel(child=lay, title=title))
    else:
        text1=Div(text='<h1>'+validation_name+': '+title+' ('+eng.serialNumber+'): '+'</h1><h2>'+starttime_disp.strftime('%Y-%m-%d %H:%M')+' - '+endtime_disp.strftime('%Y-%m-%d %H:%M')+'; '+filterstring)
        lay=layout(children=[text1,[plots]], sizing_mode='stretch_width')
        starttime_string=starttime_disp.strftime('%y_%m_%d %H_%M')
        endtime_string=endtime_disp.strftime('%y_%m_%d %H_%M')
        output_file(f'{title} ({starttime_string} - {endtime_string}).html', title=title) #Output in browser
        save(lay) #save(layout) for saving only
    
    print('')

#Generate tab-layout and out
if make_tabs:
    if display_statistics:
        tablist=tablist+[Panel(child=show_val_stats(vl, df_loadrange=loadrange, df_starts_oph=starts_oph), title='Statistics')]

    tabs = Tabs(tabs=tablist)
    main_title=Div(text='<h1>'+validation_name+': </h1><h2>'+filterstring)

    from bokeh.models.widgets import DataTable, DateFormatter, TableColumn

    #df_dashboard=vl.dashboard.drop('val start', axis=1)
    df_dashboard=vl.dashboard
    if 'LOC' in '\#'.join(datastr):
        df_dashboard['LOC']=np.round( [float(i) for i in LOC_average_last], 3)
    Columns = [TableColumn(field=Ci, title=Ci) for Ci in df_dashboard.columns] # bokeh columns
    data_table = DataTable(columns=Columns, source=ColumnDataSource(df_dashboard), autosize_mode='fit_columns', height=30*(len(df_dashboard.index)+1)) # bokeh table

    test=layout(children=[main_title, data_table, tabs], sizing_mode='stretch_width')

    #output_notebook() #output in Jupyter Notebook
    starttime_string=starttime_disp.strftime('%y_%m_%d %H_%M')
    endtime_string=endtime_disp.strftime('%y_%m_%d %H_%M')
    output_file(f'{dir_path}\{validation_name} ({starttime_string} - {endtime_string}).html', title=validation_name) #Output in browser
    show(test)