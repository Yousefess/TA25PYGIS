"""
Configuration settings for Drone Site Selection MCDA Project.
"""

# OSM Data Configuration
OSM_TAGS = {
    "critical_infrastructure": {
        "amenity": ["school", "hospital", "clinic", "university"],
        "building": ["hospital", "school"],
    },
    "candidate_sites": {
        "leisure": ["park", "garden", "recreation_ground"],
        "landuse": ["grass", "meadow", "recreation_ground"],
        "natural": ["wood", "grassland"],
    },
    "exclusion_zones": {"highway": ["motorway", "trunk", "primary", "secondary"]},
}

# Analysis Parameters
DEFAULT_PARAMETERS = {
    "service_radius": 500,  # meters
    "road_buffer": 30,  # meters
    "min_site_area": 100,  # square meters
    "target_crs": "EPSG:3857",  # Web Mercator for metric calculations
}

# MCDA Weights (can be adjusted by users)
CRITERIA_WEIGHTS = {
    "service_coverage": 0.4,
    "safety_distance": 0.3,
    "site_area": 0.2,
    "accessibility": 0.1,
}

# Visualization Settings
COLOR_SCHEME = {
    "critical_infrastructure": "#e74c3c",  # Red
    "candidate_sites": "#27ae60",  # Green
    "demand_zones": "#3498db",  # Blue
    "exclusion_zones": "#f39c12",  # Orange
    "optimal_sites": "#9b59b6",  # Purple
    "roads": "#7f8c8d",  # Gray
}

# Streamlit Config
STREAMLIT_CONFIG = {
    "page_title": " Intelligent Drone Station Siting System",
    "page_icon": "🚁",
    "layout": "wide",
}
