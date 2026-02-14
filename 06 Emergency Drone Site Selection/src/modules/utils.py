"""
Utility functions for the drone site selection project.
Fixed export functions to handle the analysis results properly.
"""

import json
from datetime import datetime

import geopandas as gpd
import numpy as np
import pandas as pd


class ResultsExporter:
    """
    A class for exporting analysis results to various formats.
    Fixed to handle analysis results dictionary properly.
    """

    @staticmethod
    def export_comprehensive_results(
        urban_data, analysis_results, mcda_results, output_dir="output"
    ):
        """
        Export all analysis results to files.
        FIXED: Now properly handles analysis_results dictionary.

        Args:
            urban_data: Original urban data
            analysis_results: Dictionary with analysis results
            mcda_results: MCDA ranking results
            output_dir: Output directory
        """
        import os

        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        try:
            # Export spatial data
            spatial_paths = ResultsExporter._export_spatial_data(
                urban_data, analysis_results, output_dir, timestamp
            )

            # Export analysis summary
            summary_path = ResultsExporter._export_analysis_summary(
                analysis_results, mcda_results, output_dir, timestamp
            )

            # Export ranked sites
            ranked_path = ResultsExporter._export_ranked_sites(
                mcda_results, output_dir, timestamp
            )

            return {
                "spatial_data": spatial_paths,
                "analysis_summary": summary_path,
                "ranked_sites": ranked_path,
            }
        except Exception as e:
            print(f"❌ Error exporting results: {e}")
            return {}

    @staticmethod
    def _export_spatial_data(urban_data, analysis_results, output_dir, timestamp):
        """Export spatial data to GeoJSON files."""
        paths = {}

        try:
            # Export original data
            for key, gdf in urban_data.items():
                if not gdf.empty and hasattr(gdf, "to_file"):
                    path = f"{output_dir}/{key}_{timestamp}.geojson"
                    gdf.to_file(path, driver="GeoJSON")
                    paths[key] = path

            # Export analysis results - FIXED: Check if key exists in dictionary
            if (
                "candidate_evaluation" in analysis_results
                and "evaluated_sites" in analysis_results["candidate_evaluation"]
            ):

                evaluated_sites = analysis_results["candidate_evaluation"][
                    "evaluated_sites"
                ]
                if not evaluated_sites.empty and hasattr(evaluated_sites, "to_file"):
                    path = f"{output_dir}/evaluated_sites_{timestamp}.geojson"
                    evaluated_sites.to_file(path, driver="GeoJSON")
                    paths["evaluated_sites"] = path

            # Export demand zones if available
            if (
                "demand_zones" in analysis_results
                and "unified_demand_zone" in analysis_results["demand_zones"]
            ):

                demand_zone = analysis_results["demand_zones"]["unified_demand_zone"]
                if not demand_zone.empty and hasattr(demand_zone, "to_file"):
                    path = f"{output_dir}/demand_zone_{timestamp}.geojson"
                    demand_zone.to_file(path, driver="GeoJSON")
                    paths["demand_zone"] = path

            # Export exclusion zones if available
            if (
                "exclusion_zones" in analysis_results
                and "unified_exclusion_zone" in analysis_results["exclusion_zones"]
            ):

                exclusion_zone = analysis_results["exclusion_zones"][
                    "unified_exclusion_zone"
                ]
                if not exclusion_zone.empty and hasattr(exclusion_zone, "to_file"):
                    path = f"{output_dir}/exclusion_zone_{timestamp}.geojson"
                    exclusion_zone.to_file(path, driver="GeoJSON")
                    paths["exclusion_zone"] = path

            return paths

        except Exception as e:
            print(f"❌ Error exporting spatial data: {e}")
            return {}

    @staticmethod
    def _export_analysis_summary(analysis_results, mcda_results, output_dir, timestamp):
        """Export analysis summary to JSON."""
        try:
            summary = {}

            # Add criteria analysis summary from the results
            if analysis_results:
                summary["criteria_analysis"] = {
                    "demand_analysis": analysis_results.get("demand_zones", {}),
                    "exclusion_analysis": analysis_results.get("exclusion_zones", {}),
                    "candidate_analysis": analysis_results.get(
                        "candidate_evaluation", {}
                    ),
                }

            # Add MCDA results summary
            if mcda_results and "summary_stats" in mcda_results:
                summary["mcda_results"] = mcda_results["summary_stats"]

            # Add timestamp and metadata
            summary["metadata"] = {
                "analysis_timestamp": timestamp,
                "total_sites_recommended": (
                    len(mcda_results["top_sites"])
                    if mcda_results and "top_sites" in mcda_results
                    else 0
                ),
            }

            path = f"{output_dir}/analysis_summary_{timestamp}.json"
            with open(path, "w") as f:
                json.dump(
                    summary, f, indent=2, default=ResultsExporter._json_serializer
                )

            return path

        except Exception as e:
            print(f"❌ Error exporting analysis summary: {e}")
            return None

    @staticmethod
    def _export_ranked_sites(mcda_results, output_dir, timestamp):
        """Export ranked sites to CSV."""
        try:
            if not mcda_results or "top_sites" not in mcda_results:
                return None

            ranked_df = mcda_results["top_sites"]

            if ranked_df.empty:
                return None

            # Create a non-spatial version for CSV
            csv_data = (
                ranked_df.drop("geometry", axis=1)
                if "geometry" in ranked_df.columns
                else ranked_df
            )

            path = f"{output_dir}/ranked_sites_{timestamp}.csv"
            csv_data.to_csv(path, index=False)

            return path

        except Exception as e:
            print(f"❌ Error exporting ranked sites: {e}")
            return None

    @staticmethod
    def _json_serializer(obj):
        """Custom JSON serializer for objects not serializable by default json code"""
        if isinstance(obj, (np.integer, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64)):
            return float(obj)
        elif isinstance(obj, (np.ndarray,)):
            return obj.tolist()
        elif isinstance(obj, (pd.Timestamp, datetime)):
            return obj.isoformat()
        elif hasattr(obj, "isoformat"):
            return obj.isoformat()
        else:
            return str(obj)


class ValidationUtils:
    """
    Utility class for data validation.
    """

    @staticmethod
    def validate_analysis_inputs(urban_data):
        """
        Validate urban data for analysis.

        Args:
            urban_data: Dictionary of GeoDataFrames

        Returns:
            dict: Validation results
        """
        validation = {"is_valid": True, "warnings": [], "errors": []}

        # Check for required data
        required_keys = ["critical_infrastructure", "candidate_sites", "roads"]
        for key in required_keys:
            if key not in urban_data or urban_data[key].empty:
                validation["warnings"].append(f"Missing or empty data: {key}")

        # Check for sufficient candidate sites
        if (
            validation["is_valid"]
            and "candidate_sites" in urban_data
            and len(urban_data["candidate_sites"]) < 3
        ):
            validation["warnings"].append("Very few candidate sites found")

        # Check coordinate reference system
        for key, gdf in urban_data.items():
            if not gdf.empty and gdf.crs is None:
                validation["errors"].append(f"Missing CRS in {key}")
                validation["is_valid"] = False

        return validation

    @staticmethod
    def generate_validation_report(validation_results):
        """Generate a formatted validation report."""
        report = []

        if validation_results["is_valid"]:
            report.append("✅ Data validation passed")
        else:
            report.append("❌ Data validation failed")

        if validation_results["warnings"]:
            report.append("\n⚠️  Warnings:")
            for warning in validation_results["warnings"]:
                report.append(f"   - {warning}")

        if validation_results["errors"]:
            report.append("\n❌ Errors:")
            for error in validation_results["errors"]:
                report.append(f"   - {error}")

        return "\n".join(report)
