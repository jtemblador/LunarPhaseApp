#!/usr/bin/env python3
# explore_api_response.py

import json
import sys
from typing import Any, Dict, List, Optional, Union

def safe_get(data: Dict[str, Any], path: List[Union[str, int]]) -> Optional[Any]:
    """
    Safely navigate through a nested structure using a path.
    Returns None if the path doesn't exist.
    """
    current = data
    path_str = ""
    
    try:
        for i, key in enumerate(path):
            path_str += f"['{key}']" if isinstance(key, str) else f"[{key}]"
            
            if isinstance(current, dict) and key in current:
                current = current[key]
            elif isinstance(current, list) and isinstance(key, int) and 0 <= key < len(current):
                current = current[key]
            else:
                print(f"Path 'data{path_str}' doesn't exist (stopped at element {i})")
                return None
        return current
    except Exception as e:
        print(f"Error accessing 'data{path_str}': {str(e)}")
        return None

def explore_path(data: Dict[str, Any], base_path: List[Union[str, int]], max_depth: int = 3) -> None:
    """
    Explore different variations of a base path up to a certain depth.
    Prints values found at each path.
    """
    # Print value at the base path
    value = safe_get(data, base_path)
    if value is not None:
        path_str = "data" + "".join(f"['{k}']" if isinstance(k, str) else f"[{k}]" for k in base_path)
        
        # For dictionaries, print keys
        if isinstance(value, dict):
            print(f"\n{path_str} is a dictionary with keys: {list(value.keys())}")
            
            # Print a preview of each key-value pair
            for k, v in value.items():
                preview = str(v)
                if len(preview) > 100:
                    preview = preview[:97] + "..."
                print(f"  - {k}: {preview}")
        
        # For lists, print length and preview
        elif isinstance(value, list):
            print(f"\n{path_str} is a list with {len(value)} items")
            
            # Print preview of up to 5 items
            for i, item in enumerate(value[:5]):
                preview = str(item)
                if len(preview) > 100:
                    preview = preview[:97] + "..."
                print(f"  - Item {i}: {preview}")
            
            if len(value) > 5:
                print(f"  ... ({len(value) - 5} more items)")
        
        # For other types, print the value
        else:
            print(f"\n{path_str} = {value}")
    
    # If we've reached the max depth, don't go deeper
    if len(base_path) >= max_depth:
        return
    
    # Try variations with different indices
    if safe_get(data, base_path) is not None:
        current = safe_get(data, base_path)
        
        # If the current value is a list, explore its items
        if isinstance(current, list):
            for i in range(min(len(current), 5)):  # Limit to first 5 items
                new_path = base_path + [i]
                explore_path(data, new_path, max_depth)
        
        # If the current value is a dictionary, explore its keys
        elif isinstance(current, dict):
            for key in current.keys():
                new_path = base_path + [key]
                explore_path(data, new_path, max_depth)

def main() -> None:
    # Load the API response from file
    try:
        with open("api_response.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: api_response.json file not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print("Error: api_response.json is not valid JSON.")
        sys.exit(1)
    
    print("===== API RESPONSE STRUCTURE EXPLORER =====\n")
    print(f"Exploring api_response.json...")
    
    # Explore specific paths of interest
    paths_to_explore = [
        ["data", "table", "rows"],
        ["data", "table", "header"],
        ["data", "observer"],
        ["data", "dates"]
    ]
    
    for path in paths_to_explore:
        explore_path(data, path)
    
    # Explore all rows and cells systematically
    rows = safe_get(data, ["data", "table", "rows"])
    if rows and isinstance(rows, list):
        for row_idx in range(len(rows)):
            # Get cells for this row
            cells = safe_get(data, ["data", "table", "rows", row_idx, "cells"])
            if cells and isinstance(cells, list):
                for cell_idx in range(len(cells)):
                    path = ["data", "table", "rows", row_idx, "cells", cell_idx]
                    
                    cell_data = safe_get(data, path)
                    if cell_data:
                        path_str = "data" + "".join(f"['{k}']" if isinstance(k, str) else f"[{k}]" for k in path)
                        print(f"\n{path_str} contains:")
                        
                        # Print name/id if available
                        name = cell_data.get("name", "Unknown")
                        cell_id = cell_data.get("id", "Unknown")
                        print(f"  - Name: {name}, ID: {cell_id}")
                        
                        # Print summary of available data sections
                        for section in ["distance", "position", "extraInfo"]:
                            if section in cell_data:
                                print(f"  - Has {section} data")
    
    print("\n===== EXPLORATION COMPLETE =====")

if __name__ == "__main__":
    main()