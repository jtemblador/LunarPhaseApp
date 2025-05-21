# backend/data_processor.py

import math
from typing import Dict, Any, List, Tuple

class LunarDataProcessor:
    """
    Process and format lunar data for display in the terminal.
    """
    
    def __init__(self, terminal_width: int = 80, enable_color: bool = True):
        """
        Initialize the data processor.
        
        Args:
            terminal_width: Width of the terminal in characters
            enable_color: Whether to use ANSI color codes in output
        """
        self.terminal_width = terminal_width
        self.enable_color = enable_color
        
        # ANSI color codes
        self.colors = {
            "reset": "\033[0m",
            "bold": "\033[1m",
            "cyan": "\033[36m",
            "yellow": "\033[33m",
            "green": "\033[32m",
            "blue": "\033[34m",
            "magenta": "\033[35m",
            "red": "\033[31m"
        }
        
        if not enable_color:
            for key in self.colors:
                self.colors[key] = ""
    
    def format_lunar_data(self, lunar_data: Dict[str, Any]) -> str:
        """
        Format lunar data for terminal display.
        
        Args:
            lunar_data: Dictionary with lunar data
            
        Returns:
            Formatted string for terminal display
        """
        c = self.colors  # Shorthand for colors
        
        # Format header
        header = f"{c['bold']}{c['cyan']}LUNAR OBSERVER - MOON DATA{c['reset']}"
        separator = "=" * self.terminal_width
        
        # Format date and latitide/longitude
        date_str = lunar_data["observer"]["date"]
        latitude = lunar_data["observer"]["latitude"]
        longitude = lunar_data["observer"]["longitude"]
        
        lat_dir = "N" if latitude >= 0 else "S"
        lon_dir = "E" if longitude >= 0 else "W"
        
        location = f"Location: {abs(latitude):.4f}° {lat_dir}, {abs(longitude):.4f}° {lon_dir}"
        
        # Format phase information
        phase_emoji = lunar_data["phase"]["emoji"]
        phase_name = lunar_data["phase"]["name"]
        illumination = lunar_data["phase"]["illumination"]
        age = lunar_data["phase"]["age"]
        
        phase_info = (
            f"{c['bold']}Moon Phase:{c['reset']} {phase_emoji} {phase_name}\n"
            f"Illumination: {illumination:.1f}%\n"
            f"Lunar Age: {age:.1f} days"
        )
        
        # Format position information
        altitude = lunar_data["position"]["altitude"]
        azimuth = lunar_data["position"]["azimuth"]
        
        visibility = "Above horizon" if altitude > 0 else "Below horizon"
        visibility_color = c["green"] if altitude > 0 else c["red"]
        
        position_info = (
            f"{c['bold']}Position:{c['reset']}\n"
            f"Altitude: {altitude:.2f}° ({visibility_color}{visibility}{c['reset']})\n"
            f"Azimuth: {azimuth:.2f}° ({self._get_direction(azimuth)})"
        )
        
        # Format distance information
        distance_km = lunar_data["distance"]["km"]
        distance_ls = lunar_data["distance"]["light_seconds"]
        
        distance_info = (
            f"{c['bold']}Distance:{c['reset']}\n"
            f"{distance_km:,.0f} km\n"
            f"{distance_ls:.2f} light seconds"
        )
        
        # Format angular size
        angular_size = lunar_data["angular_diameter"]
        
        size_info = (
            f"{c['bold']}Angular Diameter:{c['reset']}\n"
            f"{angular_size:.4f}°"
        )
        
        # Create ASCII visualization
        ascii_vis = self._create_ascii_moon_visualization(
            illumination, 
            lunar_data["phase"]["angle"],
            self.terminal_width // 2,
            10
        )
        
        # Combine all sections
        sections = [
            header,
            separator,
            f"Date: {date_str}",
            location,
            "",
            phase_info,
            "",
            position_info,
            "",
            distance_info,
            "",
            size_info,
            "",
            f"{c['bold']}Moon Visualization:{c['reset']}",
            ascii_vis
        ]
        
        return "\n".join(sections)
    
    def _get_direction(self, azimuth: float) -> str:
        """
        Convert azimuth angle to cardinal direction.
        
        Args:
            azimuth: Azimuth angle in degrees
            
        Returns:
            Cardinal direction string
        """
        directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", 
                      "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
        
        index = round(azimuth / 22.5) % 16
        return directions[index]
    
    def _create_ascii_moon_visualization(self, illumination: float, phase_angle: float, 
                                       width: int, height: int) -> str:
        """
        Create ASCII art visualization of the current moon phase.
        
        Args:
            illumination: Percentage of moon illuminated
            phase_angle: Phase angle in degrees
            width: Width of the visualization in characters
            height: Height of the visualization in characters
            
        Returns:
            ASCII art string
        """
        # Determine if waxing or waning
        is_waxing = 0 <= phase_angle <= 180
        
        # Calculate normalized illumination (0-1)
        norm_illumination = illumination / 100.0
        
        # Characters for different densities
        if self.enable_color:
            filled = "█"
            partial = ["▏", "▎", "▍", "▌", "▋", "▊", "▉"]
            empty = " "
        else:
            filled = "#"
            partial = [".", ":", "-", "=", "+", "*"]
            empty = " "
        
        # Create the visualization
        lines = []
        
        for y in range(height):
            line = []
            for x in range(width):
                # Calculate position relative to center
                nx = (x / width) * 2 - 1  # -1 to 1
                ny = (y / height) * 2 - 1  # -1 to 1
                
                # Distance from center (0 to 1)
                dist = math.sqrt(nx*nx + ny*ny)
                
                if dist > 1:
                    # Outside the moon
                    line.append(" ")
                else:
                    # Inside the moon
                    # Calculate angle from center
                    angle = math.atan2(ny, nx)
                    angle_deg = math.degrees(angle) % 360
                    
                    # Determine if this part should be illuminated
                    if is_waxing:
                        is_lit = angle_deg >= 90 and angle_deg <= 270
                    else:
                        is_lit = angle_deg <= 90 or angle_deg >= 270
                    
                    # Apply illumination percentage
                    if is_lit:
                        if norm_illumination >= 0.99:
                            line.append(filled)
                        elif norm_illumination <= 0.01:
                            line.append(empty)
                        else:
                            # Partial illumination
                            idx = min(len(partial) - 1, 
                                     int(norm_illumination * len(partial)))
                            line.append(partial[idx])
                    else:
                        line.append(empty)
            
            lines.append("".join(line))
        
        return "\n".join(lines)