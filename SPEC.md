# dstatemachine — Technical Spec

**Purpose:** Python analysis tool for INNIO field engineers to assess gas engine start/stop reliability. Downloads event messages from the Myplant IoT cloud, runs a Finite State Machine over them to segment engine cycles into phases, and extracts KPIs per start attempt.

**Why:** INNIO field engineers diagnose engine reliability across the fleet using Myplant IoT data. This tool automates the laborious process of identifying which starts succeeded/failed and why, by codifying the engine firmware state machine in Python.

---

## Repository layout

```
dstatemachine/
├── App/                        # JupyterLab ipywidgets dashboard (tabs 1–7)
│   ├── common.py               # Global state dataclass V, mp singleton, helpers
│   ├── tab1.py                 # Engine selection (file chooser + fleet search)
│   ├── tab2.py                 # Message download + FSM execution
│   ├── tab3.py                 # Tabular start results (filterable)
│   ├── tab4.py                 # Per-start Bokeh time-series plots
│   ├── tab5.py                 # Engine settings / dataitem lookup
│   ├── tab6.py                 # Run2 KPI scatter plots (load ramp phase)
│   ├── tab7.py                 # Run4 KPI scatter plots (stop phases)
│   ├── components.py           # Shared widget components
│   ├── figures.json            # Declarative plot definitions for tab4
│   └── stab1.py                # Alternative Solara tab1 (experimental)
├── dmyplant2/                  # Core library package
│   ├── __init__.py             # Public API re-exports; version 0.0.3
│   ├── dMyplant.py             # MyPlant API client (REST + GraphQL)
│   ├── dEngine.py              # Engine class: asset data + HDF time-series cache
│   ├── dValidation.py          # Validation batch analysis helpers
│   ├── dReliability.py         # Reliability KPI calculations
│   ├── dPlot.py                # Bokeh chart helpers (demonstrated reliability etc.)
│   ├── JFBokeh_Validation_DashBoard.py  # Legacy dashboard (Johannes Fischer)
│   ├── support.py              # Credential management (AES-256 + PBKDF2)
│   └── dFSM/                   # FSM sub-package
│       ├── __init__.py
│       ├── dFSM.py             # FSM classes + FSMOperator orchestrator
│       ├── dFSMData.py         # Time-series download helpers (load_data etc.)
│       ├── dFSMFigures.py      # Figure definitions for FSM plots
│       ├── dFSMPlot.py         # FSM-specific Bokeh plotting (splot, VLines…)
│       ├── dFSMResults.py      # Result display helpers (disp_result, pareto charts)
│       ├── dFSMToolBox.py      # Data_Collector plugin base + concrete collectors
│       ├── VBClassLib.py       # VB-style class helpers
│       └── VBClassMainState.py # Alternative main-state class
├── App.ipynb                   # Main notebook (entry point, assembles tabs)
├── login.ipynb                 # Credential setup notebook
├── SPEC.md                     # This file
├── query_list.json             # Persisted search history
├── engines.pkl                 # (legacy) pickled query list
├── requirements.txt
├── setup.py
└── data/                       # Runtime data directory (gitignored)
    ├── .credentials            # Fernet-encrypted credentials
    ├── dataitems.pkl / .csv    # Myplant dataitem catalog (cached from API)
    ├── Installed_base.pkl      # Fleet snapshot
    └── *.dfsm                  # Per-engine FSM result files (pickle protocol 5)
```

---

## Layer architecture

```
┌──────────────────────────────────────────────────────┐
│  App/ (tabs 1–7)  ipywidgets UI  (JupyterLab/Voila)  │
├──────────────────────────────────────────────────────┤
│  dFSM/dFSM.py     FSMOperator + startstopFSM          │
├──────────────────────────────────────────────────────┤
│  dFSM/dFSMToolBox.py  Data_Collector plugins          │
├──────────────────────────────────────────────────────┤
│  dEngine.py       Engine (per-engine data + cache)    │
├──────────────────────────────────────────────────────┤
│  dMyplant.py      MyPlant REST/GraphQL API client     │
└──────────────────────────────────────────────────────┘
```

---

## Key classes

### `MyPlant` (`dMyplant.py`)
- Singleton-ish: one `_session` (requests) shared as class variable.
- Authentication: user+password → MFA challenge → TOTP confirmation → session token (`x-seshat-token` header on every request).
- `hist_data(id, itemIds, p_from, p_to, timeCycle)` — chunked batch download (100 k datapoints/request limit). Returns DataFrame with `time` (epoch ms) + `datetime` columns.
- `fetch_installed_base()` / `get_installed_fleet()` — fleet-wide asset listing, cached to `data/Installed_base.pkl`.
- `create_request_csv()` — downloads Myplant dataitem catalog, saves `data/dataitems.pkl` + `data/dataitems.csv`.
- `_asset_data_graphQL(assetId)` — GraphQL query for rich asset metadata (engine type, series, gas type, contract, etc.).

### `Engine` (`dEngine.py`)
- Constructed via `Engine.from_sn(mp, serialNumber)`.
- `__getitem__(key)` — transparent lookup through nested Myplant asset dict (properties + dataItems).
- `hist_data2(...)` — wraps `MyPlant.hist_data`, backed by HDF5 cache per slot.
- `dataItemsCyl(pattern)` — expands cylinder wildcard patterns to a list of per-cyl dataitem names.
- `_fname` — base path for all cache files: `data/<sn>_...`.
- `sync_load` — engine property: load % at synchronization.
- `description` — dict of engine metadata, merged into `.dfsm` results.

### `startstopFSM` + `FSMOperator` (`dFSM/dFSM.py`)

#### Supporting FSMs (run alongside startstopFSM)
| FSM | States | Purpose |
|-----|--------|---------|
| `ServiceSelectorFSM` | undefined / OFF / MAN / AUTO | Tracks operator mode |
| `OilPumpFSM` | undefined / ON / OFF | Tracks oil pump demand |

#### `startstopFSM` — 11 ordered states

```
standstill → oilfilling → degasing → starter → speedup
           → idle → synchronize → loadramp → targetoperation
           → rampdown → coolrun → runout → standstill (repeat)
```

State transitions triggered by 4-digit Diane firmware message numbers:
| Message | Meaning | Transition |
|---------|---------|-----------|
| 1231 | Request module on | standstill → oilfilling |
| 1249 | Starter on | oilfilling/degasing → starter |
| 1262 | Demand oil pump (DC) off | oilfilling → degasing |
| 3225 | Ignition on | starter → speedup |
| 2124 | Idle | speedup → idle |
| 2139 | Request Synchronization | speedup/idle → synchronize |
| 1235 | Generator CB closed | synchronize → loadramp |
| 9047 | Target load reached | loadramp → targetoperation |
| 1232 | Request module off | various → rampdown/coolrun/standstill |
| 1236 | Generator CB opened | targetoperation → idle / rampdown → coolrun |
| 1234 | Operation off | coolrun → runout |
| 3226 | Ignition off | various → standstill |
| 1225 | Service selector switch Off | various → standstill |

`loadramp` uses the special `LoadrampStateV2` which synthesizes a `9047` message (target load reached) from the ramp rate if the firmware doesn't emit one.

#### `FSMOperator` — 4-pass pipeline

| Pass | Method | What happens |
|------|--------|-------------|
| run0 | `run0()` | Synthetic message injection — if 9047 is missing, calculates target load timestamp from `rP_Ramp_Set` and inserts it. |
| run1 | `run1()` | Main classification pass. Builds `results['starts']` list with per-phase timing (`startstoptiming` dict), alarm/warning lists, `success` flag. |
| run2 | `run2()` | Downloads 1 s time-series for load ramp phase. Runs `Data_Collector` plugins: `Target_load_Collector`, `Exhaust_temp_Collector`, `Tecjet_Collector`, `Sync_Current_Collector`, `Oil_Start_Collector`. |
| run4 | `run4()` | Downloads data for stop phases (rampdown/coolrun/runout). Runs stop collectors: `Rampdown_Collector`, `Coolrun_Collector`, `Runout_Collector`. |

#### `results` dict structure
```python
{
  'sn': str,
  'save_date': datetime,
  'first_message': Timestamp,
  'last_message': Timestamp,
  'starts': [                   # list of per-start dicts
    {
      'no': int,                # sequential index
      'success': 'success'|'failed'|'undefined',
      'mode': 'AUTO'|'MAN'|...,
      'starttime': Timestamp,
      'endtime': Timestamp,
      'oilfilling': float,      # phase duration seconds
      'degasing': float,
      'starter': float,
      'speedup': float,
      'idle': float,
      'synchronize': float,
      'loadramp': float,
      'cumstarttime': float,    # sum of start_timing_states
      'targetoperation': float,
      'rampdown': float,
      'coolrun': float,
      'runout': float,
      'targetload': float,      # % rated load (run2)
      'ramprate': float,        # %/s (run2)
      'maxload': float,         # kW (run2)
      'PCDifPress_min': float,  # Pre-chamber differential pressure (run2)
      'startstoptiming': dict,  # {'state': [{'start': T, 'end': T}, ...]}
      'alarms': [...],          # list of {state, msg} dicts
      'warnings': [...],
      'run2': bool,             # whether run2 was completed for this start
      'run4': bool,
    }
  ],
  'stops': [...],               # similar structure for stop phases
  'run2_content': {             # column lists for display
    'startstop': [...],
    'exhaust': [...],
    ...
  },
  'run4_content': {...},
  'serviceselectortiming': [...],
  'oilpumptiming': [...],
  'starts_counter': int,
  'stops_counter': int,
  'run2_failed': [...],         # starts where run2 couldn't extract KPIs
  'info': {                     # written at save_results() time
    'save_date', 'p_from', 'p_to', 'run2', 'runs_completed', 'starts',
    ...engine description fields...
  }
}
```

#### Success classification (`check_success`)
- `success` = `targetoperation > 300 s` AND no alarms in start phases
- `failed` = alarm occurred during start phases
- `undefined` = no alarm, but `targetoperation ≤ 300 s` (assume intentional stop)

---

## `Data_Collector` plugin pattern (`dFSMToolBox.py`)

Base class `Data_Collector`:
- `__init__(phases)` — declares which FSM phases are needed
- `register(startversuch, vset, tfrom, tto)` — expands the dataitem download window and list
- `collect(startversuch, results, data)` — extracts KPIs from the downloaded DataFrame

Concrete collectors:
| Class | Phase(s) | KPIs extracted |
|-------|---------|---------------|
| `Target_load_Collector` | loadramp | targetload, ramprate, maxload, PCDifPress_min, PressBoost_max, StartCrankCasePressure |
| `Exhaust_temp_Collector` | loadramp | ExhTCylMaxTemp, ExhTCylDevFromAvgPos/Neg, ExTCylMaxSpread, ExTCylMaxTempPos |
| `Tecjet_Collector` | loadramp | TecJet-specific gas valve metrics |
| `Sync_Current_Collector` | synchronize | synchronization current data |
| `Oil_Start_Collector` | oilfilling/degasing | oil pressure at start |
| `Rampdown_Collector` | rampdown | stop phase KPIs |
| `Coolrun_Collector` | coolrun | coolrun duration / temperature |
| `Runout_Collector` | runout | runout timing |

---

## Credential management (`support.py`)

- PBKDF2-HMAC-SHA256 key derivation from a hardcoded passphrase (`smkey`) + random salt stored in `.salt`.
- Credentials (username, password, TOTP secret) serialized to YAML then Fernet-encrypted, stored in `data/.credentials`.
- `cred()` — entry point: reads or collects credentials at startup.
- TOTP secret used with `pyotp` to handle MFA on every login.

---

## Caching strategy

| Cache file | Content | Format |
|------------|---------|--------|
| `data/dataitems.pkl` | Myplant dataitem catalog | pickle |
| `data/dataitems.csv` | Same, CSV form for legacy code | CSV |
| `data/Installed_base.pkl` | Fleet asset list | pickle |
| `data/<sn>.pkl` | Asset metadata per engine | pickle |
| `data/<sn>_statemachine.pkl` | Intermediate FSM run results | pickle protocol 5 |
| `data/<sn>_statemachine.hdf` | Per-engine time-series (HDF5, slotted) | HDF5 |
| `data/*.dfsm` | Final FSM results — **SQLite** (7 tables); legacy pickle files still load transparently | SQLite / pickle (legacy) |
| `data/*.dfsm.pkl_bak` | Backup of original pickle when migrating via `migrate_dfsm()` | pickle protocol 5 |
| `data/<sn>_temp.feather` | Temporary feather cache | Feather |

---

## App (tabs 1–7)

Global state is held in the `V` dataclass in `App/common.py`. The `mp` (MyPlant) singleton is created at import time.

| Tab | Title | Responsibility |
|-----|-------|---------------|
| 1 | select Engine | Fleet search (Combobox + Select), or load `.dfsm` file via FileChooser. Sets `V.e`, `V.fsm`. |
| 2 | messages & FSM | Date-range picker, checkboxes for run2/run4/refresh, triggers FSMOperator execution. |
| 3 | Results | Tabular view of all starts; filter by mode (MAN/AUTO/OFF), success, alarm/warning presence. Shows per-start alarm/warning details. |
| 4 | Start Plots | Per-start Bokeh time-series plots. IntSlider selects start number, `figures.json` defines which dataitems to plot per panel. |
| 5 | settings | Engine metadata display, dataitem lookup, FSM parameter tweaks. |
| 6 | Run2/4 Results | KPI scatter plots from run2 (load ramp). Filters: load capacity cutoff (%), exhaust spread cutoff. |
| 7 | Run4 Results | Stop-phase KPI scatter plots from run4. |

Plot definitions in `App/figures.json` use a declarative format:
```json
{ "panel_name": [{ "col": ["dataitem1"], "ylim": [0, "func_power"], ... }] }
```
`func_cyl|` prefix triggers cylinder expansion via `Engine.dataItemsCyl()`.

---

## Notable design patterns and constraints

1. **`Engine.__getitem__`** transparently resolves keys through nested Myplant asset dict layers (properties list → dataItems list → top-level fields).
2. **`LoadrampStateV2`**: synthesizes the `9047` (target load) message on run0 if firmware never emits it, using `rP_Ramp_Set` (ramp rate in %/s) and `sync_load`.
3. **Multi-pass design**: run0 enriches messages, run1 classifies, run2/run4 download and annotate time-series. Each pass can be run independently; `runs_completed` tracks what's been done.
4. **`append_results`**: allows two `.dfsm` files for the same engine to be merged by matching starttime of the last start in file A with an early start in file B.
4a. **`update_run4(mp, filename)`**: classmethod that loads a SQLite `.dfsm`, runs run4 on starts where `run4==False`, then writes only the run4 KPI columns back in-place via SQL `UPDATE`. No full rewrite needed.
4b. **`migrate_dfsm(mp, path)`**: converts a legacy pickle `.dfsm` to SQLite in-place, creating a `.pkl_bak` backup first.
5. **No formal tests**: ad-hoc `test.py` and a few doctests in `dEngine.py`.
6. **Bokeh 3 compatibility**: several fixes applied (2025-07): `circle()` → `scatter(size=)`, `render_mode` removed from `Label`, `Panel` → `TabPanel`, widget imports from `bokeh.models` (not `bokeh.models.widgets`).
7. **Timestamp duality**: Myplant API uses epoch milliseconds (`mp_ts` / `epoch_ts` helpers in `dMyplant.py` normalize between ms and s).
8. **HDF slot caching**: `Engine.hist_data2()` stores time-series per-slot to avoid redundant downloads when the same data is needed multiple times (e.g. run2 and tab4 both read load ramp data).

---

## .dfsm SQLite schema

Seven tables per file:

| Table | Purpose |
|---|---|
| `info` | key/value — engine metadata + run summary |
| `starts` | one row per start; all scalar KPI columns; timestamps as ISO-8601 TEXT |
| `stops` | one row per stop |
| `timings` | normalised `startstoptiming`: (start_no, phase, seq, phase_start, phase_end) |
| `alarms` | per-start alarm list (start_no, seq, state, ts_epoch, name, severity, message) |
| `warnings` | same structure as alarms |
| `misc` | JSON-encoded: run2_content, run4_content, serviceselectortiming, oilpumptiming, run2_failed, runlogdetail, runs_completed |

Legacy pickle `.dfsm` files are auto-detected on load via magic bytes and continue to work unchanged.

---

## Extension points

- **Add a new KPI**: subclass `Data_Collector` in `dFSMToolBox.py`, register it in `FSMOperator.run2()` or `run4()`.
- **Add a new FSM state**: add the state to `startstopFSM._states` dict with trigger messages; no other file needs changing.
- **Add a new plot panel**: add an entry to `App/figures.json`; no Python code needed.
- **Add a new UI tab**: create `App/tabN.py` with a `Tab` class, import in `App.ipynb`.
