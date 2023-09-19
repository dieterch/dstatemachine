from dataclasses import dataclass
from collections.abc import Iterable
import os, sys
import json
import pickle
import pandas as pd; 
import math
pd.options.mode.chained_assignment = None
pd.set_option("display.precision", 2)
import ipywidgets as widgets
from IPython.display import display, HTML
from ipywidgets import AppLayout, Button, Text, Select, Tab, Layout, VBox, HBox, Label, HTML, interact, interact_manual, interactive, IntSlider, Output
import dmyplant2 as dmp2
from pprint import pprint as pp
import logging

try:
    dmp2.cred()
    mp = dmp2.MyPlant(0)
except Exception as err:
    print(str(err))
    sys.exit(1)

def flatten_list(l):
    # make sure single elements are converted to lists also if they are str or bytes to guarantee
    # matrix to be a list of lists
    matrix = [e if (isinstance(e,Iterable) and not isinstance(e, (str,bytes))) else [e] for e in l]
    # nnow flatten by comprehension: [item for row in matrix for item in row]
    return [item for row in matrix for item in row]

def dfigures(e = None):
    def fake_cyl(dataItem):
        return [dataItem[:-1] + '01']
    func_cyl = fake_cyl if e is None else e.dataItemsCyl
    func_power = 5000 if e is None else math.ceil(e['Power_PowerNominal'] / 1000.0) * 1000.0 * 1.2
    f_figure = os.getcwd() + '/App/figures.json'
    figures = dmp2.load_json(f_figure)
    lfigures = figures.copy()
    for key in lfigures.keys():
        for i,r in enumerate(lfigures[key]):
            if 'ylim' in r:
                if r['ylim'] == "func_power":
                    figures[key][i]['ylim'] = [0,func_power]
            for j , dataitem in enumerate(r['col']):
                if 'func_cyl|' in dataitem:
                    lcol = figures[key][i]['col'].copy()
                    lcol[j] = func_cyl(f"{dataitem[len('func_cyl|'):]}")
                    figures[key][i]['col'] = flatten_list(lcol)
    return figures

with open('./assets/Misterious_mist.gif', 'rb') as f:
    img = f.read()    
loading_bar = widgets.Image(
    value=img
)

qfn = './engines.pkl'
query_list_fn = './query_list.json'

def init_query_list():
    return ['Forsa Hartmoor','BMW Landshut']

def get_query_list_pkl():
    if os.path.exists(qfn):
        with open(qfn, 'rb') as handle:
            query_list = pickle.load(handle)
    else:  
        query_list = init_query_list()
    return query_list

def get_query_list():
    if os.path.exists(query_list_fn):
        query_list=dmp2.load_json(query_list_fn)
    else:  
        query_list = init_query_list()
    return query_list

def save_query_list(query_list):
    query_list = [q for q in query_list if not q in ['312','316','320','412','416','420','424','612','616','620','624','920']]
    dmp2.save_json(query_list_fn,query_list)    


global V

@dataclass
class V:
    hh = '350px' # window height
    dfigsize = (18,8)
    dfigsize_big = (20,8)
    fleet = None
    e = None
    lfigures = None
    plotdef, vset = ([],[])
    fsm = None
    rdf = pd.DataFrame([])
    selected = None
    selected_number = None
    modes_value = ['MAN','AUTO']
    succ_value = ['undefined','success','failed']
    alarm_warning_value = ['-']
    query_list = []

def init_globals():
    V.e = None
    V.lfigures = dfigures()
    V.plotdef, V.vset = dmp2.cplotdef(mp, V.lfigures)
    V.fsm = None
    V.rdf = pd.DataFrame([])
    V.query_list = get_query_list()

# el = Text(
#     value='-', description='selected:', disabled=True, 
#     layout=Layout(width='603px'))

init_globals()
tabs_out = widgets.Output()
tabs_html = widgets.HTML(
    value='',
    Layout=widgets.Layout(
        overflow='scroll',
        border ='1px solid black',
        width  ='auto',
        height ='auto',
        flex_flow = "column wrap",
        align_items = "flex-start",
        display='flex')
)

def status(tbname ,text=''):
    with tabs_out:
        tabs_out.clear_output()
        print(f'{tbname}{" - " if text != "" else ""}{text}')

def disp_alwr(row, key, filterit, filtermsgs):
    mnums = str(filtermsgs).strip().split(',')
    rec = row[key]
    style = '''<style>
        table, 
        td, 
        th {
            border: 0px solid grey;
            border-collapse: collapse;
            padding: 0px; 
            margin: 0px;
            font-size:0.7rem;
            line-height: 18px;
            min-width: 110px;
        }
    </style>'''
    ll = []
    for m in rec:
        if m['msg']['name'] in mnums or not filterit.value:
            ll.append({
                'sno': row['no'],
                'datetime':pd.to_datetime(int(m['msg']['timestamp'])*1e6).strftime('%Y-%m-%d %H:%M:%S'),
                'state': m['state'],
                'number': m['msg']['name'],
                'type': 'Alarm' if m['msg']['severity'] == 800 else 'Warning',
                'severity': m['msg']['severity'],
                'message': m['msg']['message']
            })
    if len(rec) > 0:
        display(HTML(style + pd.DataFrame(ll).to_html(index=False, header=False)))

def display_fmt(df):
    display(df[['starttime'] + V.fsm.results['run2_content']['startstop']]                    
                        .style
                        .set_table_styles([
                            {'selector':'table,td,th', 'props': 'font-size: 0.7rem; '}
                        ])
                        .hide()
                        .format(
                    precision=2,
                    na_rep='-',
                    formatter={
                        'starttime': "{:%Y-%m-%d %H:%M:%S %z}",
                        'startpreparation': "{:.0f}",                        
                        'starter': "{:.1f}",
                        'speedup': "{:.1f}",
                        'idle': "{:.1f}",
                        'synchronize': "{:.1f}",
                        'loadramp': "{:.0f}",
                        'cumstarttime': "{:.0f}",
                        'targetload': "{:.0f}",
                        'ramprate':"{:.2f}",
                        'maxload': "{:.0f}",
                        'targetoperation': "{:.0f}",
                        'rampdown': "{:.1f}",
                        'coolrun': "{:.1f}",
                        'runout': lambda x: f"{x:0.1f}"
                    }
                ))