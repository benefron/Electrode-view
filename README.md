# Electrode Mapper GUI

A desktop GUI tool for visualizing and interactively managing electrode mappings in neuroscience recording experiments. Built with PyQt5 and PyQtGraph, it bridges three coordinate systems used in multi-electrode array setups: **OpenEphys** electrode channels, **Sparrow** pixel addresses, and physical **grid coordinates**.

---

## Background

Multi-electrode array (MEA) experiments require researchers to keep track of hundreds of electrodes across multiple coordinate systems simultaneously. This tool was built to replace error-prone manual lookups by providing a real-time visual interface where clicking on any electrode in the spatial grid instantly resolves its identity across all three systems.

---

## Features

- **64×64 Spatial Grid**: 4×4 layout of 16×16 sub-grids renders the full electrode field at a glance
- **Bi-directional Lookup**: Type an OpenEphys channel number or a Sparrow pixel number — all other fields auto-fill instantly
- **Click-to-Select**: Click any grid square to resolve its full mapping (electrode ↔ pixel ↔ x,y)
- **Multi-List Selection**: Create named selection groups with custom colors to mark electrode subsets
- **JSON Import/Export**: Load electrode mappings from JSON; save and reload selection lists between sessions
- **Zoom Grid Labels**: Each sub-grid displays its zoom number and local coordinates for hardware reference

---

## Tech Stack

| Layer | Technology |
|---|---|
| GUI framework | PyQt5 |
| Plotting / grid rendering | PyQtGraph |
| Numerical operations | NumPy |
| Data format | JSON |
| Language | Python 3.10+ |

---

## Installation

### Option 1 — Conda (Recommended)

```bash
conda create -n electrode_mapper python=3.10 -y
conda activate electrode_mapper
conda install -c conda-forge pyqt pyqtgraph numpy -y
```

### Option 2 — pip

```bash
pip install -r requirements.txt
```

---

## Running

```bash
conda activate electrode_mapper   # if using conda
python main.py
```

---

## Usage

### 1. Load an Electrode Mapping

Click **Load Mapping JSON** and select a file in one of the supported formats:

```json
[
  { "electrode": 1, "channel": 1, "pixel": 100, "x": 5, "y": 10 },
  ...
]
```

The grid populates automatically once the file is loaded.

### 2. Look Up an Electrode

- Type an **OpenEphys electrode number** → pixel and coordinates auto-fill
- Type a **Sparrow pixel number** → electrode and coordinates auto-fill
- **Click a grid square** → all fields auto-fill

### 3. Build Selection Lists

1. Click **New List** and pick a color
2. Select coordinates using any input method
3. Click **Add to List** / **Remove from List** to manage membership
4. Use the dropdown to switch between lists; **Delete List** removes the active list

### 4. Save / Load Lists

- **Save Lists to JSON** — exports all selection lists to a file
- **Load Lists from JSON** — restores a previously saved session

Exported format:

```json
{
  "selection_lists": [
    {
      "name": "Region A",
      "color": [255, 0, 0],
      "coordinates": [[5, 10], [6, 11]]
    }
  ]
}
```

### Zoom Grid Numbering

Each of the 16 sub-grids is assigned a hardware zoom number (1–16). The layout:

```
 1   3   7   9
 2   4   8   6
10  12  16  14
11  13  15   5
```

Local coordinates within each sub-grid run from (0,0) to (15,15).

---

## Project Structure

```
.
├── main.py                          # GUI application and event handling
├── electrode_mapper.py              # Coordinate mapping logic (electrode ↔ pixel ↔ grid)
├── selection_manager.py             # Selection list state management
├── elecmap.py                       # Electrode map utilities
├── config_ChannelRemappingInfo_1_4.json   # Channel remapping config (channels 1–4)
├── config_ChannelRemappingInfo_9_12.json  # Channel remapping config (channels 9–12)
├── requirements.txt                 # pip dependencies
├── CONDA_SETUP.md                   # Conda environment reference
└── README.md                        # This file
```

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| Grid is blank after launch | Load a mapping JSON file first |
| Fields don't auto-fill when typing | Verify the electrode/pixel number exists in the loaded mapping |
| Selection colors not visible | Confirm coordinates have been added to a list and the list is active |

---

## License

MIT License — free to use and modify.
