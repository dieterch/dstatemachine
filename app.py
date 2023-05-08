import solara
import os
if os.name != 'nt':
    import resource
# %matplotlib widget
import pandas as pd
import ipywidgets as widgets
from IPython.display import display, HTML
from App.common import V, init_globals, loading_bar, myfigures, get_query_list, mp, tabs_out, tabs_html
from App import tab1, tab2, tab3, tab4, tab5, tab6, tab7
import dmyplant2 as dmp2
# from dmyplant2 import cred, MyPlant, Engine, cplotdef, get_size
import logging
import shutil

logfilename = 'FSM.log'
if os.path.exists(logfilename):
    shutil.copyfile(logfilename, logfilename[:-4] + '_bak.log')

logging.basicConfig(
    filename=logfilename,
    filemode='w',
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.ERROR
)
logging.info("FSM logging Start")


#########################################
# tabs
#########################################
class App:
    def __init__(self):

        self.tab_objects_list = [
            tab1.Tab(),
            tab2.Tab(),
            tab3.Tab(),
            tab4.Tab(),
            tab5.Tab(),
            tab6.Tab(),
            # tab7.Tab()
        ]

        self.tabs = widgets.Tab()
        self.tabs.observe(self.tabs_change_index, 'selected_index')

        self.set_children()
        self.set_titles()

        self.tab_objects_list[0].selected()  # preselect the first tab.

    def show(self):
        display(
            widgets.VBox([
                self.tabs,
                tabs_out,
                tabs_html])
        )

    def set_children(self):
        self.tabs.children = [t.tab for t in self.tab_objects_list]

    def set_titles(self):
        for i, t in enumerate(self.tab_objects_list):
            self.tabs.set_title(i, t.title)

    def clear_all(self):
        for t in self.tab_objects_list:
            t.cleartab()

    def tabs_change_index(self, *args):  # the tabs callback
        self.tab_objects_list[self.tabs.selected_index].selected()


V.app = App()
V.app.show()
