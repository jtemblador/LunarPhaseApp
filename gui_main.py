#!/usr/bin/env python3
# gui_main.py - Improved version with auto-sizing and better colors

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import os
import threading
from typing import Dict, Any, Optional

# Import backend modules
from backend.location_service import LocationService
from backend.lunar_data import LunarDataService
from backend.data_processor import LunarDataProcessor
import config

class LunarObserverGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Lunar Observer - GUI Edition")
        
        # Set minimum size and make it resizable
        self.root.minsize(900, 883)
        self.root.geometry("1000x700")  # Start with larger default size
        
        # Configure the root to have dark background
        self.root.configure(bg='#0f0f23')
        
        # Initialize services
        self.location_service = LocationService()
        self.lunar_service = LunarDataService(
            app_id=config.ASTRONOMY_APP_ID,
            app_secret=config.ASTRONOMY_APP_SECRET,
            base_url=config.ASTRONOMY_API_BASE_URL
        )
        self.data_processor = LunarDataProcessor(
            terminal_width=80,
            enable_color=False
        )
        
        # Variables
        self.current_lunar_data = None
        self.moon_image = None
        
        # Style configuration
        self.setup_styles()
        
        # Create GUI elements
        self.create_widgets()
        
        # Load default moon image
        self.load_default_moon_image()
        
        # Configure grid weights for proper resizing
        self.configure_grid_weights()
        
    def setup_styles(self):
        """Configure the visual styles for the GUI with better colors."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Define color palette
        colors = {
            'bg_dark': '#0f0f23',      # Very dark blue background
            'bg_medium': '#16213e',     # Medium dark blue
            'bg_light': '#1e2a4a',     # Lighter blue for frames
            'accent': '#4a9eff',       # Bright blue accent
            'text_light': '#e8e8f0',   # Light text
            'text_accent': '#64b5f6',  # Blue text
            'button_bg': '#2196f3',    # Button background
            'button_hover': '#1976d2', # Button hover
            'entry_bg': '#263238',     # Entry field background
        }
        
        # Configure ttk styles with better colors
        style.configure('Title.TLabel', 
                       background=colors['bg_dark'], 
                       foreground=colors['text_light'], 
                       font=('Segoe UI', 18, 'bold'))
        
        style.configure('Header.TLabel', 
                       background=colors['bg_dark'], 
                       foreground=colors['accent'], 
                       font=('Segoe UI', 12, 'bold'))
        
        style.configure('Data.TLabel', 
                       background=colors['bg_light'], 
                       foreground=colors['text_light'], 
                       font=('Segoe UI', 10))
        
        style.configure('Custom.TButton',
                       background=colors['button_bg'],
                       foreground='white',
                       font=('Segoe UI', 10, 'bold'),
                       padding=(10, 5))
        
        style.map('Custom.TButton',
                  background=[('active', colors['button_hover'])])
        
        style.configure('Custom.TEntry',
                       fieldbackground=colors['entry_bg'],
                       foreground=colors['text_light'],
                       borderwidth=1,
                       insertcolor=colors['text_light'],
                       font=('Segoe UI', 10))
        
        # Custom frame styles
        style.configure('Dark.TFrame',
                       background=colors['bg_dark'],
                       borderwidth=0)
        
        style.configure('Medium.TFrame',
                       background=colors['bg_medium'],
                       borderwidth=1,
                       relief='solid')
        
        style.configure('Light.TFrame',
                       background=colors['bg_light'],
                       borderwidth=1,
                       relief='solid')
        
        # LabelFrame styles
        style.configure('Custom.TLabelframe',
                       background=colors['bg_light'],
                       foreground=colors['text_accent'],
                       borderwidth=2,
                       relief='solid')
        
        style.configure('Custom.TLabelframe.Label',
                       background=colors['bg_light'],
                       foreground=colors['text_accent'],
                       font=('Segoe UI', 11, 'bold'))
    
    def configure_grid_weights(self):
        """Configure grid weights for proper resizing."""
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def create_widgets(self):
        """Create and arrange all GUI widgets with proper grid management."""
        # Main container with padding
        main_frame = ttk.Frame(self.root, style='Dark.TFrame', padding=15)
        main_frame.grid(row=0, column=0, sticky='nsew')
        
        # Configure main_frame grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)  # Content area should expand
        
        # Title
        title_label = ttk.Label(main_frame, 
                               text="🌙 Lunar Observer", 
                               style='Title.TLabel')
        title_label.grid(row=0, column=0, pady=(0, 20), sticky='ew')
        
        # Location input frame
        location_frame = ttk.Frame(main_frame, style='Medium.TFrame', padding=10)
        location_frame.grid(row=1, column=0, sticky='ew', pady=(0, 15))
        
        # Configure location frame
        location_frame.columnconfigure(1, weight=1)
        
        ttk.Label(location_frame, 
                 text="Location:", 
                 style='Header.TLabel').grid(row=0, column=0, padx=(0, 10), sticky='w')
        
        self.location_entry = ttk.Entry(location_frame, 
                                       style='Custom.TEntry',
                                       width=40)
        self.location_entry.grid(row=0, column=1, padx=(0, 10), sticky='ew')
        self.location_entry.insert(0, "Los Angeles, CA")
        
        self.fetch_button = ttk.Button(location_frame,
                                      text="Get Moon Data",
                                      style='Custom.TButton',
                                      command=self.fetch_moon_data_threaded)
        self.fetch_button.grid(row=0, column=2, sticky='e')
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, 
                                       mode='indeterminate',
                                       style='TProgressbar')
        self.progress.grid(row=2, column=0, sticky='ew', pady=(0, 15))
        
        # Content frame (split into left and right)
        content_frame = ttk.Frame(main_frame, style='Dark.TFrame')
        content_frame.grid(row=3, column=0, sticky='nsew')
        
        # Configure content frame grid
        content_frame.columnconfigure(0, weight=1)  # Left side (image)
        content_frame.columnconfigure(1, weight=1)  # Right side (data)
        content_frame.rowconfigure(0, weight=1)
        
        # Left side - Moon image container
        self.image_container = ttk.Frame(content_frame, style='Light.TFrame', padding=15)
        self.image_container.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
        self.image_container.columnconfigure(0, weight=1)
        self.image_container.rowconfigure(0, weight=1)
        
        # Moon image label
        self.moon_image_label = ttk.Label(self.image_container, style='Data.TLabel')
        self.moon_image_label.grid(row=0, column=0, sticky='nsew')
        
        # Right side - Moon data container
        self.data_container = ttk.Frame(content_frame, style='Dark.TFrame')
        self.data_container.grid(row=0, column=1, sticky='nsew')
        self.data_container.columnconfigure(0, weight=1)
        
        # Create data display widgets
        self.create_data_widgets()
        
        # Status bar
        status_frame = ttk.Frame(main_frame, style='Medium.TFrame', padding=5)
        status_frame.grid(row=4, column=0, sticky='ew', pady=(15, 0))
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(status_frame, 
                              textvariable=self.status_var,
                              style='Data.TLabel')
        status_bar.grid(row=0, column=0, sticky='w')
    
    def create_data_widgets(self):
        """Create widgets for displaying lunar data with improved layout."""
        # Phase information
        phase_frame = ttk.LabelFrame(self.data_container, 
                                   text="Moon Phase", 
                                   style='Custom.TLabelframe',
                                   padding=15)
        phase_frame.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        phase_frame.columnconfigure(0, weight=1)
        
        self.phase_name_var = tk.StringVar()
        self.phase_emoji_var = tk.StringVar()
        self.illumination_var = tk.StringVar()
        self.age_var = tk.StringVar()
        
        # Emoji with larger font
        emoji_label = ttk.Label(phase_frame, textvariable=self.phase_emoji_var, 
                               font=('Segoe UI', 32), background='#1e2a4a',
                               foreground='#e8e8f0')
        emoji_label.grid(row=0, column=0, pady=(0, 10))
        
        ttk.Label(phase_frame, textvariable=self.phase_name_var,
                 style='Data.TLabel', font=('Segoe UI', 12, 'bold')).grid(row=1, column=0, sticky='ew')
        ttk.Label(phase_frame, textvariable=self.illumination_var,
                 style='Data.TLabel').grid(row=2, column=0, sticky='ew', pady=(5, 0))
        ttk.Label(phase_frame, textvariable=self.age_var,
                 style='Data.TLabel').grid(row=3, column=0, sticky='ew', pady=(5, 0))
        
        # Position information
        position_frame = ttk.LabelFrame(self.data_container, 
                                      text="Position", 
                                      style='Custom.TLabelframe',
                                      padding=15)
        position_frame.grid(row=1, column=0, sticky='ew', pady=(0, 10))
        position_frame.columnconfigure(0, weight=1)
        
        self.altitude_var = tk.StringVar()
        self.azimuth_var = tk.StringVar()
        
        ttk.Label(position_frame, textvariable=self.altitude_var,
                 style='Data.TLabel').grid(row=0, column=0, sticky='w', pady=(0, 5))
        ttk.Label(position_frame, textvariable=self.azimuth_var,
                 style='Data.TLabel').grid(row=1, column=0, sticky='w')
        
        # Distance information
        distance_frame = ttk.LabelFrame(self.data_container, 
                                      text="Distance", 
                                      style='Custom.TLabelframe',
                                      padding=15)
        distance_frame.grid(row=2, column=0, sticky='ew', pady=(0, 10))
        distance_frame.columnconfigure(0, weight=1)
        
        self.distance_km_var = tk.StringVar()
        self.distance_ls_var = tk.StringVar()
        
        ttk.Label(distance_frame, textvariable=self.distance_km_var,
                 style='Data.TLabel').grid(row=0, column=0, sticky='w', pady=(0, 5))
        ttk.Label(distance_frame, textvariable=self.distance_ls_var,
                 style='Data.TLabel').grid(row=1, column=0, sticky='w')
        
        # Location information
        location_info_frame = ttk.LabelFrame(self.data_container, 
                                           text="Observer Location", 
                                           style='Custom.TLabelframe',
                                           padding=15)
        location_info_frame.grid(row=3, column=0, sticky='ew')
        location_info_frame.columnconfigure(0, weight=1)
        
        self.location_info_var = tk.StringVar()
        self.coordinates_var = tk.StringVar()
        
        ttk.Label(location_info_frame, textvariable=self.location_info_var,
                 style='Data.TLabel', wraplength=300).grid(row=0, column=0, sticky='w', pady=(0, 5))
        ttk.Label(location_info_frame, textvariable=self.coordinates_var,
                 style='Data.TLabel').grid(row=1, column=0, sticky='w')
    
    def load_default_moon_image(self):
        """Load the default moon image from resources folder."""
        try:
            image_path = os.path.join("resources", "moon.png")
            if os.path.exists(image_path):
                # Load and resize image
                pil_image = Image.open(image_path)
                # Resize to fit the display area (400x400 max)
                pil_image.thumbnail((400, 400), Image.Resampling.LANCZOS)
                
                # Convert to PhotoImage for tkinter
                self.moon_image = ImageTk.PhotoImage(pil_image)
                self.moon_image_label.configure(image=self.moon_image)
                self.status_var.set("Default moon image loaded")
            else:
                # Create a placeholder if image doesn't exist
                self.create_placeholder_image()
                self.status_var.set("Default moon image not found - using placeholder")
        except Exception as e:
            self.create_placeholder_image()
            self.status_var.set(f"Error loading moon image: {str(e)}")
    
    def create_placeholder_image(self):
        """Create a simple placeholder image if moon.png is not available."""
        # Create a simple circle as placeholder
        from PIL import Image, ImageDraw
        
        img = Image.new('RGBA', (300, 300), (30, 42, 74, 255))  # Dark blue background
        draw = ImageDraw.Draw(img)
        
        # Draw a circle for the moon with gradient effect
        draw.ellipse([40, 40, 260, 260], fill=(200, 200, 200, 255), outline=(150, 150, 150, 255), width=2)
        
        # Add some crater-like features
        draw.ellipse([80, 100, 120, 140], fill=(160, 160, 160, 255))
        draw.ellipse([180, 160, 200, 180], fill=(170, 170, 170, 255))
        draw.ellipse([120, 200, 150, 230], fill=(165, 165, 165, 255))
        
        self.moon_image = ImageTk.PhotoImage(img)
        self.moon_image_label.configure(image=self.moon_image)
    
    def fetch_moon_data_threaded(self):
        """Fetch moon data in a separate thread to prevent GUI freezing."""
        # Disable button and start progress bar
        self.fetch_button.configure(state='disabled')
        self.progress.start()
        self.status_var.set("Fetching lunar data...")
        
        # Start thread for data fetching
        thread = threading.Thread(target=self.fetch_moon_data)
        thread.daemon = True
        thread.start()
    
    def fetch_moon_data(self):
        """Fetch moon data from the API."""
        try:
            location_name = self.location_entry.get().strip()
            if not location_name:
                location_name = "Los Angeles, CA"
            
            # Get coordinates
            location_data = self.location_service.get_coordinates(location_name)
            
            # Get lunar data
            lunar_data = self.lunar_service.get_moon_data(
                latitude=location_data["latitude"],
                longitude=location_data["longitude"]
            )
            
            # Store the data and location info
            self.current_lunar_data = lunar_data
            self.current_location_data = location_data
            
            # Update GUI in main thread
            self.root.after(0, self.update_display)
            
            # Try to render custom moon image
            self.root.after(100, self.render_custom_moon_image)
            
        except Exception as e:
            # Show error in main thread
            self.root.after(0, lambda: self.show_error(str(e)))
    
    def update_display(self):
        """Update the GUI with the fetched lunar data."""
        if not self.current_lunar_data or not hasattr(self, 'current_location_data'):
            return
        
        try:
            lunar_data = self.current_lunar_data
            location_data = self.current_location_data
            
            # Update phase information
            phase = lunar_data["phase"]
            self.phase_emoji_var.set(phase["emoji"])
            self.phase_name_var.set(phase["name"])
            self.illumination_var.set(f"Illumination: {phase['illumination']:.1f}%")
            self.age_var.set(f"Lunar Age: {phase['age']:.1f} days")
            
            # Update position information
            position = lunar_data["position"]
            visibility = "Above horizon" if position["altitude"] > 0 else "Below horizon"
            self.altitude_var.set(f"Altitude: {position['altitude']:.2f}° ({visibility})")
            
            # Convert azimuth to cardinal direction
            azimuth_direction = self.get_direction(position["azimuth"])
            self.azimuth_var.set(f"Azimuth: {position['azimuth']:.2f}° ({azimuth_direction})")
            
            # Update distance information
            distance = lunar_data["distance"]
            self.distance_km_var.set(f"{distance['km']:,.0f} km")
            self.distance_ls_var.set(f"{distance['light_seconds']:.2f} light seconds")
            
            # Update location information
            lat_dir = "N" if location_data["latitude"] >= 0 else "S"
            lon_dir = "E" if location_data["longitude"] >= 0 else "W"
            
            self.location_info_var.set(location_data["address"])
            self.coordinates_var.set(f"{abs(location_data['latitude']):.4f}° {lat_dir}, "
                                   f"{abs(location_data['longitude']):.4f}° {lon_dir}")
            
            # Stop progress bar and re-enable button
            self.progress.stop()
            self.fetch_button.configure(state='normal')
            self.status_var.set("Lunar data updated successfully")
            
        except Exception as e:
            self.show_error(f"Error updating display: {str(e)}")
    
    def render_custom_moon_image(self):
        """Call render.py to create a custom moon image and display it."""
        try:
            if not self.current_lunar_data:
                return
            
            # Import and call render.py
            import render
            
            # Call the render function with lunar data
            rendered_image_path = render.render_moon(self.current_lunar_data)
            
            if rendered_image_path and os.path.exists(rendered_image_path):
                # Load the rendered image
                pil_image = Image.open(rendered_image_path)
                pil_image.thumbnail((400, 400), Image.Resampling.LANCZOS)
                
                # Update the display
                self.moon_image = ImageTk.PhotoImage(pil_image)
                self.moon_image_label.configure(image=self.moon_image)
                self.status_var.set("Custom moon image rendered and displayed")
            else:
                self.status_var.set("Custom rendering failed - using default image")
                
        except ImportError:
            # render.py doesn't exist yet
            self.status_var.set("render.py not found - using default moon image")
        except Exception as e:
            self.status_var.set(f"Rendering error: {str(e)} - using default image")
    
    def get_direction(self, azimuth: float) -> str:
        """Convert azimuth angle to cardinal direction."""
        directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", 
                      "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
        index = round(azimuth / 22.5) % 16
        return directions[index]
    
    def show_error(self, error_message: str):
        """Display an error message to the user."""
        self.progress.stop()
        self.fetch_button.configure(state='normal')
        self.status_var.set(f"Error: {error_message}")
        messagebox.showerror("Error", error_message)

def main():
    """Main function to run the GUI application."""
    root = tk.Tk()
    app = LunarObserverGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()