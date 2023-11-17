#Version 1.2

from bokeh.io import push_notebook, show, output_notebook, save
from bokeh.plotting import figure, output_file, show
from bokeh.models import LinearAxis, Range1d, HoverTool, DataRange1d
from bokeh.layouts import column, row, gridplot, layout
from bokeh.models import ColumnDataSource, Div
from bokeh.models.widgets import Panel, Tabs
import bokeh

from itertools import cycle
import dmyplant2
from dmyplant2.dPlot import datastr_to_dict, bokeh_chart_engine_comparison, show_val_stats 
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

def is_number(s):
    """ Returns True is string is a number. """
    try:
        float(s)
        return math.isfinite(s)
    except ValueError:
        return False

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

    dval=dmyplant2.Validation.load_def_excel(dir_path+'\Input_engine_comparison.xlsx', 'Engines', mp) #Loading of validation engine data from excel
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
df_var=pd.read_excel(dir_path+'\Input_engine_comparison.xlsx', 'Variables', usecols=['Variable', 'Value']) #loading of relevant excel sheet in DataFrame #loading of relevant excel sheet in DataFrame
df_var.dropna(inplace=True)
for i in range(len(df_var)):
    globals()[df_var.Variable.iloc[i]]=df_var.Value.iloc[i]

validation_name=str(validation_name)

tablist=[]
eng_names=[]
df_app_all=pd.DataFrame()
LOC_average_last=[]
loadrange=pd.DataFrame(columns=['<20%', '[20%, 40%)', '[40%, 90%)', '>=90%'])
starts_oph=pd.DataFrame(columns=['OPH', 'Starts', 'OPH/ Start'])

if use_filter:
    filterstring=(f'Filter treshold {treshold}%')
else:
    filterstring=''#No filter applied'

for eng_count, eng in enumerate(enginelist): 
    df_cfg=pd.read_excel(dir_path+'\Input_engine_comparison.xlsx', sheet_name='Pltcfg', usecols=['Title', 'Variable', 'Unit', 'y-lim min', 'y-lim max'])

    title=eng.Name

    df_cfg.loc[:,'Variable']=df_cfg.loc[:,'Variable'].astype(str)
    df_cfg.loc[:,'Title']=df_cfg.loc[:,'Title'].astype(str)
    df_cfg.loc[:,'Unit']=df_cfg.loc[:,'Unit'].astype(str)
    df_cfg=df_cfg[df_cfg['Variable']!='nan']

    variables=df_cfg['Variable'].tolist()
    variables=[item.replace('\xa0', ' ') for item in variables]

    datastr=list(variables)

    datastr += ['Operating hours engine',#manually add interesting dataitems, for specific calculation or x-axis #eventually method with calls if tems requested (for mean, LOC, filter...)
    'Power current','Power nominal',#for filter
    'Speed current', #For BMEP
    'Starts', #for Starts validation
    #Add custom value: Mention all required values either here or in the definition excel
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

    #Create new df with changed column name and append to dflist
    ##append engine name to columnname
    df_app=df
    df_app = df_app[df_app['Operating hours validation'].ne(df_app['Operating hours validation'].shift())]
    df_app['Operating hours validation']=df_app['Operating hours validation'].round()
    df_app=df_app.set_index('Operating hours validation')
    df_app=df_app.add_prefix(title+'_@_')
    df_app_all=df_app_all.append(df_app)
    eng_names.append (title)

    #Store last LOC data values for data table at beginning of notebook
    if 'LOC_average' in df.columns:
        LOC_average_last.append(df['LOC_average'][-1])
    else:
        LOC_average_last.append(np.nan)
     

#Create ColumnDataSource (use CDS for connecting plots)
source = ColumnDataSource(df_app_all)

#Generate plots in Loop
plots=[]
x_dash=None
for i, variable in enumerate(variables):
    rel_data = [eng_name + '_@_' + variable for eng_name in eng_names]
    y=dict()
    for entry in rel_data:
        if 'col' in y:
            y['col'].append(entry.replace('\xa0', ' '))
        else:
            y['col']=[entry.replace('\xa0', ' ')]

    #set unit if given
    if df_cfg.Unit.iloc[i]!='nan': #take first occurance of unit
        y['unit']=df_cfg.Unit.iloc[i].replace('\xa0', ' ')

    #set y-limits if given
    lim_min=df_cfg['y-lim min'].iloc[i]
    lim_max=df_cfg['y-lim max'].iloc[i]
    if is_number(lim_min) and is_number(lim_max):
        y['ylim']=(lim_min, lim_max) #add tuple y lim

    #set title if given, else use var name
    if df_cfg.Title.iloc[i]!='nan': #take first occurance of unit
        title=df_cfg.Title.iloc[i].replace('\xa0', ' ')
    else:
        title=variable

    cfg=[y]
    if share_x_axes==True and i==1: #Setup shared x-axis or not
        x_dash=plots[0].x_range

    if variable=='LOC_average' or variable=='LOC_raw':
        glyphstyle='line' #set linestyle for interplotated values at LOC
    else:
        glyphstyle='circle'

    plots.append(bokeh_chart_engine_comparison(source, cfg, variable, eng_names, x_range=x_dash, x_ax=x_axes, x_ax_unit='h', title=title, style=glyphstyle))

#Remove plots without renderers
to_remove=[]
for fig in plots:
    if not fig.renderers:
        print(f'{fig.title.text} plot has no data, not shown in the dashboard')
        to_remove.append(fig)
plots = [e for e in plots if e not in to_remove]

    # ##Add timezone to times
berlin = pytz.timezone('Europe/Berlin')
starttime_disp=df.index[0].replace(tzinfo=pytz.utc).astimezone(berlin)
endtime_disp=df.index[-1].replace(tzinfo=pytz.utc).astimezone(berlin)

text1=Div(text='<h1>'+validation_name+': Comparison between engines</h1><h2>Validation start - '+endtime_disp.strftime('%Y-%m-%d %H:%M'))

from bokeh.models.widgets import DataTable, DateFormatter, TableColumn
df_dashboard=vl.dashboard
if 'LOC' in '\#'.join(datastr):
    df_dashboard['LOC']=np.round( [float(i) for i in LOC_average_last], 3)
Columns = [TableColumn(field=Ci, title=Ci) for Ci in df_dashboard.columns] # bokeh columns
data_table = DataTable(columns=Columns, source=ColumnDataSource(df_dashboard), autosize_mode='fit_columns', height=30*(len(df_dashboard.index)+1)) # bokeh table


if display_statistics:
    plot_lay=layout(children=[[plots]], sizing_mode='stretch_width')
    tablist=[Panel(child=plot_lay, title='Engine comparison'), Panel(child=show_val_stats(vl, df_loadrange=loadrange, df_starts_oph=starts_oph), title='Statistics')]
    tabs = Tabs(tabs=tablist)
    lay=layout(children=[text1, data_table, tabs], sizing_mode='stretch_width')
else:
    lay=layout(children=[text1, data_table, [plots]], sizing_mode='stretch_width')

#'fix times'
starttime_string=starttime_disp.strftime('%y_%m_%d %H_%M')
endtime_string=endtime_disp.strftime('%y_%m_%d %H_%M')
output_file(f'{dir_path}\{validation_name} - Comparison between engines  (until {endtime_string}).html', title=f'{validation_name}: Comparison between engines') #Output in browser 

show(lay) #save(layout) for saving only