# Lunar Observer

A terminal-based application that provides real-time lunar data visualization based on your location.

## Overview

Lunar Observer fetches accurate information about the Moon's current phase, position, and other characteristics as seen from your specific geographical location. It's designed for astronomers, stargazers, or anyone interested in lunar observation.

## Features

- **Location-based lunar data**: View the moon as it appears from your current location
- **Detailed moon information**: Phase, illumination percentage, distance, position and more
- **ASCII visualization**: Terminal-friendly representation of the current lunar phase
- **Multiple location support**: Compare moon data from different locations around the world
- **Colorful terminal output**: Easy-to-read, well-formatted data presentation

## Installation

### Prerequisites

- Python 3.6+
- Internet connection
- Astronomy API credentials

### Setup

1. Clone the repository:
```
git clone https://github.com/yourusername/lunar-observer.git
cd lunar-observer
```

2. Install required dependencies:
```
pip install requests geopy
```

3. Configure your Astronomy API credentials:
   - Register at [astronomyapi.com](https://astronomyapi.com/) to get API credentials
   - Update the `config.py` file with your App ID and App Secret

## Usage

### Basic Usage

Run the application:
```
python main.py
```

Enter your location when prompted, or press Enter for the default location (Los Angeles).

### Command Line Options

```
python main.py [-h] [-l LOCATION] [-c] [-v]

optional arguments:
  -h, --help            show help message and exit
  -l LOCATION, --location LOCATION
                        Location (e.g., 'Los Angeles, CA')
  -c, --no-color        Disable color output
  -v, --version         Show version information
```

### Example Output

```
================================================================================
                       LUNAR OBSERVER - Terminal Edition                        
              A tool to visualize the moon based on your location               
================================================================================

Location: Tokyo, Japan
Coordinates: 35.6762° N, 139.6503° E

LUNAR OBSERVER - MOON DATA
================================================================================
Date: 2025-05-21
Location: 35.6762° N, 139.6503° E

Moon Phase: 🌘 Waning Crescent
Illumination: 4.3%
Lunar Age: 23.2 days

Position:
Altitude: 45.63° (Above horizon)
Azimuth: 271.82° (W)

Distance:
369,779 km
1.23 light seconds

Angular Diameter:
0.5193°
```

## Project Structure

```
lunar_observer/
├── README.md                # This documentation file
├── main.py                  # Application entry point
├── config.py                # Configuration settings and API keys
├── backend/
│   ├── __init__.py          # Package initialization
│   ├── lunar_data.py        # API integration for lunar data
│   ├── location_service.py  # Geocoding and location processing
│   └── data_processor.py    # Formatting of data for display
└── tests/                   # Test scripts and utilities
    └── inspect_api.py       # Utility to explore API responses
```

## How It Works

1. **Geocoding**: Converts user-provided location names to geographic coordinates
2. **API Integration**: Retrieves lunar data from the Astronomy API based on location
3. **Data Processing**: Calculates additional information such as lunar age and angular diameter
4. **Data Visualization**: Formats the data for display in the terminal, including ASCII visualization
5. **Caching**: Stores recent results to reduce API calls for repeated locations

## API Structure

The application uses the Astronomy API to retrieve lunar data. Key data points:

- **Phase information**: Name, illumination percentage, age, and angle
- **Position**: Altitude, azimuth, right ascension, and declination
- **Distance**: Kilometers, astronomical units, and light seconds
- **Additional details**: Angular diameter and constellation

## Limitations

- Requires internet connection for API access
- API calls may be rate-limited based on your account tier
- ASCII visualization is approximate and not to scale

## Future Enhancements

- 3D visualization with optional GUI mode
- Historical and future lunar data
- Lunar eclipse predictions
- Rise and set times
- Integration with weather data for visibility forecast

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Astronomy API](https://astronomyapi.com/) for providing the lunar data
- [Geopy](https://geopy.readthedocs.io/) for geocoding capabilities