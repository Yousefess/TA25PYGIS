"""
Data loading module for fetching and processing OSM data.
"""

import geopandas as gpd
import osmnx as ox
import pandas as pd
from config.settings import DEFAULT_PARAMETERS, OSM_TAGS


class OSMDataLoader:
    """
    A class to load and preprocess OpenStreetMap data for drone site selection.
    """

    def __init__(self):
        """Initialize the data loader with OSMnx settings."""
        ox.settings.log_console = True
        ox.settings.use_cache = True
        ox.settings.timeout = 300

    def load_city_data(self, place_name):
        """
        Load comprehensive OSM data for a given city/area.

        Args:
            place_name (str): Name of the city or area

        Returns:
            dict: Dictionary containing all loaded GeoDataFrames
        """
        print(f"🗺️ Loading OSM data for {place_name}...")

        try:
            data = {}

            # Load critical infrastructure
            data["critical_infrastructure"] = self._load_critical_infrastructure(
                place_name
            )

            # Load candidate sites (parks and open spaces)
            data["candidate_sites"] = self._load_candidate_sites(place_name)

            # Load road network for exclusion zones
            data["roads"] = self._load_road_network(place_name)

            # Load urban area boundary
            data["urban_area"] = self._load_urban_area(place_name)

            # Reproject all data to metric CRS
            data = self._reproject_data(data)

            print("✅ OSM data loaded successfully!")
            return data

        except Exception as e:
            print(f"❌ Error loading OSM data: {e}")
            raise

    def _load_critical_infrastructure(self, place_name):
        """Load critical infrastructure points."""
        try:
            gdf = ox.features_from_place(
                place_name, tags=OSM_TAGS["critical_infrastructure"]
            )

            # Filter to points and valid geometries
            gdf = gdf[gdf.geometry.notna() & gdf.geometry.is_valid]
            point_mask = gdf.geometry.type.isin(["Point", "MultiPoint"])
            gdf = gdf[point_mask]

            print(f"✅ Loaded {len(gdf)} critical infrastructure points")
            return gdf

        except Exception as e:
            print(f"⚠️ Error loading critical infrastructure: {e}")
            return gpd.GeoDataFrame()

    def _load_candidate_sites(self, place_name):
        """Load potential candidate sites (parks, open spaces)."""
        try:
            gdf = ox.features_from_place(place_name, tags=OSM_TAGS["candidate_sites"])

            # Filter to polygons and valid geometries
            gdf = gdf[gdf.geometry.notna() & gdf.geometry.is_valid]
            polygon_mask = gdf.geometry.type.isin(["Polygon", "MultiPolygon"])
            gdf = gdf[polygon_mask]

            # Calculate area
            gdf_proj = gdf.to_crs(DEFAULT_PARAMETERS["target_crs"])
            gdf["area_sq_m"] = gdf_proj.geometry.area
            gdf = gdf.to_crs("EPSG:4326")

            print(f"✅ Loaded {len(gdf)} candidate sites")
            return gdf

        except Exception as e:
            print(f"⚠️ Error loading candidate sites: {e}")
            return gpd.GeoDataFrame()

    def _load_road_network(self, place_name):
        """Load road network for exclusion zones."""
        try:
            # Get road network
            graph = ox.graph_from_place(place_name, network_type="drive", simplify=True)

            # Convert to GeoDataFrame
            gdf_roads = ox.graph_to_gdfs(graph, nodes=False, edges=True)

            # Filter to major roads only
            road_mask = gdf_roads["highway"].isin(
                OSM_TAGS["exclusion_zones"]["highway"]
            )
            gdf_roads = gdf_roads[road_mask]

            print(f"✅ Loaded {len(gdf_roads)} road segments")
            return gdf_roads

        except Exception as e:
            print(f"⚠️ Error loading road network: {e}")
            return gpd.GeoDataFrame()

    def _load_urban_area(self, place_name):
        """Load urban area boundary."""
        try:
            gdf = ox.geocode_to_gdf(place_name)
            print("✅ Loaded urban area boundary")
            return gdf
        except Exception as e:
            print(f"⚠️ Error loading urban area: {e}")
            # Create a default bounding box
            return ox.utils_geo.bbox_to_poly(
                *ox.utils_geo.bbox_from_point((35.6892, 51.3890), dist=5000)
            )

    def _reproject_data(self, data):
        """Reproject all data to metric CRS."""
        target_crs = DEFAULT_PARAMETERS["target_crs"]

        for key, gdf in data.items():
            if not gdf.empty:
                data[key] = gdf.to_crs(target_crs)

        return data

    def get_data_summary(self, data):
        """Generate summary of loaded data."""
        summary = {}

        for key, gdf in data.items():
            summary[key] = {
                "count": len(gdf),
                "crs": str(gdf.crs) if not gdf.empty else "No data",
                "geometry_types": (
                    gdf.geometry.type.unique().tolist() if not gdf.empty else []
                ),
            }

            if key == "candidate_sites" and not gdf.empty:
                summary[key]["total_area_sq_km"] = gdf["area_sq_m"].sum() / 1e6
                summary[key]["avg_area_sq_m"] = gdf["area_sq_m"].mean()

        return summary
