import os
import re
import traceback
import pandas as pd; pd.options.mode.chained_assignment = None
import ipywidgets as widgets
from IPython.display import display, HTML
import dmyplant2 as dmp2
import App.common as cm
import logging

DATA_DIR = os.path.join(os.getcwd(), 'data')


class Tab():
    def __init__(self):
        self.title = '1. select Engine'
        self.tab1_out = widgets.Output()

        # ── File chooser panel ──────────────────────────────────────
        self._all_files = self._scan_dfsm_files()

        self.file_search = widgets.Text(
            value='',
            placeholder='type to filter …',
            description='Filter:',
            layout=widgets.Layout(width='340px'))
        self.file_search.observe(self._apply_search, 'value')

        self.file_select = widgets.Select(
            options=self._all_files,
            rows=12,
            layout=widgets.Layout(width='560px'))

        self.bt_load_testfile = widgets.Button(
            description='Load',
            disabled=False,
            button_style='success')
        self.bt_load_testfile.on_click(self.load_testfile)

        self.child1 = widgets.VBox([
            widgets.HBox([self.file_search, self.bt_load_testfile]),
            self.file_select,
        ])

        # ── Fleet panel ─────────────────────────────────────────────
        self.query_drop_down = widgets.Combobox(
            value='',
            options=cm.V.query_list,
            description='Site Name:',
            disabled=False,
            layout=widgets.Layout(width='600px'))

        self.engine_selections = widgets.Select(
            options=list(),
            rows=10,
            description='Engine:',
            disabled=False,
            layout=widgets.Layout(width='600px'))
        self.engine_selections.observe(self.do_selection, 'value')

        self.selected_engine = widgets.Text(
            value='-',
            description='selected:',
            disabled=True,
            layout=widgets.Layout(width='400px'))

        self.selected_engine_number = widgets.Text(
            value='-',
            description='Motor No:',
            disabled=True,
            layout=widgets.Layout(width='200px'))

        self.b_search = widgets.Button(
            description='Lookup',
            disabled=False,
            tooltip='Site Name / Engine Type / Engine Version / Design Number / serialNumber / assetNumber',
            button_style='primary')
        self.b_search.on_click(self.search)

        self.b_LoadEngine = widgets.Button(
            description='Load Engine',
            disabled=False,
            button_style='primary',
            layout=widgets.Layout(display='none'))
        self.b_LoadEngine.on_click(self.loadEngine)

        self.b_clear = widgets.Button(
            description='Clear',
            disabled=False,
            button_style='')
        self.b_clear.on_click(self.clear)

        self.child2 = widgets.HBox([
            widgets.VBox([
                self.query_drop_down,
                self.engine_selections,
                widgets.HBox([self.selected_engine, self.selected_engine_number])
            ]),
            widgets.VBox([self.b_search, self.b_LoadEngine, self.b_clear])
        ])

        # ── Accordion ───────────────────────────────────────────────
        self.accordion = widgets.Accordion(children=[self.child1, self.child2])
        self.accordion.set_title(0, 'FSM Files')
        self.accordion.set_title(1, 'Start Analysis from Installed Fleet')
        self.accordion.observe(self.accordion_change_index, 'selected_index')
        self.accordion.selected_index = 1

        # ── Persistent load-state indicator ─────────────────────────
        self.load_state_html = widgets.HTML(value=self._render_load_state())

    # ── File list helpers ────────────────────────────────────────────

    def _dfsm_label(self, fname):
        path = os.path.join(DATA_DIR, fname)
        try:
            with open(path, 'rb') as fh:
                magic = fh.read(16)
            if magic[:15] == b'SQLite format 3':
                icon = '\U0001f5c4'   # 🗄 cabinet (SQLite)
            elif magic[:1] == b'\x80':
                icon = '\U0001f952'   # 🥒 pickle
            else:
                icon = '\U0001f4c4'   # 📄 generic
        except OSError:
            icon = '?'
        return f'{icon} {fname}'

    def _scan_dfsm_files(self):
        """Return sorted list of (label, filename) tuples for .dfsm files in DATA_DIR."""
        try:
            files = [f for f in os.listdir(DATA_DIR) if f.endswith('.dfsm')]
        except OSError:
            return []
        files = sorted(files, key=lambda f: re.sub(r'^\d+_', '', f).lower())
        return [(self._dfsm_label(f), f) for f in files]

    def _apply_search(self, change):
        q = change['new'].strip().lower()
        filtered = [t for t in self._all_files if q in t[1].lower()] if q else self._all_files
        current = self.file_select.value
        self.file_select.options = filtered
        if current in [t[1] for t in filtered]:
            self.file_select.value = current

    # ── Load state indicator ────────────────────────────────────────

    def _render_load_state(self, error=None):
        if error:
            return (f'<div style="padding:6px 10px; background:#ffebee; '
                    f'border-left:4px solid #f44336; font-size:0.85rem; color:#b71c1c">'
                    f'&#10060; {error}</div>')
        if cm.V.fsm is None and cm.V.e is None:
            return ('<div style="padding:6px 10px; background:#f5f5f5; '
                    'border-left:4px solid #aaa; font-size:0.85rem; color:#666">'
                    'No data loaded</div>')
        if cm.V.fsm is None:
            return (f'<div style="padding:6px 10px; background:#fff8e1; '
                    f'border-left:4px solid #ffc107; font-size:0.85rem">'
                    f'Engine: <b>{cm.V.selected}</b> &nbsp;|&nbsp; no FSM results</div>')
        runs = sorted(cm.V.fsm.runs_completed)
        runs_str = ', '.join(f'run{r}' for r in runs) if runs else '—'
        rdf = cm.V.rdf
        n = len(rdf) if rdf is not None and not rdf.empty else 0
        if n > 0 and 2 in runs:
            succ = rdf[rdf['success'] == 'success'].shape[0]
            fail = rdf[rdf['success'] == 'failed'].shape[0]
            pct = succ / n * 100
            detail = f'{n} starts &nbsp;|&nbsp; {succ} ok / {fail} fail &nbsp;|&nbsp; reliability {pct:.0f}%'
        else:
            detail = f'{n} starts'
        return (f'<div style="padding:6px 10px; background:#e8f5e9; '
                f'border-left:4px solid #4caf50; font-size:0.85rem">'
                f'&#10003; Engine: <b>{cm.V.selected}</b> &nbsp;|&nbsp; '
                f'{runs_str} &nbsp;|&nbsp; {detail}</div>')

    def _update_load_state(self, error=None):
        self.load_state_html.value = self._render_load_state(error=error)

    # ── Widget tree ─────────────────────────────────────────────────

    @property
    def tab(self):
        return widgets.VBox([
            self.accordion,
            self.load_state_html,
            self.tab1_out
        ], layout=widgets.Layout(min_height=cm.V.hh))

    def selected(self):
        self._update_load_state()
        with cm.tabs_out:
            cm.tabs_out.clear_output()
            print(f'tab1 - {cm.V.selected}')

    def cleartab(self):
        self.tab1_out.clear_output()

    # ── Callbacks ───────────────────────────────────────────────────

    def loadEngine(self, but):
        if cm.V.selected_number is None:
            return
        cm.tabs_html.value = ''
        cm.status('tab1', f'⌛ loading Myplant Engine Data for "{cm.V.selected}" …')
        try:
            logging.debug(f"loadEngine: cm.V.e = {cm.V.e}.")
            logging.debug(f"fleet info: {cm.V.fleet.iloc[int(cm.V.selected_number)]}")
            cm.V.e = dmp2.Engine.from_fleet(cm.mp, cm.V.fleet.iloc[int(cm.V.selected_number)])
            logging.debug(f"got this engine back: {cm.V.e}")
            cm.V.fsm = None
            self._update_load_state()
            cm.status('tab1', cm.V.selected)
        except Exception as err:
            logging.error(f"loadEngine: {err}")
            self._update_load_state(error=f'Engine load failed: {err}')
            cm.status('tab1', f'Error: {err}')

    def do_lookup(self, lookup):
        def sfun(x):
            return (
                (str(lookup).upper() in str(x['IB Site Name']).upper()) or
                (str(lookup).upper() in str(x['Engine Type']).upper()) or
                (str(lookup).upper() in str(x['Engine Version']).upper()) or
                (str(lookup) == str(x['Design Number'])) or
                (str(lookup) == str(x['serialNumber'])) or
                (str(lookup) == str(x['id']))) and \
                (x['OperationalCondition'] != 'Decommissioned')

        cm.V.fleet = cm.mp.search_installed_fleet(sfun).drop('index', axis=1)
        cm.V.fleet = cm.V.fleet.sort_values(by='Engine ID', ascending=True).reset_index(drop='index')
        return [f"{x['serialNumber']}  J{x['Engine Type']} {x['Engine Version']:<4} {x['Engine ID']} {x['IB Site Name']}"
                for i, x in cm.V.fleet.iterrows()]

    def do_selection(self, *args):
        self.selected_engine.value = self.engine_selections.value
        self.selected_engine_number.value = str(
            list(self.engine_selections.options).index(self.engine_selections.value))
        cm.V.selected = self.selected_engine.value
        cm.V.selected_number = self.selected_engine_number.value
        cm.status('tab1', f'{len(list(self.engine_selections.options))} Engines found — select one and load it.')
        self.b_LoadEngine.layout.display = 'block'

    def search(self, but):
        self.tab1_out.clear_output()
        if not self.query_drop_down.value:
            cm.status('tab1', 'please provide a query string.')
            return
        try:
            self.engine_selections.options = self.do_lookup(self.query_drop_down.value)
            with cm.tabs_out:
                cm.tabs_html.value = (cm.V.fleet[:].T
                    .style
                    .set_table_styles([{'selector': 'th,td',
                                        'props': 'font-size:0.7rem; min-width: 70px; margin: 0px; padding: 0px;'}])
                    .format(precision=0, na_rep='-')
                    .to_html(escape=False, index=False))
            if (self.query_drop_down.value not in cm.V.query_list and
                    len(self.engine_selections.options) > 0):
                cm.V.query_list.append(self.query_drop_down.value)
            cm.save_query_list(cm.V.query_list)
        except Exception as err:
            logging.error(f"search: {err}")
            cm.status('tab1', f'Lookup error: {err}')

    def load_testfile(self, but):
        self.tab1_out.clear_output()
        fname = self.file_select.value
        if not fname:
            cm.status('tab1', 'please select a *.dfsm file.')
            return
        sel = os.path.join(DATA_DIR, fname)
        cm.status('tab1', f'⌛ loading {fname} …')
        try:
            cm.V.fsm = dmp2.FSMOperator.load_results(cm.mp, sel)
            cm.V.e = cm.V.fsm._e
            cm.V.rdf = cm.V.fsm.starts
            cm.V.selected = cm.V.fsm.results['info']['Name']
            cm.V.selected_number = '0'
            self.selected_engine.value = cm.V.selected
            self.selected_engine_number.value = cm.V.selected_number
            self._update_load_state()
            cm.status('tab1', cm.V.selected)
            with self.tab1_out:
                info = cm.V.fsm.results['info']
                rows = ''.join(
                    f'<tr><td style="font-weight:bold;padding:2px 8px">{k}</td>'
                    f'<td style="padding:2px 8px">'
                    f'{v.strftime("%Y-%m-%d") if isinstance(v, pd.Timestamp) else str(v)}'
                    f'</td></tr>'
                    for k, v in info.items())
                display(HTML(
                    f'<table style="font-size:0.8rem;border-collapse:collapse">{rows}</table>'))
            cm.V.app.clear_all()
        except Exception as err:
            logging.error(f"load_testfile: {traceback.format_exc()}")
            self._update_load_state(error=f'Load failed: {err}')
            cm.status('tab1', f'Error loading {fname}: {err}')

    def clear(self, but):
        cm.tabs_out.clear_output()
        cm.tabs_html.value = ''
        self.tab1_out.clear_output()
        self.b_LoadEngine.layout.display = 'none'
        self.query_drop_down.value = ''
        self.engine_selections.options = ['']
        self.selected_engine.value = ''
        self.selected_engine_number.value = ''
        self.file_search.value = ''
        self.file_select.options = self._all_files
        cm.V.selected = None
        cm.V.selected_number = None
        cm.V.fsm = None
        cm.V.e = None
        self._update_load_state()
        cm.V.app.clear_all()
        cm.status('tab1')

    def accordion_change_index(self, *args):
        if self.accordion.selected_index == 0:
            cm.status('tab1', 'please select a *.dfsm file.')
        elif self.accordion.selected_index == 1:
            cm.status('tab1', 'please provide a query string.')
