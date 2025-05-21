# backend/lunar_data.py

import requests
import json
import base64
from datetime import datetime, timedelta
import os
import time
import sys
from typing import Dict, Any, Optional

class LunarDataService:
    """Service for retrieving lunar data from astronomy APIs."""
    
    def __init__(self, app_id: str, app_secret: str, base_url: str):
        """
        Initialize the lunar data service.
        
        Args:
            app_id: Application ID for the astronomy service
            app_secret: Application Secret for the astronomy service
            base_url: Base URL for the astronomy API
        """
        # Clean the credentials to remove any potential whitespace
        self.app_id = app_id.strip()
        self.app_secret = app_secret.strip()
        self.base_url = base_url.strip()
        
        # Create the auth string exactly as in the test script
        auth_string = f"{self.app_id}:{self.app_secret}"
        self.encoded_auth = base64.b64encode(auth_string.encode()).decode()
        
        # Set headers - keeping it minimal like the test script
        self.headers = {
            "Authorization": f"Basic {self.encoded_auth}",
            "Content-Type": "application/json"
        }
        
        # Initialize cache
        self.cache = {}
        self.cache_duration = 3600  # 1 hour in seconds
        
    def get_moon_data(self, latitude: float, longitude: float, date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get comprehensive moon data for a specific location and time.
        
        Args:
            latitude: Observer latitude
            longitude: Observer longitude
            date: Observation time (defaults to current time)
            
        Returns:
            Dictionary with moon data including phase, position, etc.
        """
        if date is None:
            date = datetime.now()
            
        # Create a cache key based on location and date
        cache_key = f"{latitude}_{longitude}_{date.strftime('%Y-%m-%d_%H')}"
        
        # Check if we have cached data
        if cache_key in self.cache:
            cache_time, cached_data = self.cache[cache_key]
            if time.time() - cache_time < self.cache_duration:
                return cached_data
        
        # Format the date for API request
        formatted_date = date.strftime("%Y-%m-%d")
        
        print("Fetching lunar data...", end="", flush=True)
        
        try:
            # Build the URL for the API request
            url = (f"{self.base_url}bodies/positions/moon"
                f"?latitude={latitude}&longitude={longitude}"
                f"&elevation=0&from_date={formatted_date}&to_date={formatted_date}"
                f"&time=12:00:00")
            
            # Make the request
            response = requests.get(url, headers=self.headers)
            
            if response.status_code != 200:
                print(f" Failed: {response.status_code}")
                raise Exception(f"API request failed: {response.status_code}")
                
            # Parse the response
            data = response.json()
            print(" Done.")
            
            # Direct path to the moon data
            moon_data = data["data"]["table"]["rows"][0]["cells"][0]
            
            # Extract phase information
            phase_info = moon_data["extraInfo"]["phase"]
            phase_name = phase_info["string"]
            phase_angle = float(phase_info["angel"])
            illumination = float(phase_info["fraction"]) * 100
            
            # Calculate lunar age (days)
            lunar_cycle = 29.53
            age = (phase_angle / 360) * lunar_cycle
            
            # Extract distance information
            distance = moon_data["distance"]["fromEarth"]
            distance_km = float(distance["km"])
            distance_au = float(distance["au"])
            
            # Extract position information
            position = moon_data["position"]
            altitude = float(position["horizontal"]["altitude"]["degrees"])
            azimuth = float(position["horizontal"]["azimuth"]["degrees"])
            right_ascension = float(position["equatorial"]["rightAscension"]["hours"])
            declination = float(position["equatorial"]["declination"]["degrees"])
            
            # Calculate angular diameter
            avg_distance = 384400  # km
            avg_angular_diameter = 0.5  # degrees
            angular_diameter = avg_angular_diameter * (avg_distance / distance_km)
            
            # Create and return the result
            result = {
                "phase": {
                    "name": phase_name,
                    "emoji": self._get_phase_emoji(phase_name),
                    "illumination": illumination,
                    "age": age,
                    "angle": phase_angle
                },
                "distance": {
                    "km": distance_km,
                    "au": distance_au,
                    "light_seconds": distance_km / 299792.458
                },
                "position": {
                    "altitude": altitude,
                    "azimuth": azimuth,
                    "right_ascension": right_ascension,
                    "declination": declination
                },
                "angular_diameter": angular_diameter,
                "observer": {
                    "latitude": latitude,
                    "longitude": longitude,
                    "date": formatted_date
                }
            }
            
            # Cache the result
            self.cache[cache_key] = (time.time(), result)
            
            return result
            
        except Exception as e:
            print(f" Error: {str(e)}")
            
            # For better debugging, show the specific error location
            import traceback
            traceback.print_exc()
            
            raise Exception(f"Failed to retrieve lunar data: {str(e)}")
    
    def _get_phase_emoji(self, phase_name: str) -> str:
        """
        Get emoji representation of moon phase.
        
        Args:
            phase_name: Name of the moon phase
            
        Returns:
            Emoji character representing the phase
        """
        phase_emojis = {
            "New Moon": "🌑",
            "Waxing Crescent": "🌒",
            "First Quarter": "🌓",
            "Waxing Gibbous": "🌔",
            "Full Moon": "🌕",
            "Waning Gibbous": "🌖",
            "Last Quarter": "🌗",
            "Waning Crescent": "🌘"
        }
        
        return phase_emojis.get(phase_name, "🌙")