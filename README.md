# Electrode Mapper GUI

A PyQt5-based GUI application for visualizing and managing electrode mappings between OpenEphys electrodes, Sparrow pixels, and grid coordinates.

## Features

- **4x4 Grid Visualization**: Displays 16 grids (4x4 layout), each containing 16x16 squares (total 64x64 coordinate space)
- **Coordinate Mapping**: Maps between three coordinate systems:
  - OpenEphys electrode numbers
  - Sparrow pixel numbers
  - Grid coordinates (0,0 to 63,63)
- **Interactive Selection**: Click on grid squares to select electrodes
- **Multiple Selection Lists**: Create multiple selection lists with custom colors
- **Auto-complete Inputs**: Enter electrode or pixel number and the other fields auto-fill
- **Zoom Grid Display**: Shows zoom grid numbers (1-16) with local coordinates
- **JSON Import/Export**: Load electrode mappings and save/load selection lists

## Installation

### Requirements
- Python 3.10 or higher
- Conda package manager
- PyQt5
- PyQtGraph
- NumPy

### Setup

#### Using Conda (Recommended)

1. Create and activate the conda environment:
```bash
conda create -n electrode_mapper python=3.10 -y
conda activate electrode_mapper
```

2. Install dependencies:
```bash
conda install -c conda-forge pyqt pyqtgraph numpy -y
```

#### Using pip (Alternative)

```bash
pip install -r requirements.txt
```

## Usage

### Running the Application

Make sure to activate the conda environment first:

```bash
conda activate electrode_mapper
python main.py
```

### Loading Electrode Mapping

1. Click "Load Mapping JSON" button
2. Select your electrode mapping JSON file (format: `[{"electrode": N, "pixel": M, "x": X, "y": Y}, ...]`)
3. The grid will display all mapped coordinates

### Working with Coordinates

**Input Methods:**
- **Type OpenEphys electrode number**: Sparrow pixel and coordinates auto-fill
- **Type Sparrow pixel number**: OpenEphys electrode and coordinates auto-fill
- **Click grid square**: All fields auto-fill

### Creating Selection Lists

1. Click "New List" button
2. Choose a color from the color picker
3. Select coordinates (via any input method)
4. Click "Add to List" to add the coordinate to the current list
5. Click "Remove from List" to remove the coordinate

### Managing Lists

- **Switch Lists**: Use the dropdown to switch between lists
- **Delete List**: Click "Delete List" to remove the current list
- **View Coordinates**: The list widget shows all coordinates in the current list

### Saving and Loading Lists

- **Save**: Click "Save Lists to JSON" to export all selection lists
- **Load**: Click "Load Lists from JSON" to import previously saved lists

### Zoom Grid System

The zoom feature uses a special grid numbering system (1-16) for the 16 individual grids:

```
Grid Layout (Top to Bottom, Left to Right):
 1   3   7   9
 2   4   8   6
10  12  16  14
11  13  15   5
```

Each grid has local coordinates from (0,0) to (15,15).

## File Structure

```
.
├── main.py                  # Main GUI application
├── electrode_mapper.py      # Coordinate mapping logic
├── selection_manager.py     # Selection list management
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## JSON File Formats

### Electrode Mapping (Input)
```json
[
  {
    "electrode": 1,
    "channel": 1,
    "pixel": 100,
    "x": 5,
    "y": 10
  },
  ...
]
```

### Selection Lists (Export/Import)
```json
{
  "selection_lists": [
    {
      "name": "List 1",
      "color": [255, 0, 0],
      "coordinates": [[5, 10], [6, 11], ...]
    },
    ...
  ]
}
```

## Troubleshooting

**Grid not displaying**: Make sure you've loaded a mapping JSON file first

**Coordinates not auto-filling**: Verify the electrode/pixel number exists in your mapping file

**Colors not showing**: Ensure you've added coordinates to a list and the list has been created

## License

This project is provided as-is for electrode mapping visualization purposes.
