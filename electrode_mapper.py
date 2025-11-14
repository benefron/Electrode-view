"""
Electrode Mapper - Maps between OpenEphys electrodes, Sparrow pixels, and grid coordinates
"""
import json
from typing import Optional, Tuple, Dict, List


class ElectrodeMapper:
    """Handles mapping between different coordinate systems"""
    
    def __init__(self):
        self.mapping_data: List[Dict] = []
        self.electrode_to_data: Dict[int, Dict] = {}
        self.pixel_to_data: Dict[int, Dict] = {}
        self.coord_to_data: Dict[Tuple[int, int], Dict] = {}
        
    def load_mapping(self, filepath: str) -> bool:
        """Load mapping data from JSON file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Handle different JSON formats
            if isinstance(data, dict) and 'channels' in data:
                # Format: {"channels": [...], "pixels": [...], "coordinates": [...]}
                channels = data.get('channels', [])
                pixels = data.get('pixels', [])
                coordinates = data.get('coordinates', [])
                
                # Combine parallel arrays into list of dicts
                self.mapping_data = []
                for i in range(len(coordinates)):
                    channel = channels[i] if i < len(channels) else None
                    pixel = pixels[i] if i < len(pixels) else None
                    coord = coordinates[i]
                    
                    # Handle both uppercase and lowercase keys
                    x = coord.get('X') if coord.get('X') is not None else coord.get('x')
                    y = coord.get('Y') if coord.get('Y') is not None else coord.get('y')
                    
                    self.mapping_data.append({
                        'electrode': channel,
                        'pixel': pixel,
                        'x': x,
                        'y': y
                    })
                    
            elif isinstance(data, list):
                # Format: [{"electrode": N, "pixel": M, "x": X, "y": Y}, ...]
                self.mapping_data = data
            else:
                raise ValueError("Unsupported JSON format")
            
            # Create lookup dictionaries
            self.electrode_to_data.clear()
            self.pixel_to_data.clear()
            self.coord_to_data.clear()
            
            for item in self.mapping_data:
                # Use explicit None checks to handle 0 values correctly
                electrode = item.get('electrode')
                if electrode is None:
                    electrode = item.get('channel')
                pixel = item.get('pixel')
                x = item.get('x')
                y = item.get('y')
                
                if pixel is None or x is None or y is None:
                    continue
                
                data_entry = {
                    'electrode': electrode,
                    'pixel': pixel,
                    'x': x,
                    'y': y
                }
                
                if electrode is not None:
                    self.electrode_to_data[electrode] = data_entry
                self.pixel_to_data[pixel] = data_entry
                self.coord_to_data[(x, y)] = data_entry
            
            print(f"Loaded {len(self.coord_to_data)} electrode mappings")
            return True
        except Exception as e:
            print(f"Error loading mapping file: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_by_electrode(self, electrode: int) -> Optional[Dict]:
        """Get mapping data by OpenEphys electrode number"""
        return self.electrode_to_data.get(electrode)
    
    def get_by_pixel(self, pixel: int) -> Optional[Dict]:
        """Get mapping data by Sparrow pixel number"""
        return self.pixel_to_data.get(pixel)
    
    def get_by_coords(self, x: int, y: int) -> Optional[Dict]:
        """Get mapping data by grid coordinates"""
        return self.coord_to_data.get((x, y))
    
    def coords_to_zoom_grid(self, x: int, y: int) -> Tuple[int, int, int]:
        """
        Convert global coordinates to zoom grid number and local coordinates
        Returns: (grid_number, local_x, local_y)
        Grid numbers: 1,3,7,9,2,4,8,6,10,12,16,14,11,13,15,5
        Coordinates start from top-left (0,0)
        """
        # Determine which 16x16 grid the coordinate falls into
        grid_x = x // 16  # 0-3
        grid_y = y // 16  # 0-3
        
        # Local coordinates within the 16x16 grid
        local_x = x % 16
        local_y = y % 16
        
        # Mapping from grid position to zoom number
        # Grid layout (4x4), with (0,0) at top-left:
        # [0,0] [1,0] [2,0] [3,0]  <- row 0 (top)
        # [0,1] [1,1] [2,1] [3,1]  <- row 1
        # [0,2] [1,2] [2,2] [3,2]  <- row 2
        # [0,3] [1,3] [2,3] [3,3]  <- row 3 (bottom)
        
        # Zoom numbering (top-left to right, then next row):
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
        
        grid_number = zoom_map.get((grid_x, grid_y), 1)
        
        return grid_number, local_x, local_y
