# utils/lunar_math.py - Astronomical calculations for libration and orientation

import math
from datetime import datetime
from typing import Dict, Any

class LunarMath:
    """Calculate lunar libration and orientation effects."""
    
    @staticmethod
    def calculate_libration(julian_day: float, longitude: float, latitude: float) -> Dict[str, float]:
        """
        Calculate lunar libration values.
        
        Libration is the oscillating movement of the Moon that allows us to see 
        slightly more than 50% of its surface over time. There are three types:
        - Longitudinal libration: East-west wobbling due to elliptical orbit
        - Latitudinal libration: North-south wobbling due to axial tilt  
        - Diurnal libration: Daily parallax shift due to Earth's rotation
        
        Args:
            julian_day: Julian day number
            longitude: Observer longitude in degrees
            latitude: Observer latitude in degrees
            
        Returns:
            Dictionary with libration values in degrees
        """
        # Time since J2000.0 in centuries
        T = (julian_day - 2451545.0) / 36525.0
        
        # Mean longitude of the Moon (degrees)
        L_moon = 218.316 + 481267.881 * T
        
        # Mean anomaly of the Moon (degrees)
        M_moon = 134.963 + 477198.868 * T
        
        # Mean anomaly of the Sun (degrees)
        M_sun = 357.529 + 35999.050 * T
        
        # Moon's argument of latitude (degrees)
        F = 93.272 + 483202.019 * T
        
        # Longitude of ascending node (degrees)
        Omega = 125.045 - 1934.136 * T
        
        # Convert to radians for trigonometric functions
        L_moon_rad = math.radians(L_moon % 360)
        M_moon_rad = math.radians(M_moon % 360)
        M_sun_rad = math.radians(M_sun % 360)
        F_rad = math.radians(F % 360)
        Omega_rad = math.radians(Omega % 360)
        
        # Calculate libration in longitude (degrees)
        # This is the east-west wobbling of the Moon
        lib_lon = -1.274 * math.sin(M_moon_rad - 2 * F_rad) + \
                  0.658 * math.sin(-2 * F_rad) - \
                  0.186 * math.sin(M_sun_rad) - \
                  0.059 * math.sin(2 * M_moon_rad - 2 * F_rad) - \
                  0.057 * math.sin(M_moon_rad - 2 * F_rad + M_sun_rad)
        
        # Calculate libration in latitude (degrees)
        # This is the north-south wobbling of the Moon
        lib_lat = -0.173 * math.sin(F_rad - 2 * F_rad) - \
                  0.055 * math.sin(M_moon_rad - F_rad - 2 * F_rad) - \
                  0.046 * math.sin(M_moon_rad + F_rad - 2 * F_rad) + \
                  0.033 * math.sin(F_rad + 2 * F_rad)
        
        # Observer effect (diurnal libration approximation)
        # This accounts for the daily parallax shift due to Earth's rotation
        diurnal_lon = longitude * 0.0003  # Very small effect
        diurnal_lat = latitude * 0.0002
        
        # Total libration values
        total_lon = lib_lon + diurnal_lon
        total_lat = lib_lat + diurnal_lat
        
        return {
            "longitude": total_lon,
            "latitude": total_lat,
            "total": math.sqrt(total_lon**2 + total_lat**2),
            "longitudinal_only": lib_lon,
            "latitudinal_only": lib_lat,
            "diurnal_longitude": diurnal_lon,
            "diurnal_latitude": diurnal_lat
        }
    
    @staticmethod
    def calculate_orientation(latitude: float, azimuth: float, altitude: float) -> float:
        """
        Calculate moon's apparent rotation due to observer position.
        
        The Moon appears rotated differently depending on where you observe it from
        on Earth. This is due to the spherical geometry of celestial observations.
        
        Args:
            latitude: Observer latitude in degrees
            azimuth: Moon's azimuth in degrees
            altitude: Moon's altitude in degrees
            
        Returns:
            Position angle in degrees (rotation of the Moon's bright limb)
        """
        # Convert to radians for calculations
        lat_rad = math.radians(latitude)
        az_rad = math.radians(azimuth)
        alt_rad = math.radians(altitude)
        
        # Calculate position angle of the moon's bright limb
        # This affects how the illuminated portion appears rotated
        try:
            position_angle = math.atan2(
                math.cos(lat_rad) * math.sin(az_rad),
                math.sin(lat_rad) * math.cos(alt_rad) - 
                math.cos(lat_rad) * math.sin(alt_rad) * math.cos(az_rad)
            )
            
            return math.degrees(position_angle) % 360
        except (ValueError, ZeroDivisionError):
            # Return 0 if calculation fails (e.g., moon at zenith)
            return 0.0

def julian_day(date: datetime) -> float:
    """
    Convert datetime to Julian day number.
    
    The Julian day number is the continuous count of days since the beginning
    of the Julian period on January 1, 4713 BCE. It's used in astronomical
    calculations to avoid calendar complications.
    
    Args:
        date: Python datetime object
        
    Returns:
        Julian day number as float
    """
    # Julian day calculation algorithm
    a = (14 - date.month) // 12
    y = date.year + 4800 - a
    m = date.month + 12 * a - 3
    
    # Calculate Julian day number for the date
    jdn = date.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
    
    # Add time fraction (hours, minutes, seconds as fraction of day)
    time_fraction = (date.hour - 12) / 24.0 + date.minute / 1440.0 + date.second / 86400.0
    
    return jdn + time_fraction

def get_next_phase_info(current_phase_angle: float) -> Dict[str, Any]:
    """
    Calculate when the next major lunar phase occurs.
    
    Args:
        current_phase_angle: Current phase angle in degrees
        
    Returns:
        Dictionary with next phase name and days until it occurs
    """
    # Major lunar phases and their angles
    phase_angles = {
        "New Moon": 0,
        "First Quarter": 90,
        "Full Moon": 180,
        "Last Quarter": 270
    }
    
    # Find next phase after current angle
    next_phases = []
    for phase_name, angle in phase_angles.items():
        if angle > (current_phase_angle % 360):
            # Calculate days until this phase
            angle_diff = angle - (current_phase_angle % 360)
            days_until = angle_diff * 29.53 / 360  # 29.53 days per lunar cycle
            next_phases.append({"name": phase_name, "days": days_until})
    
    # If no phases found in current cycle, get next new moon
    if not next_phases:
        angle_diff = 360 - (current_phase_angle % 360)
        days_until = angle_diff * 29.53 / 360
        next_phases.append({"name": "New Moon", "days": days_until})
    
    # Return the soonest next phase
    return min(next_phases, key=lambda x: x["days"])

def get_direction_from_azimuth(azimuth: float) -> str:
    """
    Convert azimuth angle to cardinal direction.
    
    Args:
        azimuth: Azimuth angle in degrees (0-360)
        
    Returns:
        Cardinal direction string (N, NNE, NE, etc.)
    """
    directions = [
        "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", 
        "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"
    ]
    
    # Calculate index (16 directions, so 360/16 = 22.5 degrees each)
    index = round(azimuth / 22.5) % 16
    return directions[index]