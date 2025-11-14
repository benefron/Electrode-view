#!/usr/bin/env python3
"""Test script to verify coordinate mapping"""

from electrode_mapper import ElectrodeMapper

mapper = ElectrodeMapper()
success = mapper.load_mapping('config_ChannelRemappingInfo_9_12.json')

print(f"Loaded: {success}")
print(f"Total coordinates: {len(mapper.coord_to_data)}")
print(f"Total electrodes: {len(mapper.electrode_to_data)}")
print(f"Total pixels: {len(mapper.pixel_to_data)}")
print()

# Check coordinates with 0
print("Checking coordinates with X=0:")
for y in range(5):
    data = mapper.get_by_coords(0, y)
    if data:
        print(f"  (0,{y}): Channel={data['electrode']}, Pixel={data['pixel']}")
    else:
        print(f"  (0,{y}): NOT FOUND")

print()
print("Checking coordinates with Y=0:")
for x in range(5):
    data = mapper.get_by_coords(x, 0)
    if data:
        print(f"  ({x},0): Channel={data['electrode']}, Pixel={data['pixel']}")
    else:
        print(f"  ({x},0): NOT FOUND")

print()
print("First 10 channels:")
for ch in range(10):
    data = mapper.get_by_electrode(ch)
    if data:
        print(f"  Ch {ch}: Pixel={data['pixel']}, Coords=({data['x']},{data['y']})")
    else:
        print(f"  Ch {ch}: NOT FOUND")
