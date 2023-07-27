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
        set_showspinner(True)
        _ , lfile = os.path.split(file) if file is not None else (None, None) 
        set_fsminfo(f"###&nbsp;&nbsp;loading ...")

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

    # def lsetdirectory(d):
    #     set_directory(Path("~" + localpath).expanduser())

    with solara.Columns([2,2]) as main:
        with solara.Column():
            can_select =False

            #solara.use_memo(reset_path, [can_select])
            solara.FileBrowser(directory, on_directory_change=set_directory, filter=lfilter, on_path_select=set_path, on_file_open=set_file, can_select=can_select)

        with solara.Column():
            _ , lfile = os.path.split(file) if file is not None else (None, None) 
            solara.Markdown(f"""
            <br>
            ###Load FSM File:
            """)   
            solara.Button(label=f"{lfile}", color="primary", on_click=lonclick)
            with solara.Card():
                 with solara.HBox():
                    if showspinner:
                        solara.SpinnerSolara(size="20px")
                    solara.Markdown(f"{fsminfo}")
    return main