#!/usr/bin/env python3
# main.py

import os
import sys
import time
import argparse
from datetime import datetime
from typing import Dict, Any, Optional

# Import configuration
import config

# Import backend modules
from backend.location_service import LocationService
from backend.lunar_data import LunarDataService
from backend.data_processor import LunarDataProcessor

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def display_header():
    """Display the application header."""
    print("\n" + "=" * 80)
    print("LUNAR OBSERVER - Terminal Edition".center(80))
    print("A tool to visualize the moon based on your location".center(80))
    print("=" * 80 + "\n")

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Lunar Observer - Terminal Edition")
    parser.add_argument("-l", "--location", type=str, help="Location (e.g., 'Los Angeles, CA')")
    parser.add_argument("-c", "--no-color", action="store_true", help="Disable color output")
    parser.add_argument("-v", "--version", action="store_true", help="Show version information")
    
    return parser.parse_args()

def main():
    """Main application function."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Display version if requested
    if args.version:
        from backend import __version__
        print(f"Lunar Observer - Terminal Edition v{__version__}")
        return
    
    # Clear screen and display header
    clear_screen()
    display_header()

    print("\nInitializing with API credentials:")
    print(f"App ID: {config.ASTRONOMY_APP_ID[:6]}...")  # Only print first 6 chars for security
    print(f"Base URL: {config.ASTRONOMY_API_BASE_URL}")
    
    # Create service instances
    location_service = LocationService()
    lunar_service = LunarDataService(
        app_id=config.ASTRONOMY_APP_ID,
        app_secret=config.ASTRONOMY_APP_SECRET,
        base_url=config.ASTRONOMY_API_BASE_URL
    )
    data_processor = LunarDataProcessor(
        terminal_width=config.TERMINAL_WIDTH,
        enable_color=not args.no_color
    )
    
    try:
        # Get location - either from args or prompt user
        if args.location:
            location_data = location_service.get_coordinates(args.location)
        else:
            print("Welcome to Lunar Observer - Terminal Edition!")
            print("This tool shows accurate lunar data for your location.\n")
            location_data = location_service.get_user_location_input()
        
        # Display location information
        print("\n" + location_service.format_location_info(location_data))
        
        # Get lunar data
        lunar_data = lunar_service.get_moon_data(
            latitude=location_data["latitude"],
            longitude=location_data["longitude"]
        )
        
        # Process and display lunar data
        formatted_data = data_processor.format_lunar_data(lunar_data)
        print("\n" + formatted_data)
        
        # Ask if user wants to check another location
        while True:
            print("\nOptions:")
            print("1. Check another location")
            print("2. Exit")
            
            choice = input("Enter your choice (1-2): ")
            
            if choice == "1":
                clear_screen()
                display_header()
                location_data = location_service.get_user_location_input()
                print("THIS IS THE ADDRESS" + location_data["address"])
                print("\n" + location_service.format_location_info(location_data))
                
                lunar_data = lunar_service.get_moon_data(
                    latitude=location_data["latitude"],
                    longitude=location_data["longitude"]
                )
                
                formatted_data = data_processor.format_lunar_data(lunar_data)
                print("\n" + formatted_data)
            elif choice == "2":
                print("\nThank you for using Lunar Observer!")
                break
            else:
                print("Invalid choice. Please try again.")
                
    except KeyboardInterrupt:
        print("\n\nExiting Lunar Observer. Goodbye!")
    except Exception as e:
        print(f"\nError: {str(e)}")
        print("Please check your internet connection and API credentials.")
        sys.exit(1)

if __name__ == "__main__":
    main()