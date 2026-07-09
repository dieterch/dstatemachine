# Tab 8 — Figure Editor: User Manual

## What it does

`figures.json` defines every plot that appears in **Tab 4 (Start Plots)**. Each entry is a named **Figure Set** (e.g. `actuators`, `exhaust`) containing a list of **Panels** — one stacked sub-plot each. Tab 8 lets you create, edit, reorder, and preview these without touching the JSON file by hand.

---

## Concepts

| Term | Meaning |
|---|---|
| **Figure Set** | A named group of panels shown together when you pick it in Tab 4. e.g. `actuators`, `exhaust`. |
| **Panel** | One horizontal strip in the plot — shows one or more data columns on a shared Y-axis. |
| **Column** | A MyPlant data item name, e.g. `Various_Values_SpeedAct`. |
| **`func_cyl|`** | Special prefix that expands a template name to all cylinder channels automatically. |
| **ylim** | The fixed Y-axis range for a panel. Use `func_power` to auto-scale to nominal engine power. |

---

## Layout overview

```
[ Save figures.json ]  [ Reload from disk ]

Figure Sets       │  Panels
──────────────────┼──────────────────────────────────────
actuators         │  P0: Power_SetPower, Power_PowerAct … | kW
exhaust      ◄──  │  P1: Various_Values_SpeedAct … | rpm
hydraulics        │  P2: TecJet_Lambda1 … | -
…                 │  [ ↑ Up ] [ ↓ Down ] [ + Panel ] [ Del Panel ]
──────────────────┴──────────────────────────────────────
Edit Panel
  Columns: [list]   [ Remove Selected ]
  Unit: °C    Color: blue, red
  ylim: ○ numeric  min: 0  max: 700
        ○ func_power
  [ Preview Panel ]  Start No: 5

Search DataItems
  [search box]  [ Search ]  □ search myPlantName
  [results list]
  [ Add to Panel ]  □ use func_cyl| prefix
```

---

## Step-by-step workflows

### 1. Viewing and navigating existing sets

1. Open **Tab 8**. The left column lists all Figure Sets from `figures.json`.
2. Click any set name — the **Panels** list updates on the right.
3. Click any panel — the **Edit Panel** section fills with its current columns, unit, color, and Y-axis range.
4. Nothing is saved until you click **Save figures.json**.

---

### 2. Editing an existing panel's Y-axis range

*Example: the `exhaust` set, panel P4 currently shows cylinder exhaust temps at `ylim [0, 700]`. You want to narrow it to `[300, 700]` for better resolution.*

1. Click **exhaust** in the Figure Sets list.
2. Click **P4** in the Panels list (the one with `Exhaust_TempCyl*`).
3. In Edit Panel, change **min** to `300`, **max** to `700`.
4. The panel list label updates immediately.
5. Click **Preview Panel** (with a valid start number) to see the result.
6. Click **Save figures.json** when satisfied.

---

### 3. Changing a panel's color

*Example: make the speed trace in `hydraulics` orange instead of blue.*

1. Select **hydraulics**, then click **P1** (`Various_Values_SpeedAct`).
2. In the **Color** field, replace `blue` with `orange`.
3. For multiple columns, enter comma-separated values: `red, blue, green` — one per column, in order.
4. CSS named colors, hex codes, and `rgba(r,g,b,a)` all work. Example: `rgba(255,165,0,0.4)` is a semi-transparent orange.

---

### 4. Adding a new data column to an existing panel

*Example: add `Hyd_TempCoolWat` to the temperature panel in `hydraulics`.*

1. Select **hydraulics**, then click the temperature panel (P6, `Hyd_TempOil, Hyd_TempCoolWat…`).
2. Scroll to **Search DataItems**. Type `TempCool` in the search box and click **Search**.
3. The results list shows matching items with their unit and MyPlant name.
4. Click the correct entry to select it.
5. Click **Add to Panel**. The column name appears in the **Columns** list.
6. If the colors list has fewer entries than columns, the plotter cycles through what's there — add another color to the **Color** field if needed.

---

### 5. Removing a column from a panel

1. Select the panel.
2. In the **Columns** list, click the column you want to remove (hold Ctrl for multiple).
3. Click **Remove Selected**.

---

### 6. Reordering panels within a set

Select a panel and use **↑ Up** / **↓ Down** to move it. The order here is the order the strips appear top-to-bottom in Tab 4.

---

### 7. Creating a new Figure Set from scratch

*Example: a new set called `gas_quality` for gas supply monitoring.*

1. Type `gas_quality` in the text field below the Figure Sets list.
2. Click **+ Add Set**. The set appears in the list, selected and empty.
3. Click **+ Panel** to add the first panel. It starts with empty columns, `ylim [0, 100]`, unit `-`, color `blue`.
4. Use Search to find your columns and add them.
5. Set unit, color, and Y-axis range in Edit Panel.
6. Repeat for each panel you need.
7. Click **Save figures.json**.

---

### 8. Using `func_cyl|` for cylinder-by-cylinder data

Some data items exist once per cylinder: `Exhaust_TempCyl01`, `Exhaust_TempCyl02`, … `Exhaust_TempCyl20`. Instead of adding them one by one, use the wildcard template:

1. Search for `Exhaust_TempCyl` — you'll see `Exhaust_TempCyl*` in the results (the `*` is the cylinder placeholder).
2. Select it.
3. **Check** the `use func_cyl| prefix` checkbox.
4. Click **Add to Panel**.

The column is stored as `func_cyl|Exhaust_TempCyl*`. At plot time, this expands to all cylinders present on the specific engine loaded in Tab 1. You can see this in the existing `exhaust` set:

```json
{"col": ["func_cyl|Exhaust_TempCyl*", "Exhaust_TempCylMax", "Exhaust_TempCylMin"],
 "ylim": [0, 700], "unit": "°C"}
```

That single panel shows all individual cylinder temps plus the max and min summary lines.

---

### 9. Previewing before saving

Select a panel, enter a **Start No** (default 0, meaning the first recorded start), and click **Preview Panel**. This downloads the actual measurement data for that start and draws the panel exactly as Tab 4 would. Requires a `.dfsm` file to be loaded in Tab 1.

If the preview shows the lines squeezed together or clipped, adjust `min`/`max` and preview again.

---

### 10. Renaming or deleting a set

- **Rename:** type the new name in the text field, select the set, click **Rename**.
- **Delete:** select the set, click **Delete Set** (red button — immediate, no confirmation).

---

## `func_power` vs numeric ylim

| Setting | When to use |
|---|---|
| `func_power` | Power and setpoint panels — auto-scales to 120% of nominal engine power. Changes automatically when a different engine is loaded. |
| `numeric` | Everything else — enter min/max explicitly. |

---

## Save and reload

- **Save figures.json** — writes the in-memory state to disk and immediately reloads Tab 4's plot definitions. Changes are live for the current session.
- **Reload from disk** — discards all unsaved in-editor changes and reverts to the last saved file. Use this if you made a mistake.

Changes are only in memory until you save. Restarting the app without saving loses them.
