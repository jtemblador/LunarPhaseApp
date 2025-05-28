#!/usr/bin/env python3
# inspect_api.py

import requests
import base64
import json
from datetime import datetime

# Import your configuration
import config

# Your location
latitude = 34.0522  # Los Angeles
longitude = -118.2437

# Create auth string
app_id = config.ASTRONOMY_APP_ID.strip()
app_secret = config.ASTRONOMY_APP_SECRET.strip()
auth_string = f"{app_id}:{app_secret}"
encoded_auth = base64.b64encode(auth_string.encode()).decode()

# Set headers
headers = {
    "Authorization": f"Basic {encoded_auth}",
    "Content-Type": "application/json"
}

# Get current date
current_date = datetime.now().strftime("%Y-%m-%d")

# Test the positions endpoint
print("Testing positions endpoint...")
url = (f"{config.ASTRONOMY_API_BASE_URL}bodies/positions/moon"
       f"?latitude={latitude}&longitude={longitude}"
       f"&elevation=0&from_date={current_date}&to_date={current_date}"
       f"&time=12:00:00")

response = requests.get(url, headers=headers)

# Print results
print(f"Status code: {response.status_code}")
if response.status_code != 200:
    print(f"Error response: {response.text}")
else:
    print("Request successful!")
    
    # Save the response to a file
    with open("api_response.json", "w") as f:
        json.dump(response.json(), f, indent=2)
    
    print("Response saved to 'api_response.json'")
    
    # Print the top-level structure
    data = response.json()
    print("\nTop-level keys:", list(data.keys()))
    
    if "data" in data:
        print("Keys in data:", list(data["data"].keys()))
        
        if "table" in data["data"]:
            print("Keys in table:", list(data["data"]["table"].keys()))
            
            if "rows" in data["data"]["table"]:
                print(f"Number of rows: {len(data['data']['table']['rows'])}")
                
                if data["data"]["table"]["rows"]:
                    first_row = data["data"]["table"]["rows"][0]
                    print("Keys in first row:", list(first_row.keys()))