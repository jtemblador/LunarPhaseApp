# Debug version of main.py with extra logging

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
import os
from datetime import datetime
from typing import Dict, Any

# Import backend modules
from backend.location_service import LocationService
from backend.lunar_data import LunarDataService
from utils.lunar_math import LunarMath, julian_day, get_next_phase_info
import config

app = FastAPI(title="Lunar Phase Calculator", version="1.0.0")

# Debug: Print current working directory and file existence
print(f"📁 Current directory: {os.getcwd()}")
print(f"📁 Utils folder exists: {os.path.exists('utils')}")
print(f"📁 Index.html exists: {os.path.exists('utils/index.html')}")
print(f"📁 Resources folder exists: {os.path.exists('resources')}")
print(f"📁 Moon.png exists: {os.path.exists('resources/moon.png')}")

# Mount static files with debugging
try:
    app.mount("/static", StaticFiles(directory="resources"), name="static")
    print("✅ Mounted /static -> resources/")
except Exception as e:
    print(f"❌ Failed to mount /static: {e}")

try:
    app.mount("/utils", StaticFiles(directory="utils"), name="utils")
    print("✅ Mounted /utils -> utils/")
except Exception as e:
    print(f"❌ Failed to mount /utils: {e}")

# Initialize services
location_service = LocationService()
lunar_service = LunarDataService(
    app_id=config.ASTRONOMY_APP_ID,
    app_secret=config.ASTRONOMY_APP_SECRET,
    base_url=config.ASTRONOMY_API_BASE_URL
)

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML page."""
    print("🏠 Root endpoint accessed")
    try:
        with open("utils/index.html", "r", encoding="utf-8") as f:
            content = f.read()
            print("✅ Successfully read index.html")
            return HTMLResponse(content=content)
    except FileNotFoundError:
        print("❌ index.html not found")
        return HTMLResponse(content="""
        <html><body>
        <h1>🌙 Lunar Phase Calculator</h1>
        <p style="color: red;">Error: index.html not found in utils/ folder</p>
        <p>Current directory: """ + os.getcwd() + """</p>
        </body></html>
        """)
    except Exception as e:
        print(f"❌ Error reading index.html: {e}")
        return HTMLResponse(content=f"<html><body><h1>Error: {str(e)}</h1></body></html>")

@app.get("/test")
async def test_endpoint():
    """Simple test endpoint."""
    print("🧪 Test endpoint accessed")
    return {"message": "Server is working!", "status": "success", "cwd": os.getcwd()}

@app.get("/lunar-data")
async def get_lunar_data(location: str = "Los Angeles, CA"):
    """API endpoint to get comprehensive lunar data."""
    print(f"🌙 Lunar data requested for: {location}")
    try:
        # Get coordinates for the location
        print("📍 Getting coordinates...")
        location_data = location_service.get_coordinates(location)
        print(f"✅ Coordinates: {location_data['latitude']}, {location_data['longitude']}")
        
        # Get lunar data from astronomy API
        print("🔭 Fetching lunar data from API...")
        lunar_data = lunar_service.get_moon_data(
            latitude=location_data["latitude"],
            longitude=location_data["longitude"]
        )
        print("✅ Lunar data received from API")
        
        # Calculate additional data
        current_time = datetime.now()
        jd = julian_day(current_time)
        
        # Calculate libration
        print("🌀 Calculating libration...")
        libration = LunarMath.calculate_libration(
            jd, 
            location_data["longitude"], 
            location_data["latitude"]
        )
        
        # Calculate orientation effects
        print("🔄 Calculating orientation...")
        orientation_angle = LunarMath.calculate_orientation(
            location_data["latitude"],
            lunar_data["position"]["azimuth"],
            lunar_data["position"]["altitude"]
        )
        
        # Get next phase information
        print("🔮 Calculating next phase...")
        next_phase = get_next_phase_info(lunar_data["phase"]["angle"])
        
        # Compile comprehensive response
        response_data = {
            **lunar_data,  # Include all original lunar data
            "libration": libration,
            "orientation": {
                "position_angle": orientation_angle,
            },
            "next_phase": next_phase,
            "observer": {
                **lunar_data["observer"],
                "location": location_data["address"]
            },
            "timestamp": current_time.isoformat(),
            "julian_day": jd
        }
        
        print("✅ Lunar data response prepared")
        return JSONResponse(content=response_data)
        
    except Exception as e:
        print(f"❌ Error in lunar data endpoint: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    print("🌙 Starting Lunar Phase Calculator...")
    print("📍 Default location: Los Angeles, CA")
    print("🌐 Opening web interface at http://127.0.0.1:8000")
    print("🧪 Test endpoint: http://127.0.0.1:8000/test")
    
    uvicorn.run(
        "main:app",
        host="127.0.0.1", 
        port=8000,
        reload=True,
        log_level="info"
    )