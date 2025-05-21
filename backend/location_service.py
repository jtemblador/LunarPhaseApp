import requests
from geopy.geocoders import Nominatim
import sys
import time
from typing import Dict, Any, Tuple, Optional

class LocationService:
    """Service for handling location data and geocoding."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the location service.
        
        Args:
            api_key: Optional API key for geocoding service
        """
        self.api_key = api_key
        # Use Nominatim as default geocoder (no API key required)
        self.geolocator = Nominatim(user_agent="lunar_observer")
        
    def get_coordinates(self, location_name: str) -> Dict[str, Any]:
        """
        Convert a location name to geographic coordinates.
        
        Args:
            location_name: Name of the location (e.g., "Los Angeles, CA")
            
        Returns:
            Dictionary with latitude, longitude, and formatted address
            
        Raises:
            ValueError: If location cannot be found
        """
        try:
            print(f"Finding coordinates for {location_name}...", end="", flush=True)
            location = self.geolocator.geocode(location_name)
            
            if location is None:
                raise ValueError(f"Location not found: {location_name}")
                
            print(" Done.")
            
            return {
                "latitude": location.latitude,
                "longitude": location.longitude,
                "address": location.address
            }
        except Exception as e:
            print(f" Error: {str(e)}")
            raise ValueError(f"Error finding location: {str(e)}")
    
    def format_location_info(self, location_data: Dict[str, Any]) -> str:
        """
        Format location data for display in terminal.
        
        Args:
            location_data: Dictionary with location information
            
        Returns:
            Formatted string for terminal display
        """
        lat_dir = "N" if location_data["latitude"] >= 0 else "S"
        lon_dir = "E" if location_data["longitude"] >= 0 else "W"
        
        lat_formatted = f"{abs(location_data['latitude']):.4f}° {lat_dir}"
        lon_formatted = f"{abs(location_data['longitude']):.4f}° {lon_dir}"
        
        return (
            f"Location: {location_data['address']}\n"
            f"Coordinates: {lat_formatted}, {lon_formatted}"
        )
    
    def get_user_location_input(self) -> Dict[str, Any]:
        """
        Prompt user for location input and return coordinates.
        
        Returns:
            Dictionary with latitude, longitude, and formatted address
        """
        while True:
            try:
                location_name = input("\nEnter location (or press Enter for Los Angeles): ")
                
                if not location_name.strip():
                    location_name = "Los Angeles, CA"
                    
                coordinates = self.get_coordinates(location_name)
                return coordinates
            except ValueError as e:
                print(f"Error: {str(e)}")
                retry = input("Try again? (y/n): ")
                if retry.lower() != 'y':
                    print("Using default location (Los Angeles, CA)")
                    return self.get_coordinates("Los Angeles, CA")