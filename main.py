# main.py - FastAPI Web Server Entry Point

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

# Mount static files
app.mount("/static", StaticFiles(directory="resources"), name="static")
app.mount("/utils", StaticFiles(directory="utils"), name="utils")

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
    with open("utils/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/lunar-data")
async def get_lunar_data(location: str = "Los Angeles, CA"):
    """API endpoint to get comprehensive lunar data."""
    try:
        # Get coordinates for the location
        location_data = location_service.get_coordinates(location)
        
        # Get lunar data from astronomy API
        lunar_data = lunar_service.get_moon_data(
            latitude=location_data["latitude"],
            longitude=location_data["longitude"]
        )
        
        # Calculate additional data
        current_time = datetime.now()
        jd = julian_day(current_time)
        
        # Calculate libration
        libration = LunarMath.calculate_libration(
            jd, 
            location_data["longitude"], 
            location_data["latitude"]
        )
        
        # Calculate orientation effects
        orientation_angle = LunarMath.calculate_orientation(
            location_data["latitude"],
            lunar_data["position"]["azimuth"],
            lunar_data["position"]["altitude"]
        )
        
        # Get next phase information
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
        
        return JSONResponse(content=response_data)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    print("🌙 Starting Lunar Phase Calculator...")
    print("📍 Default location: Los Angeles, CA")
    print("🌐 Opening web interface at http://127.0.0.1:8000")
    
    uvicorn.run(
        "main:app",  # Pass as import string for reload to work
        host="127.0.0.1", 
        port=8000,
        reload=True,
        log_level="info"
    )