"""
Selection List Manager - Manages multiple selection lists with colors and names
"""
import json
from typing import List, Dict, Tuple
from PyQt5.QtGui import QColor


class SelectionList:
    """Represents a single selection list with coordinates, color, and name"""
    
    def __init__(self, name: str = "List", color: QColor = None):
        self.name = name
        self.color = color or QColor(255, 0, 0)
        self.coordinates: List[Tuple[int, int]] = []
        
    def add_coordinate(self, x: int, y: int):
        """Add a coordinate to the list if not already present"""
        if (x, y) not in self.coordinates:
            self.coordinates.append((x, y))
            
    def remove_coordinate(self, x: int, y: int):
        """Remove a coordinate from the list"""
        if (x, y) in self.coordinates:
            self.coordinates.remove((x, y))
            
    def has_coordinate(self, x: int, y: int) -> bool:
        """Check if coordinate is in the list"""
        return (x, y) in self.coordinates
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON export"""
        return {
            'name': self.name,
            'color': [self.color.red(), self.color.green(), self.color.blue()],
            'coordinates': self.coordinates
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'SelectionList':
        """Create SelectionList from dictionary"""
        color_values = data.get('color', [255, 0, 0])
        color = QColor(color_values[0], color_values[1], color_values[2])
        selection_list = SelectionList(data['name'], color)
        selection_list.coordinates = [tuple(coord) for coord in data['coordinates']]
        return selection_list


class SelectionManager:
    """Manages multiple selection lists"""
    
    def __init__(self):
        self.lists: List[SelectionList] = []
        self.current_list: SelectionList = None
        
    def create_list(self, name: str, color: QColor) -> SelectionList:
        """Create a new selection list"""
        new_list = SelectionList(name, color)
        self.lists.append(new_list)
        self.current_list = new_list
        return new_list
    
    def remove_list(self, selection_list: SelectionList):
        """Remove a selection list"""
        if selection_list in self.lists:
            self.lists.remove(selection_list)
            if self.current_list == selection_list:
                self.current_list = self.lists[0] if self.lists else None
                
    def get_color_at(self, x: int, y: int) -> QColor:
        """Get the color of the topmost list containing this coordinate"""
        for selection_list in reversed(self.lists):
            if selection_list.has_coordinate(x, y):
                return selection_list.color
        return None
    
    def save_to_file(self, filepath: str) -> bool:
        """Save all selection lists to JSON file"""
        try:
            data = {
                'selection_lists': [lst.to_dict() for lst in self.lists]
            }
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving selection lists: {e}")
            return False
    
    def load_from_file(self, filepath: str) -> bool:
        """Load selection lists from JSON file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            self.lists.clear()
            for list_data in data.get('selection_lists', []):
                self.lists.append(SelectionList.from_dict(list_data))
            
            self.current_list = self.lists[0] if self.lists else None
            return True
        except Exception as e:
            print(f"Error loading selection lists: {e}")
            return False
