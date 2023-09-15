import json
import os
import pandas as pd
from pathlib import Path
from pprint import pformat as pf
import time
from typing import Optional, cast

import solara
import solara.lab

import App.common as cm
import dmyplant2 as dmp2

@solara.component
def LoadFile(localpath,pattern):
    file, set_file = solara.use_state(cast(Optional[Path], None))
    path, set_path = solara.use_state(cast(Optional[Path], None))
    directory, set_directory = solara.use_state(Path("~" + localpath).expanduser())
    showspinner, set_showspinner = solara.use_state(False)
    fsminfo, set_fsminfo = solara.use_state(cast(Optional[str], None))

    def lfilter(s):
        #return s.endswith(pattern)
        return str(s).endswith(pattern)
    
    def lonclick():
        if file is not None:
            set_showspinner(True)
            _ , lfile = os.path.split(file) if file is not None else (None, None) 
            set_fsminfo(f"###⌛ &nbsp;loading ...")
            try:
                cm.V.fsm = dmp2.FSMOperator.load_results(cm.mp, file)
                cm.V.e = cm.V.fsm._e
                cm.V.rdf = cm.V.fsm.starts
                cm.V.selected = cm.V.fsm.results['info']['Name']
                cm.V.selected_number = '0'
                set_showspinner(False)
                info = cm.V.fsm.results['info']
                sinfo =  "| Name | Value |\n"
                sinfo += "| :--- |  ---: |\n"
                for k in info.keys():
                    val = info[k].strftime('%Y-%m-%d') if isinstance(info[k] , pd.Timestamp) else str(info[k])
                    sinfo += f"| {k} | {val} |\n"
                set_fsminfo(sinfo)
            except Exception as e:
                set_fsminfo(e)

    def delclick():
        set_file(None)
        set_fsminfo(None)

    # def lsetdirectory(d):
    #     set_directory(Path("~" + localpath).expanduser())

    with solara.Columns([3,2]) as main:
        with solara.Column():
            can_select =False

            #solara.use_memo(reset_path, [can_select])
            #with solara.Card(style={"height": "100%"}):
            with solara.Card(style={"min-height": "600px"}):
                solara.FileBrowser(directory, on_directory_change=set_directory, filter=lfilter, on_path_select=set_path, on_file_open=set_file, can_select=can_select)

        with solara.Column():
            _ , lfile = os.path.split(file) if file is not None else (None, None)
            with solara.Card(style={"height": "600px"}):
                with solara.VBox():
                    solara.Markdown(f"###**{lfile}**")
                    with solara.Card(style={"min-height": "15em", "max-height": "30em"}):
                            solara.Markdown(f"{fsminfo}")
                    with solara.Row():
                        if lfile is not None:
                            solara.Button(label=f"Load", color="lightgray", on_click=lonclick, style={"margin-top": "10px"})
                            solara.Button(label=f"Delete", color="orange", on_click=delclick, style={"margin-top": "10px"})
    return main

@solara.component
def StartAnalysis():
    with solara.Card(style={"background-color": "yellow", "min-height": "500px"}) as main:
        with solara.Columns([4,1]):
            with solara.Column():
                #solara.Markdown("Start Analysis from installed fleet")
                solara.InputText(label="New Site Name:")
                solara.Select(label="", values=cm.V.query_list, value="text")
                solara.Select(label="Engines:", values=['eins','zwei','drei'])
            with solara.Column():
                with solara.VBox():
                    solara.Button(label="Lookup", color="primary", disabled=False)
                    solara.Button(label="Clear", color="primary", disabled=True, style={"margin-top": "10px"})
    return main
