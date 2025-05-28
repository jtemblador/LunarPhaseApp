#!/usr/bin/env python3
# test_moon_phases.py

import requests
import base64
import json
from datetime import datetime, timedelta
import config

class MoonPhaseAPITester:
    def __init__(self):
        # Set up authentication
        auth_string = f"{config.ASTRONOMY_APP_ID}:{config.ASTRONOMY_APP_SECRET}"
        self.encoded_auth = base64.b64encode(auth_string.encode()).decode()
        
        self.headers = {
            "Authorization": f"Basic {self.encoded_auth}",
            "Content-Type": "application/json"
        }
        
        self.base_url = config.ASTRONOMY_API_BASE_URL
        
    def test_endpoint(self, endpoint_name, url, params=None, data=None, method="GET"):
        """Test a specific API endpoint and return results."""
        print(f"\n{'='*60}")
        print(f"Testing: {endpoint_name}")
        print(f"URL: {url}")
        print(f"Method: {method}")
        if params:
            print(f"Params: {params}")
        if data:
            print(f"Data: {json.dumps(data, indent=2)}")
        print("="*60)
        
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers, params=params)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ SUCCESS")
                result = response.json()
                
                # Pretty print the response
                print("\nResponse Structure:")
                self.print_json_structure(result)
                
                # Look for phase data specifically
                phase_data = self.extract_phase_data(result)
                if phase_data:
                    print("\n🌙 PHASE DATA FOUND:")
                    print(json.dumps(phase_data, indent=2))
                
                return result
            else:
                print("❌ FAILED")
                print(f"Error: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ EXCEPTION: {str(e)}")
            return None
    
    def print_json_structure(self, data, indent=0):
        """Print the structure of JSON data without full content."""
        spaces = "  " * indent
        
        if isinstance(data, dict):
            print(f"{spaces}{{")
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    print(f"{spaces}  '{key}': ", end="")
                    if isinstance(value, dict):
                        print(f"dict with {len(value)} keys")
                        if indent < 2:  # Limit depth
                            self.print_json_structure(value, indent + 2)
                    elif isinstance(value, list):
                        print(f"list with {len(value)} items")
                        if len(value) > 0 and indent < 2:
                            print(f"{spaces}    [0]: ", end="")
                            self.print_json_structure(value[0], indent + 2)
                else:
                    print(f"{spaces}  '{key}': {value}")
            print(f"{spaces}}}")
        elif isinstance(data, list):
            print(f"{spaces}[{len(data)} items]")
            if len(data) > 0 and indent < 2:
                self.print_json_structure(data[0], indent + 1)
        else:
            print(f"{spaces}{data}")
    
    def extract_phase_data(self, data):
        """Try to find phase data in the response."""
        phase_data = {}
        
        # Common paths where phase data might be
        phase_paths = [
            ["phase"],
            ["data", "phase"],
            ["data", "table", "rows", 0, "cells", 0, "extraInfo", "phase"],
            ["extraInfo", "phase"],
            ["moon", "phase"],
            ["body", "phase"]
        ]
        
        for path in phase_paths:
            try:
                current = data
                for key in path:
                    if isinstance(current, dict) and key in current:
                        current = current[key]
                    elif isinstance(current, list) and isinstance(key, int) and 0 <= key < len(current):
                        current = current[key]
                    else:
                        break
                else:
                    # Successfully navigated the full path
                    if isinstance(current, dict):
                        phase_data[f"Path: {' -> '.join(map(str, path))}"] = current
            except:
                continue
        
        return phase_data if phase_data else None
    
    def run_all_tests(self):
        """Run tests on all possible moon phase endpoints."""
        current_date = datetime.now().strftime("%Y-%m-%d")
        test_lat = 34.0522  # Los Angeles
        test_lon = -118.2437
        
        print("🌙 MOON PHASE API ENDPOINT TESTER")
        print(f"Testing date: {current_date}")
        print(f"Test location: {test_lat}, {test_lon}")
        
        # Test 1: Direct moon phase endpoint (known to fail)
        self.test_endpoint(
            "Moon Phase (Direct)",
            f"{self.base_url}moon/phase",
            params={"date": current_date}
        )
        
        # Test 2: Moon phase with different parameter format
        self.test_endpoint(
            "Moon Phase (Different params)",
            f"{self.base_url}moon/phase",
            params={"format": "json", "date": current_date}
        )
        
        # Test 3: Bodies endpoint (known to work)
        self.test_endpoint(
            "Bodies List",
            f"{self.base_url}bodies"
        )
        
        # Test 4: Moon positions (known to work and contains phase data)
        self.test_endpoint(
            "Moon Positions",
            f"{self.base_url}bodies/positions/moon",
            params={
                "latitude": test_lat,
                "longitude": test_lon,
                "elevation": 0,
                "from_date": current_date,
                "to_date": current_date,
                "time": "12:00:00"
            }
        )
        
        # Test 5: Try different moon phase endpoint variations
        phase_endpoints = [
            "moon/phase",
            "moon/phases", 
            "bodies/moon/phase",
            "phase/moon"
        ]
        
        for endpoint in phase_endpoints:
            self.test_endpoint(
                f"Phase Endpoint: {endpoint}",
                f"{self.base_url}{endpoint}",
                params={"date": current_date}
            )
        
        # Test 6: Try POST method for moon phase
        self.test_endpoint(
            "Moon Phase (POST)",
            f"{self.base_url}moon/phase",
            data={"date": current_date, "format": "json"},
            method="POST"
        )
        
        # Test 7: Try different date formats
        date_formats = [
            datetime.now().strftime("%Y-%m-%d"),
            datetime.now().strftime("%Y/%m/%d"),
            datetime.now().strftime("%d-%m-%Y"),
            datetime.now().isoformat()
        ]
        
        for date_format in date_formats:
            self.test_endpoint(
                f"Moon Phase (Date format: {date_format})",
                f"{self.base_url}moon/phase",
                params={"date": date_format}
            )
        
        # Test 8: Try multiple dates
        dates = []
        for i in range(3):
            date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
            dates.append(date)
        
        for i, date in enumerate(dates):
            self.test_endpoint(
                f"Moon Phase (Day +{i}: {date})",
                f"{self.base_url}moon/phase",
                params={"date": date}
            )
        
        print(f"\n{'='*60}")
        print("🔍 SUMMARY")
        print("="*60)
        print("Based on the tests above:")
        print("- Check which endpoints returned 200 (success)")
        print("- Look for phase data in successful responses")
        print("- Note any working alternative endpoints")
        print("- Compare phase data between different endpoints")

def main():
    """Run the moon phase API tests."""
    tester = MoonPhaseAPITester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()