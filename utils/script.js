// utils/script.js - Frontend JavaScript for Lunar Phase Calculator

let currentData = null;

/**
 * Initialize the application when the page loads
 */
window.addEventListener('load', function() {
    initializeApp();
});

/**
 * Initialize the application with geolocation detection
 */
function initializeApp() {
    // Try to detect user location for better default
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function(position) {
                // For now, just use default location
                // In future, could reverse geocode coordinates to location name
                console.log('Geolocation detected:', position.coords);
                fetchLunarData();
            },
            function(error) {
                console.log('Geolocation failed:', error.message);
                // Use default location if geolocation fails
                fetchLunarData();
            },
            {
                timeout: 5000,
                enableHighAccuracy: false
            }
        );
    } else {
        console.log('Geolocation not supported by browser');
        fetchLunarData();
    }
    
    // Set up event listeners
    setupEventListeners();
}

/**
 * Set up event listeners for user interactions
 */
function setupEventListeners() {
    // Allow Enter key to trigger search
    document.getElementById('locationInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            fetchLunarData();
        }
    });
    
    // Add input validation and auto-suggestions in future
    document.getElementById('locationInput').addEventListener('input', function(e) {
        // Could add live search suggestions here
        validateLocationInput(e.target.value);
    });
}

/**
 * Validate location input (basic validation for now)
 */
function validateLocationInput(value) {
    const input = document.getElementById('locationInput');
    const button = document.querySelector('.location-input button');
    
    if (value.trim().length < 2) {
        input.style.borderColor = '#ff6b6b';
        button.disabled = true;
    } else {
        input.style.borderColor = '#2196f3';
        button.disabled = false;
    }
}

/**
 * Fetch lunar data from the backend API
 */
async function fetchLunarData() {
    const location = document.getElementById('locationInput').value.trim() || 'Los Angeles, CA';
    const loading = document.getElementById('loading');
    const content = document.getElementById('content');
    const error = document.getElementById('error');

    // Show loading state
    showLoading(true);
    hideError();
    hideContent();

    try {
        const response = await fetch(`/lunar-data?location=${encodeURIComponent(location)}`);
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }
        
        currentData = await response.json();
        console.log('Lunar data received:', currentData);
        
        displayLunarData(currentData);
        showContent();
        
    } catch (err) {
        console.error('Error fetching lunar data:', err);
        showError(`Failed to fetch lunar data: ${err.message}`);
    } finally {
        showLoading(false);
    }
}

/**
 * Display the fetched lunar data in the UI
 */
function displayLunarData(data) {
    displayMoonImage(data);
    displayLibrationInfo(data);
    displayDataSections(data);
    updatePageTitle(data);
}

/**
 * Display moon image and related information
 */
function displayMoonImage(data) {
    const moonImg = document.getElementById('moonImg');
    const moonImage = document.getElementById('moonImage');
    
    // For now, just use the default moon.png
    // In future, this will call render.js to create custom moon phase image
    moonImg.src = '/static/moon.png';
    moonImg.alt = `${data.phase.name} - ${data.phase.illumination.toFixed(1)}% illuminated`;
    
    // Add visual indicators for phase
    moonImage.style.filter = `brightness(${0.7 + (data.phase.illumination / 100) * 0.5})`;
    
    // Apply libration rotation effect (subtle visual indication)
    const rotationAngle = data.libration.total * 2; // Amplify for visibility
    moonImg.style.transform = `rotate(${rotationAngle}deg)`;
}

/**
 * Display libration information below the moon image
 */
function displayLibrationInfo(data) {
    const librationInfo = document.getElementById('librationInfo');
    
    const librationMagnitude = data.libration.total;
    let librationDescription;
    
    if (librationMagnitude < 2) {
        librationDescription = "minimal wobble";
    } else if (librationMagnitude < 4) {
        librationDescription = "moderate wobble";
    } else {
        librationDescription = "significant wobble";
    }
    
    librationInfo.innerHTML = `
        <h4>🌀 Libration Effects</h4>
        <p>
            The Moon is currently experiencing a <strong>${librationDescription}</strong> 
            of ${librationMagnitude.toFixed(3)}° from its mean position.
        </p>
        <p style="margin-top: 8px; font-size: 0.85rem;">
            Longitude: ${data.libration.longitude.toFixed(3)}° | 
            Latitude: ${data.libration.latitude.toFixed(3)}°
        </p>
    `;
}

/**
 * Create and display all data sections
 */
function displayDataSections(data) {
    const dataPanel = document.getElementById('dataPanel');
    
    // Define data sections in order of importance
    const sections = [
        {
            title: "🌙 Current Moon Phase",
            priority: 1,
            items: [
                { label: "Phase", value: `${data.phase.emoji} ${data.phase.name}` },
                { label: "Illumination", value: `${data.phase.illumination.toFixed(1)}%` },
                { label: "Lunar Age", value: `${data.phase.age.toFixed(1)} days` }
            ]
        },
        {
            title: "👁️ Visibility Status",
            priority: 2,
            items: [
                { 
                    label: "Status", 
                    value: data.position.altitude > 0 ? "Above Horizon ✅" : "Below Horizon ❌" 
                },
                { label: "Altitude", value: `${data.position.altitude.toFixed(2)}°` },
                { 
                    label: "Next Phase", 
                    value: `${data.next_phase.name} in ${data.next_phase.days.toFixed(1)} days` 
                }
            ]
        },
        {
            title: "📏 Distance & Size",
            priority: 3,
            items: [
                { label: "Distance", value: `${data.distance.km.toLocaleString()} km` },
                { label: "Light Travel Time", value: `${data.distance.light_seconds.toFixed(2)} seconds` },
                { label: "Angular Size", value: `${data.angular_diameter.toFixed(4)}°` }
            ]
        },
        {
            title: "🧭 Position Details",
            priority: 4,
            items: [
                { 
                    label: "Azimuth", 
                    value: `${data.position.azimuth.toFixed(2)}° (${getDirection(data.position.azimuth)})` 
                },
                { label: "Right Ascension", value: `${data.position.right_ascension.toFixed(2)}h` },
                { label: "Declination", value: `${data.position.declination.toFixed(2)}°` }
            ]
        },
        {
            title: "🌀 Libration (Wobble)",
            priority: 5,
            items: [
                { label: "Longitude Libration", value: `${data.libration.longitude.toFixed(3)}°` },
                { label: "Latitude Libration", value: `${data.libration.latitude.toFixed(3)}°` },
                { label: "Total Wobble", value: `${data.libration.total.toFixed(3)}°` },
                { label: "Diurnal Effect", value: `${Math.sqrt(data.libration.diurnal_longitude**2 + data.libration.diurnal_latitude**2).toFixed(4)}°` }
            ]
        },
        {
            title: "🔄 Orientation Effects",
            priority: 6,
            items: [
                { label: "Position Angle", value: `${data.orientation.position_angle.toFixed(2)}°` },
                { label: "Phase Angle", value: `${data.phase.angle.toFixed(2)}°` },
                { label: "Observer Latitude", value: `${data.observer.latitude.toFixed(4)}°` },
                { label: "Julian Day", value: `${data.julian_day.toFixed(2)}` }
            ]
        }
    ];

    // Clear existing content
    dataPanel.innerHTML = '';
    
    // Create and append each section
    sections.forEach(section => {
        const sectionElement = createDataSection(section);
        dataPanel.appendChild(sectionElement);
    });
}

/**
 * Create a data section element
 */
function createDataSection(section) {
    const sectionDiv = document.createElement('div');
    sectionDiv.className = `data-section priority-${section.priority}`;
    
    // Create title
    const title = document.createElement('h3');
    title.innerHTML = section.title;
    sectionDiv.appendChild(title);
    
    // Create data items
    section.items.forEach(item => {
        const itemDiv = document.createElement('div');
        itemDiv.className = 'data-item';
        itemDiv.innerHTML = `
            <span class="data-label">${item.label}:</span>
            <span class="data-value">${item.value}</span>
        `;
        sectionDiv.appendChild(itemDiv);
    });
    
    return sectionDiv;
}

/**
 * Convert azimuth angle to cardinal direction
 */
function getDirection(azimuth) {
    const directions = [
        "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", 
        "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"
    ];
    const index = Math.round(azimuth / 22.5) % 16;
    return directions[index];
}

/**
 * Update page title with current moon phase
 */
function updatePageTitle(data) {
    document.title = `${data.phase.emoji} ${data.phase.name} - Lunar Phase Calculator`;
}

/**
 * Show/hide loading state
 */
function showLoading(show) {
    const loading = document.getElementById('loading');
    loading.style.display = show ? 'block' : 'none';
}

/**
 * Show content area
 */
function showContent() {
    const content = document.getElementById('content');
    content.style.display = 'grid';
}

/**
 * Hide content area
 */
function hideContent() {
    const content = document.getElementById('content');
    content.style.display = 'none';
}

/**
 * Show error message
 */
function showError(message) {
    const error = document.getElementById('error');
    error.textContent = message;
    error.style.display = 'block';
}

/**
 * Hide error message
 */
function hideError() {
    const error = document.getElementById('error');
    error.style.display = 'none';
}

/**
 * Format numbers for better readability
 */
function formatNumber(num, decimals = 2) {
    return new Intl.NumberFormat('en-US', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    }).format(num);
}

/**
 * Get relative time description
 */
function getRelativeTime(days) {
    if (days < 1) {
        const hours = Math.round(days * 24);
        return `${hours} hour${hours !== 1 ? 's' : ''}`;
    } else if (days < 7) {
        return `${Math.round(days)} day${Math.round(days) !== 1 ? 's' : ''}`;
    } else {
        const weeks = Math.round(days / 7);
        return `${weeks} week${weeks !== 1 ? 's' : ''}`;
    }
}

/**
 * Export current data as JSON (for debugging/development)
 */
function exportData() {
    if (currentData) {
        const dataStr = JSON.stringify(currentData, null, 2);
        const dataBlob = new Blob([dataStr], {type: 'application/json'});
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `lunar-data-${new Date().toISOString().split('T')[0]}.json`;
        link.click();
        URL.revokeObjectURL(url);
    }
}

/**
 * Handle keyboard shortcuts
 */
document.addEventListener('keydown', function(e) {
    // Ctrl+R or F5 to refresh data
    if ((e.ctrlKey && e.key === 'r') || e.key === 'F5') {
        e.preventDefault();
        fetchLunarData();
    }
    
    // Ctrl+E to export data (for development)
    if (e.ctrlKey && e.key === 'e') {
        e.preventDefault();
        exportData();
    }
});

/**
 * Add smooth scrolling for any future navigation
 */
function scrollToElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// Expose some functions globally for debugging
window.lunarApp = {
    fetchLunarData,
    exportData,
    currentData: () => currentData
};