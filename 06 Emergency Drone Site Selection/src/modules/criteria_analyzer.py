"""
Criteria analysis module for drone site selection.
"""

import geopandas as gpd
import numpy as np
import pandas as pd
from config.settings import DEFAULT_PARAMETERS
from shapely.geometry import MultiPolygon, Polygon
from shapely.ops import unary_union


class CriteriaAnalyzer:
    """
    A class to analyze spatial criteria for drone site selection.
    """

    def __init__(self, urban_data):
        """
        Initialize the criteria analyzer.

        Args:
            urban_data (dict): Dictionary containing urban data from OSMDataLoader
        """
        self.data = urban_data
        self.results = {}

    def analyze_demand_zones(self, service_radius):
        """
        Analyze demand zones around critical infrastructure.

        Args:
            service_radius (float): Service radius in meters

        Returns:
            dict: Demand zone analysis results
        """
        print("🎯 Analyzing demand zones...")

        if self.data["critical_infrastructure"].empty:
            return {}

        try:
            # Create buffers around critical infrastructure
            critical_gdf = self.data["critical_infrastructure"]
            buffers = critical_gdf.geometry.buffer(service_radius)

            # Create unified demand zone
            demand_zone = unary_union(buffers.tolist())

            # Calculate coverage statistics
            total_critical = len(critical_gdf)

            results = {
                "individual_buffers": gpd.GeoDataFrame(
                    geometry=buffers, crs=critical_gdf.crs
                ),
                "unified_demand_zone": gpd.GeoDataFrame(
                    geometry=[demand_zone], crs=critical_gdf.crs
                ),
                "service_radius": service_radius,
                "total_critical_points": total_critical,
                "demand_zone_area_sq_km": (
                    demand_zone.area / 1e6 if not demand_zone.is_empty else 0
                ),
            }

            self.results["demand_zones"] = results
            return results

        except Exception as e:
            print(f"❌ Error analyzing demand zones: {e}")
            return {}

    def analyze_exclusion_zones(self, road_buffer):
        """
        Analyze exclusion zones around roads.

        Args:
            road_buffer (float): Safety buffer distance in meters

        Returns:
            dict: Exclusion zone analysis results
        """
        print("🚧 Analyzing exclusion zones...")

        if self.data["roads"].empty:
            return {}

        try:
            roads_gdf = self.data["roads"]

            # Create buffers around roads
            road_buffers = roads_gdf.geometry.buffer(road_buffer)

            # Create unified exclusion zone
            exclusion_zone = unary_union(road_buffers.tolist())

            results = {
                "road_buffers": gpd.GeoDataFrame(
                    geometry=road_buffers, crs=roads_gdf.crs
                ),
                "unified_exclusion_zone": gpd.GeoDataFrame(
                    geometry=[exclusion_zone], crs=roads_gdf.crs
                ),
                "road_buffer": road_buffer,
                "exclusion_zone_area_sq_km": (
                    exclusion_zone.area / 1e6 if not exclusion_zone.is_empty else 0
                ),
            }

            self.results["exclusion_zones"] = results
            return results

        except Exception as e:
            print(f"❌ Error analyzing exclusion zones: {e}")
            return {}

    def evaluate_candidate_sites(self, demand_results, exclusion_results, min_area=100):
        """
        Evaluate candidate sites against all criteria.
        FIXED: Ensure only one geometry column is kept.

        Args:
            demand_results: Results from analyze_demand_zones
            exclusion_results: Results from analyze_exclusion_zones
            min_area (float): Minimum site area in square meters

        Returns:
            dict: Candidate site evaluation results
        """
        print("📊 Evaluating candidate sites...")

        if self.data["candidate_sites"].empty:
            return {}

        try:
            candidate_sites = self.data["candidate_sites"]
            demand_zone = demand_results.get("unified_demand_zone", gpd.GeoDataFrame())
            exclusion_zone = exclusion_results.get(
                "unified_exclusion_zone", gpd.GeoDataFrame()
            )

            if demand_zone.empty or exclusion_zone.empty:
                return {}

            # Extract geometries
            demand_geom = (
                demand_zone.geometry.iloc[0] if not demand_zone.empty else None
            )
            exclusion_geom = (
                exclusion_zone.geometry.iloc[0] if not exclusion_zone.empty else None
            )

            if demand_geom is None or exclusion_geom is None:
                return {}

            evaluated_sites = []

            for idx, site in candidate_sites.iterrows():
                site_geom = site.geometry

                # Criterion 1: Must intersect with demand zone
                intersects_demand = site_geom.intersects(demand_geom)

                if not intersects_demand:
                    continue

                # Criterion 2: Must not intersect with exclusion zone (or only minimally)
                safe_geom = site_geom.difference(exclusion_geom)

                if safe_geom.is_empty:
                    continue

                # Criterion 3: Minimum area requirement
                safe_area = safe_geom.area
                if safe_area < min_area:
                    continue

                # Calculate coverage percentage
                original_area = site_geom.area
                coverage_pct = (
                    (safe_area / original_area) * 100 if original_area > 0 else 0
                )

                # Calculate distance to nearest critical infrastructure
                distance_to_critical = self._calculate_min_distance_to_critical(
                    safe_geom
                )

                # FIXED: Only include essential data, avoid storing multiple geometry objects
                evaluated_sites.append(
                    {
                        "geometry": safe_geom,  # Keep only this geometry column
                        "site_id": idx,
                        "name": site.get("name", f"Site_{idx}"),
                        "original_area_sq_m": original_area,
                        "safe_area_sq_m": safe_area,
                        "coverage_percentage": coverage_pct,
                        "distance_to_critical_m": distance_to_critical,
                        "intersects_demand": intersects_demand,
                        "is_safe": True,
                    }
                )

            # Create results GeoDataFrame
            if evaluated_sites:
                results_gdf = gpd.GeoDataFrame(evaluated_sites, crs=candidate_sites.crs)

                results = {
                    "evaluated_sites": results_gdf,
                    "total_candidates": len(candidate_sites),
                    "feasible_sites": len(results_gdf),
                    "success_rate": (
                        (len(results_gdf) / len(candidate_sites)) * 100
                        if len(candidate_sites) > 0
                        else 0
                    ),
                }

                self.results["candidate_evaluation"] = results
                return results
            else:
                return {}

        except Exception as e:
            print(f"❌ Error evaluating candidate sites: {e}")
            return {}

    def _calculate_min_distance_to_critical(self, geometry):
        """Calculate minimum distance to critical infrastructure."""
        if self.data["critical_infrastructure"].empty:
            return float("inf")

        critical_geoms = self.data["critical_infrastructure"].geometry
        distances = [geometry.distance(crit_geom) for crit_geom in critical_geoms]

        return min(distances) if distances else float("inf")

    def get_analysis_summary(self):
        """Get comprehensive analysis summary."""
        summary = {
            "demand_analysis": {},
            "exclusion_analysis": {},
            "candidate_analysis": {},
        }

        if "demand_zones" in self.results:
            summary["demand_analysis"] = {
                "service_radius_m": self.results["demand_zones"]["service_radius"],
                "critical_points_covered": self.results["demand_zones"][
                    "total_critical_points"
                ],
                "demand_zone_area_km2": self.results["demand_zones"][
                    "demand_zone_area_sq_km"
                ],
            }

        if "exclusion_zones" in self.results:
            summary["exclusion_analysis"] = {
                "safety_buffer_m": self.results["exclusion_zones"]["road_buffer"],
                "exclusion_zone_area_km2": self.results["exclusion_zones"][
                    "exclusion_zone_area_sq_km"
                ],
            }

        if "candidate_evaluation" in self.results:
            candidate_results = self.results["candidate_evaluation"]
            summary["candidate_analysis"] = {
                "total_candidates": candidate_results["total_candidates"],
                "feasible_sites": candidate_results["feasible_sites"],
                "success_rate_pct": candidate_results["success_rate"],
                "total_safe_area_km2": candidate_results["evaluated_sites"][
                    "safe_area_sq_m"
                ].sum()
                / 1e6,
            }

        return summary
