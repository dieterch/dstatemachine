import os
import re
import copy
import math
import ipywidgets as widgets
from ipywidgets import VBox, HBox, Button, Layout
from IPython.display import display
import dmyplant2 as dmp2
import App.common as cm


class Tab():
    def __init__(self):
        self.title = '8. Figure Editor'
        self._updating = False
        self._search_names = []

        self._figures = dmp2.load_json(os.getcwd() + '/App/figures.json')

        # Top buttons
        self.b_save = Button(description='Save figures.json', button_style='success',
                             layout=Layout(width='160px'))
        self.b_save.on_click(self._do_save)

        self.save_as_name = widgets.Text(
            placeholder='filename (no .json)', layout=Layout(width='200px'))
        self.b_save_as = Button(description='Save As', button_style='warning',
                                layout=Layout(width='90px'))
        self.b_save_as.on_click(self._do_save_as)

        self._json_files = self._scan_json_files()
        self.file_pick_select = widgets.Select(
            options=self._json_files, rows=4, layout=Layout(width='260px'))
        if 'figures.json' in self._json_files:
            self.file_pick_select.value = 'figures.json'

        self.b_reload = Button(description='Load from disk', button_style='',
                               layout=Layout(width='120px'))
        self.b_reload.on_click(self._do_reload)

        # Figure set selector
        self.set_select = widgets.Select(
            options=list(self._figures.keys()),
            rows=12, layout=Layout(width='160px'))

        self.new_set_name = widgets.Text(
            placeholder='Set name', layout=Layout(width='150px'))
        self.b_add_set = Button(description='+ Add Set', layout=Layout(width='90px'))
        self.b_rename_set = Button(description='Rename', layout=Layout(width='80px'))
        self.b_copy_set = Button(description='Copy Set', button_style='info',
                                 layout=Layout(width='90px'))
        self.b_delete_set = Button(description='Delete Set', button_style='danger',
                                   layout=Layout(width='90px'))
        self.b_add_set.on_click(self._do_add_set)
        self.b_rename_set.on_click(self._do_rename_set)
        self.b_copy_set.on_click(self._do_copy_set)
        self.b_delete_set.on_click(self._do_delete_set)

        # Panel list
        self.panel_select = widgets.Select(
            options=[], rows=12, layout=Layout(width='480px'))

        self.b_panel_up = Button(description='↑ Up', layout=Layout(width='68px'))
        self.b_panel_down = Button(description='↓ Down', layout=Layout(width='75px'))
        self.b_panel_add = Button(description='+ Panel', layout=Layout(width='75px'))
        self.b_panel_del = Button(description='Del Panel', button_style='danger',
                                  layout=Layout(width='85px'))
        self.b_panel_up.on_click(self._do_panel_up)
        self.b_panel_down.on_click(self._do_panel_down)
        self.b_panel_add.on_click(self._do_panel_add)
        self.b_panel_del.on_click(self._do_panel_del)

        # Panel edit form
        self.col_select = widgets.SelectMultiple(
            options=[], rows=5, layout=Layout(width='480px'))
        self.b_col_remove = Button(description='Remove Selected', button_style='warning',
                                   layout=Layout(width='140px'))
        self.b_col_remove.on_click(self._do_col_remove)

        self.col_edit_text = widgets.Text(
            placeholder='Select a column to edit its name',
            layout=Layout(width='380px'))
        self.b_col_apply = Button(description='Apply Edit', button_style='info',
                                  layout=Layout(width='100px'))
        self.b_col_apply.on_click(self._do_col_apply)
        self.col_select.observe(self._on_col_selected, 'value')

        self.unit_text = widgets.Text(description='Unit:', layout=Layout(width='200px'))
        self.color_text = widgets.Text(
            description='Color:', placeholder='e.g. blue, red, rgba(255,0,0,0.4)',
            layout=Layout(width='460px'))

        self.ylim_radio = widgets.RadioButtons(
            options=['numeric', 'func_power'], description='ylim:',
            layout=Layout(width='180px'))
        self.ylim_min = widgets.FloatText(description='min:', layout=Layout(width='150px'))
        self.ylim_max = widgets.FloatText(description='max:', layout=Layout(width='150px'))

        self.sno_preview = widgets.IntText(
            value=0, description='Start No:', layout=Layout(width='150px'))
        self.b_preview = Button(description='Preview Panel', button_style='primary')
        self.b_preview.on_click(self._do_preview)

        self.unit_text.observe(self._form_changed, 'value')
        self.color_text.observe(self._form_changed, 'value')
        self.ylim_radio.observe(self._form_changed, 'value')
        self.ylim_min.observe(self._form_changed, 'value')
        self.ylim_max.observe(self._form_changed, 'value')

        # DataItem search
        self.search_text = widgets.Text(
            placeholder='Search dataitems...', layout=Layout(width='280px'))
        self.exclude_text = widgets.Text(
            placeholder='Exclude prefix, e.g. par_', layout=Layout(width='220px'))
        self.search_myplant_chkbox = widgets.Checkbox(
            value=False, description='search myPlantName', indent=False)
        self.b_search = Button(description='Search', button_style='primary',
                               layout=Layout(width='80px'))
        self.b_search.on_click(self._do_search)

        self.search_results = widgets.Select(
            options=[], rows=8, layout=Layout(width='640px'))

        self.func_cyl_chkbox = widgets.Checkbox(
            value=False, description='use func_cyl| prefix', indent=False)
        self.b_add_to_panel = Button(description='Add to Panel', button_style='success')
        self.b_add_to_panel.on_click(self._do_add_to_panel)

        self.tab8_out = widgets.Output()

        self.set_select.observe(self._on_set_selected, 'value')
        self.panel_select.observe(self._on_panel_selected, 'value')

        self._refresh_panel_list()

    @property
    def tab(self):
        set_col = VBox([
            widgets.HTML('<b>Figure Sets</b>'),
            self.set_select,
            self.new_set_name,
            HBox([self.b_add_set, self.b_rename_set]),
            HBox([self.b_copy_set, self.b_delete_set]),
        ])

        panel_col = VBox([
            widgets.HTML('<b>Panels</b>'),
            self.panel_select,
            HBox([self.b_panel_up, self.b_panel_down, self.b_panel_add, self.b_panel_del]),
        ])

        form_section = VBox([
            widgets.HTML('<b>Edit Panel</b>'),
            HBox([widgets.HTML('<b>Columns:</b>'), self.b_col_remove]),
            self.col_select,
            HBox([self.col_edit_text, self.b_col_apply]),
            HBox([self.unit_text, self.color_text]),
            HBox([self.ylim_radio, self.ylim_min, self.ylim_max]),
            HBox([self.b_preview, self.sno_preview]),
            self.tab8_out,
        ])

        search_section = VBox([
            widgets.HTML('<b>Search DataItems</b>'),
            HBox([self.search_text, self.exclude_text, self.b_search, self.search_myplant_chkbox]),
            self.search_results,
            HBox([self.b_add_to_panel, self.func_cyl_chkbox]),
        ])

        file_section = VBox([
            widgets.HTML('<b>Load from disk</b>'),
            self.file_pick_select,
            self.b_reload,
        ])

        return VBox([
            HBox([self.b_save,
                  self.save_as_name, self.b_save_as,
                  widgets.HTML('&nbsp;&nbsp;&nbsp;'),
                  file_section]),
            HBox([set_col, panel_col]),
            form_section,
            search_section,
        ], layout=Layout(min_height=cm.V.hh))

    def selected(self):
        pass

    def cleartab(self):
        self.tab8_out.clear_output()

    # --- File list helper ---

    def _scan_json_files(self):
        app_dir = os.path.join(os.getcwd(), 'App')
        try:
            return sorted(f for f in os.listdir(app_dir) if f.endswith('.json'))
        except OSError:
            return []

    # --- Internal helpers ---

    def _current_set(self):
        val = self.set_select.value
        return val if (val is not None and val in self._figures) else None

    def _current_panel_idx(self):
        opts = self.panel_select.options
        val = self.panel_select.value
        if val is None or val not in opts:
            return None
        return list(opts).index(val)

    def _panel_option_str(self, i, p):
        cols = p.get('col', [])
        preview = ', '.join(cols[:3]) + ('...' if len(cols) > 3 else '')
        return f"P{i}: {preview} | {p.get('unit', '')}"

    def _refresh_set_list(self, keep_value=None):
        self._updating = True
        keys = list(self._figures.keys())
        self.set_select.options = keys
        if keep_value and keep_value in keys:
            self.set_select.value = keep_value
        elif keys:
            self.set_select.value = keys[0]
        self._updating = False
        self._refresh_panel_list()

    def _refresh_panel_list(self, keep_idx=None):
        skey = self._current_set()
        if skey is None:
            self._updating = True
            self.panel_select.options = ()
            self._updating = False
            self._refresh_panel_form()
            return
        panels = self._figures[skey]
        opts = tuple(self._panel_option_str(i, p) for i, p in enumerate(panels))
        self._updating = True
        self.panel_select.options = opts
        if opts:
            idx = keep_idx if (keep_idx is not None and keep_idx < len(opts)) else 0
            self.panel_select.value = opts[idx]
        self._updating = False
        self._refresh_panel_form()

    def _refresh_panel_form(self):
        skey = self._current_set()
        idx = self._current_panel_idx()
        if skey is None or idx is None:
            return
        p = self._figures[skey][idx]
        self._updating = True
        self.col_select.options = tuple(p.get('col', []))
        self.unit_text.value = str(p.get('unit', ''))
        has_wildcard = any('*' in c for c in p.get('col', []))
        self.color_text.disabled = has_wildcard
        color = p.get('color', '')
        self.color_text.value = '' if has_wildcard else (', '.join(color) if isinstance(color, list) else str(color))
        ylim = p.get('ylim', [0, 100])
        if ylim == 'func_power':
            self.ylim_radio.value = 'func_power'
            self.ylim_min.disabled = True
            self.ylim_max.disabled = True
        else:
            self.ylim_radio.value = 'numeric'
            self.ylim_min.disabled = False
            self.ylim_max.disabled = False
            if isinstance(ylim, list) and len(ylim) == 2:
                self.ylim_min.value = float(ylim[0])
                self.ylim_max.value = float(ylim[1])
        self._updating = False

    def _write_form_to_panel(self):
        if self._updating:
            return
        skey = self._current_set()
        idx = self._current_panel_idx()
        if skey is None or idx is None:
            return
        p = self._figures[skey][idx]
        p['unit'] = self.unit_text.value
        if any('*' in c for c in p.get('col', [])):
            p.pop('color', None)
            self.color_text.disabled = True
        else:
            self.color_text.disabled = False
            color_str = self.color_text.value.strip()
            p['color'] = [c.strip() for c in color_str.split(',')] if ',' in color_str else color_str
        if self.ylim_radio.value == 'func_power':
            p['ylim'] = 'func_power'
            self.ylim_min.disabled = True
            self.ylim_max.disabled = True
        else:
            p['ylim'] = [self.ylim_min.value, self.ylim_max.value]
            self.ylim_min.disabled = False
            self.ylim_max.disabled = False
        # Refresh option string without losing selection
        self._updating = True
        opts = list(self.panel_select.options)
        opts[idx] = self._panel_option_str(idx, p)
        self.panel_select.options = tuple(opts)
        self.panel_select.value = opts[idx]
        self._updating = False

    def _form_changed(self, change):
        self._write_form_to_panel()

    def _on_set_selected(self, change):
        if not self._updating:
            self._refresh_panel_list()

    def _on_panel_selected(self, change):
        if not self._updating:
            self._refresh_panel_form()

    # --- Figure set management ---

    def _do_add_set(self, b):
        name = self.new_set_name.value.strip()
        if not name:
            with self.tab8_out:
                self.tab8_out.clear_output()
                print('Enter a name in the text field above first.')
            return
        if name in self._figures:
            with self.tab8_out:
                self.tab8_out.clear_output()
                print(f'Set "{name}" already exists.')
            return
        self._figures[name] = []
        self.new_set_name.value = ''
        self._refresh_set_list(keep_value=name)

    def _do_delete_set(self, b):
        skey = self._current_set()
        if skey and skey in self._figures:
            del self._figures[skey]
            self._refresh_set_list()

    def _do_rename_set(self, b):
        skey = self._current_set()
        new_name = self.new_set_name.value.strip()
        if not skey or not new_name:
            return
        if new_name in self._figures:
            with self.tab8_out:
                self.tab8_out.clear_output()
                print(f'Set "{new_name}" already exists.')
            return
        new_figures = {(new_name if k == skey else k): v for k, v in self._figures.items()}
        self._figures = new_figures
        self.new_set_name.value = ''
        self._refresh_set_list(keep_value=new_name)

    def _do_copy_set(self, b):
        skey = self._current_set()
        new_name = self.new_set_name.value.strip()
        if not skey:
            return
        if not new_name:
            with self.tab8_out:
                self.tab8_out.clear_output()
                print('Enter a name for the copy in the text field above first.')
            return
        if new_name in self._figures:
            with self.tab8_out:
                self.tab8_out.clear_output()
                print(f'Set "{new_name}" already exists.')
            return
        self._figures[new_name] = copy.deepcopy(self._figures[skey])
        self.new_set_name.value = ''
        self._refresh_set_list(keep_value=new_name)

    # --- Panel management ---

    def _do_panel_add(self, b):
        skey = self._current_set()
        if skey is None:
            return
        self._figures[skey].append({'col': [], 'ylim': [0, 100], 'unit': '-', 'color': 'blue'})
        self._refresh_panel_list(keep_idx=len(self._figures[skey]) - 1)

    def _do_panel_del(self, b):
        skey = self._current_set()
        idx = self._current_panel_idx()
        if skey is None or idx is None:
            return
        self._figures[skey].pop(idx)
        self._refresh_panel_list(keep_idx=max(0, idx - 1))

    def _do_panel_up(self, b):
        skey = self._current_set()
        idx = self._current_panel_idx()
        if skey is None or idx is None or idx == 0:
            return
        p = self._figures[skey]
        p[idx - 1], p[idx] = p[idx], p[idx - 1]
        self._refresh_panel_list(keep_idx=idx - 1)

    def _do_panel_down(self, b):
        skey = self._current_set()
        idx = self._current_panel_idx()
        if skey is None or idx is None:
            return
        p = self._figures[skey]
        if idx >= len(p) - 1:
            return
        p[idx], p[idx + 1] = p[idx + 1], p[idx]
        self._refresh_panel_list(keep_idx=idx + 1)

    # --- Column management ---

    def _do_col_remove(self, b):
        skey = self._current_set()
        idx = self._current_panel_idx()
        if skey is None or idx is None:
            return
        to_remove = set(self.col_select.value)
        p = self._figures[skey][idx]
        p['col'] = [c for c in p['col'] if c not in to_remove]
        self._updating = True
        self.col_select.options = tuple(p['col'])
        opts = list(self.panel_select.options)
        opts[idx] = self._panel_option_str(idx, p)
        self.panel_select.options = tuple(opts)
        self.panel_select.value = opts[idx]
        self._updating = False

    def _on_col_selected(self, change):
        if self._updating:
            return
        selected = self.col_select.value
        if len(selected) == 1:
            self.col_edit_text.value = selected[0]

    def _do_col_apply(self, b):
        skey = self._current_set()
        idx = self._current_panel_idx()
        if skey is None or idx is None:
            return
        selected = self.col_select.value
        if len(selected) != 1:
            with self.tab8_out:
                self.tab8_out.clear_output()
                print('Select exactly one column to edit.')
            return
        new_name = self.col_edit_text.value.strip()
        if not new_name:
            return
        old_name = selected[0]
        p = self._figures[skey][idx]
        p['col'] = [new_name if c == old_name else c for c in p['col']]
        self._updating = True
        self.col_select.options = tuple(p['col'])
        self.col_select.value = (new_name,)
        opts = list(self.panel_select.options)
        opts[idx] = self._panel_option_str(idx, p)
        self.panel_select.options = tuple(opts)
        self.panel_select.value = opts[idx]
        self._updating = False

    # --- DataItem search ---

    def _do_search(self, b):
        lookup = self.search_text.value.strip()
        exclude = self.exclude_text.value.strip().lower()
        search_myplant = self.search_myplant_chkbox.value
        df = dmp2.MyPlant.get_dataitems()

        def sfun(x):
            lu = lookup.upper()
            return (
                (lu in str(x['id']).upper()) or
                (lu in str(x['name']).upper()) or
                (lu in str(x['unit']).upper()) or
                (search_myplant and lu in str(x['myPlantName']).upper())
            )

        if lookup:
            df = df[df.apply(sfun, axis=1)].reset_index(drop=True)
        if exclude:
            df = df[~df['name'].str.lower().str.startswith(exclude)].reset_index(drop=True)
        self._search_names = list(df['name'])
        opts = tuple(
            f"{row['name']}  |  {row['unit']}  |  {row['myPlantName']}"
            for _, row in df.iterrows()
        )
        self.search_results.options = opts
        if opts:
            self.search_results.value = opts[0]

    def _do_add_to_panel(self, b):
        skey = self._current_set()
        idx = self._current_panel_idx()
        if skey is None or idx is None:
            with self.tab8_out:
                self.tab8_out.clear_output()
                print('Select a panel first.')
            return
        if not self.search_results.options or self.search_results.value is None:
            with self.tab8_out:
                self.tab8_out.clear_output()
                print('Run a search and select a result first.')
            return
        sel_idx = list(self.search_results.options).index(self.search_results.value)
        if sel_idx >= len(self._search_names):
            return
        name = self._search_names[sel_idx]
        if self.func_cyl_chkbox.value:
            name = re.sub(r'\d+$', '', name)
            if not name.endswith('*'):
                name = name + '*'
            name = 'func_cyl|' + name
        p = self._figures[skey][idx]
        p['col'].append(name)
        self._updating = True
        self.col_select.options = tuple(p['col'])
        opts = list(self.panel_select.options)
        opts[idx] = self._panel_option_str(idx, p)
        self.panel_select.options = tuple(opts)
        self.panel_select.value = opts[idx]
        self._updating = False

    # --- Preview ---

    def _expand_panel(self, p_raw):
        p = copy.deepcopy(p_raw)
        e = cm.V.e
        func_cyl = (lambda n: [n[:-1] + '01']) if e is None else e.dataItemsCyl
        func_power = 5000 if e is None else math.ceil(e['Power_PowerNominal'] / 1000.0) * 1000.0 * 1.2
        if p.get('ylim') == 'func_power':
            p['ylim'] = [0, func_power]
        new_col = []
        for item in p.get('col', []):
            if 'func_cyl|' in item:
                new_col.extend(func_cyl(item[len('func_cyl|'):]))
            else:
                new_col.append(item)
        p['col'] = new_col
        return p

    def _do_preview(self, b):
        with self.tab8_out:
            self.tab8_out.clear_output()
            if cm.V.fsm is None or cm.V.e is None:
                print('Load an engine and .dfsm file first (tabs 1 & 2).')
                return
            skey = self._current_set()
            idx = self._current_panel_idx()
            if skey is None or idx is None:
                print('Select a panel to preview.')
                return
            p_raw = self._figures[skey][idx]
            if not p_raw.get('col'):
                print('Panel has no columns defined.')
                return
            sno = self.sno_preview.value
            rdf = cm.V.fsm.starts
            if rdf.empty or sno >= len(rdf):
                print(f'Start No {sno} not available (total starts: {len(rdf)}).')
                return
            startversuch = rdf.iloc[sno]
            p_expanded = self._expand_panel(p_raw)
            vset = p_expanded['col']
            try:
                print(f'Loading data for Start No. {sno}...')
                data = dmp2.get_cycle_data3(
                    cm.V.fsm, startversuch,
                    cycletime=1, silent=True, p_data=vset, p_refresh=False)
                ftitle = (f"{cm.V.fsm._e} — Start {startversuch['no']}"
                          f" | {skey} P{idx}")
                fig = dmp2.FSM_splot(cm.V.fsm, startversuch, data, [p_expanded],
                                     title=ftitle)
                fig = dmp2.FSM_add_Notations(fig, cm.V.fsm, startversuch)
                fig = dmp2.FSM_add_StatesLines(fig, cm.V.fsm, startversuch)
                dmp2.bokeh_show(fig)
            except Exception as err:
                print(f'Preview error: {err}')

    # --- Save / Reload ---

    def _clean_figures(self, figures):
        for panels in figures.values():
            for p in panels:
                color = p.get('color', None)
                if color is not None:
                    empty = (isinstance(color, str) and color.strip() == '') or \
                            (isinstance(color, list) and all(c.strip() == '' for c in color))
                    if empty:
                        del p['color']
        return figures

    def _do_save(self, b):
        with self.tab8_out:
            self.tab8_out.clear_output()
            path = os.path.join(os.getcwd(), 'App', 'figures.json')
            dmp2.save_json(path, self._clean_figures(self._figures))
            cm.V.lfigures = cm.dfigures(cm.V.e)
            cm.V.plotdef, cm.V.vset = dmp2.cplotdef(cm.mp, cm.V.lfigures)
            print(f'Saved to {path}')
            print(f'Reloaded: {len(cm.V.plotdef)} figure sets, {len(cm.V.vset)} data items.')

    def _do_save_as(self, b):
        name = self.save_as_name.value.strip()
        with self.tab8_out:
            self.tab8_out.clear_output()
            if not name:
                print('Enter a filename (without .json) in the text field.')
                return
            fname = name if name.endswith('.json') else name + '.json'
            path = os.path.join(os.getcwd(), 'App', fname)
            dmp2.save_json(path, self._clean_figures(self._figures))
            print(f'Saved to {path}')
            self.save_as_name.value = ''
            # refresh file picker so the new file appears
            self._json_files = self._scan_json_files()
            self.file_pick_select.options = self._json_files
            if fname in self._json_files:
                self.file_pick_select.value = fname

    def _do_reload(self, b):
        fname = self.file_pick_select.value
        with self.tab8_out:
            self.tab8_out.clear_output()
            if not fname:
                print('Select a file in the list above first.')
                return
            path = os.path.join(os.getcwd(), 'App', fname)
            self._figures = dmp2.load_json(path)
            cur_set = self._current_set()
            self._refresh_set_list(keep_value=cur_set)
            print(f'Loaded {fname} from disk.')
