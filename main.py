"""
Main GUI Application for Electrode Visualization
"""
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFileDialog, QColorDialog,
    QComboBox, QGroupBox, QListWidget, QMessageBox, QGridLayout,
    QInputDialog
)
from PyQt5.QtCore import Qt, QRectF, pyqtSignal
from PyQt5.QtGui import QColor
import pyqtgraph as pg
from electrode_mapper import ElectrodeMapper
from selection_manager import SelectionManager, SelectionList


class GridWidget(pg.GraphicsLayoutWidget):
    """Custom widget for displaying the electrode grid"""
    
    square_clicked = pyqtSignal(int, int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.mapper = None
        self.selection_manager = None
        self.highlight_item = None
        self.current_highlight = None
        self.zoomed_grids = []  # List of grid numbers to zoom on
        self.setup_grid()
        
    def setup_grid(self):
        """Initialize the 4x4 grid layout with 16x16 squares each"""
        self.clear()
        
        # Reduce spacing between plots
        self.ci.layout.setSpacing(2)
        
        # Create 4x4 grid of plots
        # Start from top-left: row 0 = top, row 3 = bottom
        self.plots = []
        for row in range(4):
            plot_row = []
            for col in range(4):
                # Add plot with minimal spacing
                plot = self.addPlot(row=row, col=col)
                plot.setAspectLocked(True)
                plot.showGrid(x=True, y=True, alpha=0.3)
                
                # Invert Y axis so (0,0) is top-left
                plot.invertY(True)
                
                # Hide axes for cleaner look
                plot.hideAxis('left')
                plot.hideAxis('bottom')
                
                # Store plot reference with grid position
                plot.grid_col = col
                plot.grid_row = row  # row 0 is now top
                
                # Calculate and store grid number
                # Top-left to right, then next row
                # Grid layout (top to bottom, left to right):
                # 1  3  7  5     (row 0)
                # 2  4  8  6     (row 1)
                # 10 12 16 14    (row 2)
                # 9 11 15 13     (row 3)
                zoom_map = {
                    (0, 0): 1,  (1, 0): 3,  (2, 0): 7,  (3, 0): 5,
                    (0, 1): 2,  (1, 1): 4,  (2, 1): 8,  (3, 1): 6,
                    (0, 2): 10, (1, 2): 12, (2, 2): 16, (3, 2): 14,
                    (0, 3): 9,  (1, 3): 11, (2, 3): 15, (3, 3): 13,
                }
                plot.grid_number = zoom_map.get((col, row), 0)
                
                # Add grid number label
                text = pg.TextItem(str(plot.grid_number), anchor=(1, 0.5))
                text.setPos(-1, 8)
                plot.addItem(text)
                
                plot_row.append(plot)
                
                # Create scatter plot for the squares
                scatter = pg.ScatterPlotItem(size=10, pen=pg.mkPen(None))
                plot.addItem(scatter)
                plot.scatter = scatter
                
                # Create highlight scatter (initially empty)
                highlight = pg.ScatterPlotItem(
                    size=15,
                    pen=pg.mkPen('y', width=3),
                    brush=pg.mkBrush(None)
                )
                plot.addItem(highlight)
                plot.highlight = highlight
                
                # Connect click events
                scatter.sigClicked.connect(self.on_square_clicked)
                
            self.plots.append(plot_row)
        
        self.update_grid()
        
    def highlight_square(self, x, y):
        """Highlight a specific square on the grid"""
        self.current_highlight = (x, y)
        
        # Determine which grid and local position
        grid_col = x // 16
        grid_row = y // 16
        local_x = x % 16
        local_y = y % 16
        
        # Clear all highlights
        for row in self.plots:
            for plot in row:
                plot.highlight.setData(spots=[])
        
        # Set highlight on the correct grid
        if 0 <= grid_row < 4 and 0 <= grid_col < 4:
            plot = self.plots[grid_row][grid_col]
            plot.highlight.setData(spots=[{
                'pos': (local_x, local_y),
                'size': 15
            }])
    
    def clear_highlight(self):
        """Clear the highlight from all grids"""
        self.current_highlight = None
        for row in self.plots:
            for plot in row:
                plot.highlight.setData(spots=[])
    
    def set_zoom(self, grid_numbers):
        """Zoom on specific grids by their numbers (1-16)"""
        self.zoomed_grids = grid_numbers if grid_numbers else []
        
        if not self.zoomed_grids:
            # Reset all views - show all grids with auto-fit
            for row in self.plots:
                for plot in row:
                    plot.setVisible(True)
                    plot.autoRange(padding=0.05)
            return
        
        # Create a mapping of grid numbers to their row/col positions
        grid_positions = {}
        for row in self.plots:
            for plot in row:
                grid_positions[plot.grid_number] = (
                    plot.grid_row, plot.grid_col
                )
        
        # Get the positions of zoomed grids
        zoomed_positions = [
            grid_positions[gn] for gn in self.zoomed_grids
            if gn in grid_positions
        ]
        
        if not zoomed_positions:
            return
        
        # Calculate bounding box of zoomed grids
        rows = [pos[0] for pos in zoomed_positions]
        cols = [pos[1] for pos in zoomed_positions]
        min_row, max_row = min(rows), max(rows)
        min_col, max_col = min(cols), max(cols)
        
        # Show/hide grids based on whether they're in the bounding box
        for row in self.plots:
            for plot in row:
                # Show grid if it's in the bounding box area
                in_bbox = (min_row <= plot.grid_row <= max_row and
                          min_col <= plot.grid_col <= max_col)
                
                if in_bbox:
                    plot.setVisible(True)
                    plot.autoRange(padding=0.05)
                else:
                    plot.setVisible(False)
        
    def on_square_clicked(self, scatter, points):
        """Handle click on a square"""
        if len(points) > 0:
            point = points[0]
            pos = point.pos()
            
            # Get the plot that contains this scatter
            plot = None
            for row in self.plots:
                for p in row:
                    if p.scatter == scatter:
                        plot = p
                        break
                if plot:
                    break
            
            if plot:
                # Convert to global coordinates
                local_x = int(pos.x())
                local_y = int(pos.y())
                global_x = plot.grid_col * 16 + local_x
                global_y = plot.grid_row * 16 + local_y
                
                self.square_clicked.emit(global_x, global_y)
    
    def update_grid(self):
        """Update the grid visualization with current selections"""
        if not self.mapper or not self.selection_manager:
            return
        
        for row_idx, row in enumerate(self.plots):
            for col_idx, plot in enumerate(row):
                spots = []
                
                # Create spots for all 16x16 squares in this grid
                for local_y in range(16):
                    for local_x in range(16):
                        # Calculate global coordinates
                        global_x = col_idx * 16 + local_x
                        global_y = row_idx * 16 + local_y
                        
                        # Check if this coordinate has a selection color
                        color = self.selection_manager.get_color_at(
                            global_x, global_y
                        )
                        
                        if color:
                            brush = pg.mkBrush(color)
                        else:
                            # Default gray color for unselected squares
                            brush = pg.mkBrush(200, 200, 200, 100)
                        
                        spots.append({
                            'pos': (local_x, local_y),
                            'brush': brush
                        })
                
                plot.scatter.setData(spots=spots)
                
                # Auto-fit the view to show all data
                plot.autoRange(padding=0.05)
    
    def set_mapper(self, mapper: ElectrodeMapper):
        """Set the electrode mapper"""
        self.mapper = mapper
        self.update_grid()
        
    def set_selection_manager(self, manager: SelectionManager):
        """Set the selection manager"""
        self.selection_manager = manager
        self.update_grid()


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.mapper = ElectrodeMapper()
        self.selection_manager = SelectionManager()
        self.current_coord = None
        
        self.setWindowTitle("Electrode Mapper")
        self.setGeometry(100, 100, 1400, 900)
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        
        # Left side: Grid visualization
        self.grid_widget = GridWidget()
        self.grid_widget.set_mapper(self.mapper)
        self.grid_widget.set_selection_manager(self.selection_manager)
        self.grid_widget.square_clicked.connect(self.on_grid_square_clicked)
        main_layout.addWidget(self.grid_widget, stretch=3)
        
        # Right side: Controls
        controls_layout = QVBoxLayout()
        main_layout.addLayout(controls_layout, stretch=1)
        
        # File loading
        file_group = QGroupBox("Configuration")
        file_layout = QVBoxLayout()
        load_btn = QPushButton("Load Mapping JSON")
        load_btn.clicked.connect(self.load_mapping)
        file_layout.addWidget(load_btn)
        file_group.setLayout(file_layout)
        controls_layout.addWidget(file_group)
        
        # Coordinate input group
        coord_group = QGroupBox("Coordinate Selection")
        coord_layout = QVBoxLayout()
        
        # OpenEphys electrode input
        ephys_layout = QHBoxLayout()
        ephys_layout.addWidget(QLabel("OpenEphys:"))
        self.ephys_input = QLineEdit()
        self.ephys_input.textChanged.connect(self.on_ephys_changed)
        ephys_layout.addWidget(self.ephys_input)
        coord_layout.addLayout(ephys_layout)
        
        # Sparrow pixel input
        pixel_layout = QHBoxLayout()
        pixel_layout.addWidget(QLabel("Sparrow Pixel:"))
        self.pixel_input = QLineEdit()
        self.pixel_input.textChanged.connect(self.on_pixel_changed)
        pixel_layout.addWidget(self.pixel_input)
        coord_layout.addLayout(pixel_layout)
        
        # Grid coordinates display
        grid_layout = QHBoxLayout()
        grid_layout.addWidget(QLabel("Grid (X,Y):"))
        self.grid_display = QLabel("---, ---")
        grid_layout.addWidget(self.grid_display)
        coord_layout.addLayout(grid_layout)
        
        # Zoom display
        zoom_layout = QHBoxLayout()
        zoom_layout.addWidget(QLabel("Zoom Grid:"))
        self.zoom_display = QLabel("---")
        zoom_layout.addWidget(self.zoom_display)
        coord_layout.addLayout(zoom_layout)
        
        # Zoom input
        zoom_input_layout = QHBoxLayout()
        zoom_input_layout.addWidget(QLabel("Zoom to Grid(s):"))
        self.zoom_input = QLineEdit()
        self.zoom_input.setPlaceholderText("e.g., 1,3,7 or leave empty")
        zoom_input_layout.addWidget(self.zoom_input)
        coord_layout.addLayout(zoom_input_layout)
        
        # Zoom buttons
        zoom_btn_layout = QHBoxLayout()
        apply_zoom_btn = QPushButton("Apply Zoom")
        apply_zoom_btn.clicked.connect(self.apply_zoom)
        reset_zoom_btn = QPushButton("Reset Zoom")
        reset_zoom_btn.clicked.connect(self.reset_zoom)
        zoom_btn_layout.addWidget(apply_zoom_btn)
        zoom_btn_layout.addWidget(reset_zoom_btn)
        coord_layout.addLayout(zoom_btn_layout)
        
        coord_group.setLayout(coord_layout)
        controls_layout.addWidget(coord_group)
        
        # Selection list management
        list_group = QGroupBox("Selection Lists")
        list_layout = QVBoxLayout()
        
        # Current list selector
        list_select_layout = QHBoxLayout()
        list_select_layout.addWidget(QLabel("Current List:"))
        self.list_combo = QComboBox()
        self.list_combo.currentIndexChanged.connect(self.on_list_changed)
        list_select_layout.addWidget(self.list_combo)
        list_layout.addLayout(list_select_layout)
        
        # Add/Remove buttons for current coordinate
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add to List")
        add_btn.clicked.connect(self.add_to_list)
        remove_btn = QPushButton("Remove from List")
        remove_btn.clicked.connect(self.remove_from_list)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(remove_btn)
        list_layout.addLayout(btn_layout)
        
        # List management buttons
        mgmt_layout = QHBoxLayout()
        new_list_btn = QPushButton("New List")
        new_list_btn.clicked.connect(self.create_new_list)
        delete_list_btn = QPushButton("Delete List")
        delete_list_btn.clicked.connect(self.delete_current_list)
        mgmt_layout.addWidget(new_list_btn)
        mgmt_layout.addWidget(delete_list_btn)
        list_layout.addLayout(mgmt_layout)
        
        # Coordinates in current list
        list_layout.addWidget(QLabel("Coordinates in list:"))
        self.coord_list_widget = QListWidget()
        list_layout.addWidget(self.coord_list_widget)
        
        # Save lists button
        save_lists_btn = QPushButton("Save Lists to JSON")
        save_lists_btn.clicked.connect(self.save_selection_lists)
        list_layout.addWidget(save_lists_btn)
        
        # Load lists button
        load_lists_btn = QPushButton("Load Lists from JSON")
        load_lists_btn.clicked.connect(self.load_selection_lists)
        list_layout.addWidget(load_lists_btn)
        
        list_group.setLayout(list_layout)
        controls_layout.addWidget(list_group)
        
        controls_layout.addStretch()
        
    def load_mapping(self):
        """Load electrode mapping from JSON file"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Load Mapping JSON", "", "JSON Files (*.json)"
        )
        if filename:
            if self.mapper.load_mapping(filename):
                QMessageBox.information(
                    self, "Success", "Mapping loaded successfully!"
                )
                self.grid_widget.update_grid()
            else:
                QMessageBox.warning(
                    self, "Error", "Failed to load mapping file."
                )
    
    def on_ephys_changed(self, text):
        """Handle OpenEphys electrode input change"""
        if not text or not text.isdigit():
            self.clear_coordinate_display()
            return
            
        electrode = int(text)
        data = self.mapper.get_by_electrode(electrode)
        
        if data:
            # Block signals to prevent recursion
            self.pixel_input.blockSignals(True)
            self.pixel_input.setText(str(data['pixel']))
            self.pixel_input.blockSignals(False)
            
            self.update_coordinate_display(data['x'], data['y'])
            self.highlight_square(data['x'], data['y'])
        else:
            self.clear_coordinate_display()
    
    def on_pixel_changed(self, text):
        """Handle Sparrow pixel input change"""
        if not text or not text.isdigit():
            self.clear_coordinate_display()
            return
            
        pixel = int(text)
        data = self.mapper.get_by_pixel(pixel)
        
        if data:
            # Block signals to prevent recursion
            self.ephys_input.blockSignals(True)
            if data['electrode'] is not None:
                self.ephys_input.setText(str(data['electrode']))
            else:
                self.ephys_input.setText("")
            self.ephys_input.blockSignals(False)
            
            self.update_coordinate_display(data['x'], data['y'])
            self.highlight_square(data['x'], data['y'])
        else:
            self.clear_coordinate_display()
    
    def on_grid_square_clicked(self, x, y):
        """Handle click on grid square"""
        data = self.mapper.get_by_coords(x, y)
        
        if data:
            # Update input fields
            self.ephys_input.blockSignals(True)
            self.pixel_input.blockSignals(True)
            
            if data['electrode'] is not None:
                self.ephys_input.setText(str(data['electrode']))
            else:
                self.ephys_input.setText("")
            self.pixel_input.setText(str(data['pixel']))
            
            self.ephys_input.blockSignals(False)
            self.pixel_input.blockSignals(False)
            
            self.update_coordinate_display(x, y)
            self.highlight_square(x, y)
    
    def update_coordinate_display(self, x, y):
        """Update the coordinate display fields"""
        self.current_coord = (x, y)
        self.grid_display.setText(f"{x}, {y}")
        
        # Calculate zoom grid
        grid_num, local_x, local_y = self.mapper.coords_to_zoom_grid(x, y)
        self.zoom_display.setText(
            f"Grid {grid_num} ({local_x}, {local_y})"
        )
    
    def clear_coordinate_display(self):
        """Clear the coordinate display fields"""
        self.current_coord = None
        self.grid_display.setText("---, ---")
        self.zoom_display.setText("---")
        self.grid_widget.clear_highlight()
    
    def highlight_square(self, x, y):
        """Highlight a specific square on the grid"""
        self.grid_widget.highlight_square(x, y)
    
    def create_new_list(self):
        """Create a new selection list"""
        # Get list name from user
        name, ok = QInputDialog.getText(
            self, "New List", "Enter list name:"
        )
        if not ok or not name:
            return
        
        # Get color from user
        color = QColorDialog.getColor()
        if color.isValid():
            self.selection_manager.create_list(name, color)
            self.list_combo.addItem(name)
            idx = len(self.selection_manager.lists) - 1
            self.list_combo.setCurrentIndex(idx)
            self.update_list_display()
    
    def delete_current_list(self):
        """Delete the currently selected list"""
        if self.selection_manager.current_list:
            self.selection_manager.remove_list(
                self.selection_manager.current_list
            )
            self.list_combo.removeItem(self.list_combo.currentIndex())
            self.update_list_display()
            self.grid_widget.update_grid()
    
    def on_list_changed(self, index):
        """Handle selection list change"""
        if 0 <= index < len(self.selection_manager.lists):
            self.selection_manager.current_list = (
                self.selection_manager.lists[index]
            )
            self.update_list_display()
    
    def add_to_list(self):
        """Add current coordinate to current list"""
        if not self.current_coord:
            QMessageBox.warning(
                self, "No Coordinate", "Please select a coordinate first."
            )
            return
            
        if not self.selection_manager.current_list:
            QMessageBox.warning(
                self, "No List", "Please create a list first."
            )
            return
        
        x, y = self.current_coord
        self.selection_manager.current_list.add_coordinate(x, y)
        self.update_list_display()
        self.grid_widget.update_grid()
    
    def remove_from_list(self):
        """Remove current coordinate from current list"""
        if not self.current_coord:
            QMessageBox.warning(
                self, "No Coordinate", "Please select a coordinate first."
            )
            return
            
        if not self.selection_manager.current_list:
            return
        
        x, y = self.current_coord
        self.selection_manager.current_list.remove_coordinate(x, y)
        self.update_list_display()
        self.grid_widget.update_grid()
    
    def update_list_display(self):
        """Update the list widget showing coordinates"""
        self.coord_list_widget.clear()
        
        if self.selection_manager.current_list:
            for x, y in self.selection_manager.current_list.coordinates:
                self.coord_list_widget.addItem(f"({x}, {y})")
    
    def save_selection_lists(self):
        """Save selection lists to JSON file"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Selection Lists", "", "JSON Files (*.json)"
        )
        if filename:
            if self.selection_manager.save_to_file(filename):
                QMessageBox.information(
                    self, "Success", "Selection lists saved successfully!"
                )
            else:
                QMessageBox.warning(
                    self, "Error", "Failed to save selection lists."
                )
    
    def load_selection_lists(self):
        """Load selection lists from JSON file"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Load Selection Lists", "", "JSON Files (*.json)"
        )
        if filename:
            if self.selection_manager.load_from_file(filename):
                # Update combo box
                self.list_combo.clear()
                for lst in self.selection_manager.lists:
                    self.list_combo.addItem(lst.name)
                
                if self.selection_manager.lists:
                    self.list_combo.setCurrentIndex(0)
                
                self.update_list_display()
                self.grid_widget.update_grid()
                
                QMessageBox.information(
                    self, "Success", "Selection lists loaded successfully!"
                )
            else:
                QMessageBox.warning(
                    self, "Error", "Failed to load selection lists."
                )
    
    def apply_zoom(self):
        """Apply zoom to specified grids"""
        zoom_text = self.zoom_input.text().strip()
        
        if not zoom_text:
            self.reset_zoom()
            return
        
        try:
            # Parse grid numbers - support both comma-separated and ranges
            grid_numbers = []
            parts = zoom_text.split(',')
            
            for part in parts:
                part = part.strip()
                if '-' in part:
                    # Handle range like "1-4"
                    start, end = part.split('-', 1)
                    start = int(start.strip())
                    end = int(end.strip())
                    if start > end:
                        start, end = end, start
                    grid_numbers.extend(range(start, end + 1))
                else:
                    # Single number
                    grid_numbers.append(int(part))
            
            # Remove duplicates and sort
            grid_numbers = sorted(set(grid_numbers))
            
            # Validate grid numbers (1-16)
            invalid = [n for n in grid_numbers if n < 1 or n > 16]
            if invalid:
                QMessageBox.warning(
                    self, "Invalid Grid Numbers",
                    f"Grid numbers must be 1-16. Invalid: {invalid}"
                )
                return
            
            self.grid_widget.set_zoom(grid_numbers)
            
        except ValueError:
            QMessageBox.warning(
                self, "Invalid Input",
                "Enter numbers/ranges (e.g., 1,3,7 or 1-4)"
            )
    
    def reset_zoom(self):
        """Reset zoom to show all grids"""
        self.zoom_input.clear()
        self.grid_widget.set_zoom([])


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
