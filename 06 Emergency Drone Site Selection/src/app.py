"""
Main Streamlit application for Drone Site Selection MCDA.
Fixed export issue in Step 5.
"""

import os
import sys

import numpy as np
import pandas as pd
import streamlit as st

# Add modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), "modules"))

from config.settings import DEFAULT_PARAMETERS, STREAMLIT_CONFIG
from modules.criteria_analyzer import CriteriaAnalyzer
from modules.data_loader import OSMDataLoader
from modules.mcda_engine import MCDAEngine
from modules.utils import ResultsExporter, ValidationUtils
from modules.visualizer import SiteSelectionVisualizer

# Configure Streamlit page
st.set_page_config(**STREAMLIT_CONFIG)


def main():
    """
    Main Streamlit application for drone site selection.
    """
    st.title("🚁 Intelligent Drone Station Siting System")
    st.markdown(
        """
    This application performs **Multi-Criteria Decision Analysis (MCDA)** to find optimal locations
    for emergency drone stations using **OpenStreetMap data** and **spatial analysis**.
    """
    )

    # Sidebar for user inputs
    st.sidebar.header("📍 Area Selection")
    place_name = st.sidebar.text_input(
        "Enter City/District Name:", value="Tehran, District 6, Iran"
    )

    st.sidebar.header("⚙️ Analysis Parameters")
    service_radius = st.sidebar.slider(
        "Service Radius (meters)", 100, 2000, DEFAULT_PARAMETERS["service_radius"]
    )
    road_buffer = st.sidebar.slider(
        "Safety Distance from Roads (meters)",
        10,
        100,
        DEFAULT_PARAMETERS["road_buffer"],
    )
    min_site_area = st.sidebar.slider(
        "Minimum Site Area (sq meters)", 50, 500, DEFAULT_PARAMETERS["min_site_area"]
    )
    top_sites_count = st.sidebar.slider("Number of Top Sites to Recommend", 3, 15, 5)

    # MCDA Weights
    st.sidebar.header("📊 MCDA Criteria Weights")
    st.sidebar.markdown("Adjust the importance of each criterion:")

    service_weight = st.sidebar.slider("Service Coverage Weight", 0.1, 0.5, 0.4)
    safety_weight = st.sidebar.slider("Safety Distance Weight", 0.1, 0.5, 0.3)
    area_weight = st.sidebar.slider("Site Area Weight", 0.1, 0.5, 0.2)
    accessibility_weight = st.sidebar.slider("Accessibility Weight", 0.0, 0.3, 0.1)

    # Normalize weights to sum to 1.0
    total_weight = service_weight + safety_weight + area_weight + accessibility_weight
    if total_weight != 1.0:
        st.sidebar.warning(
            f"Weights sum to {total_weight:.1f}. They will be normalized."
        )

    mcda_weights = {
        "service_coverage": service_weight,
        "safety_distance": safety_weight,
        "site_area": area_weight,
        "accessibility": accessibility_weight,
    }

    # Analysis button
    if st.sidebar.button("🚀 Run Spatial Analysis", type="primary"):
        run_complete_analysis(
            place_name,
            service_radius,
            road_buffer,
            min_site_area,
            top_sites_count,
            mcda_weights,
        )
    else:
        show_instructions()


def run_complete_analysis(
    place_name,
    service_radius,
    road_buffer,
    min_site_area,
    top_sites_count,
    mcda_weights,
):
    """
    Run the complete drone site selection analysis.
    FIXED: Export issue in Step 5
    """
    with st.spinner("🌐 Loading OSM data and performing spatial analysis..."):
        try:
            # Step 1: Load OSM Data
            st.header("📥 Step 1: Data Loading")
            data_loader = OSMDataLoader()
            urban_data = data_loader.load_city_data(place_name)

            # Validate data
            validation = ValidationUtils.validate_analysis_inputs(urban_data)
            st.text(ValidationUtils.generate_validation_report(validation))

            if not validation["is_valid"]:
                st.error("Cannot proceed with analysis due to data validation errors.")
                return

            # Display data summary
            data_summary = data_loader.get_data_summary(urban_data)
            display_data_summary(data_summary)

            # Step 2: Criteria Analysis
            st.header("🎯 Step 2: Spatial Criteria Analysis")
            criteria_analyzer = CriteriaAnalyzer(urban_data)

            # Analyze demand zones
            demand_results = criteria_analyzer.analyze_demand_zones(service_radius)

            # Analyze exclusion zones
            exclusion_results = criteria_analyzer.analyze_exclusion_zones(road_buffer)

            # Evaluate candidate sites
            candidate_results = criteria_analyzer.evaluate_candidate_sites(
                demand_results, exclusion_results, min_site_area
            )

            # Store all analysis results in a dictionary for export
            analysis_results_dict = {
                "demand_zones": demand_results,
                "exclusion_zones": exclusion_results,
                "candidate_evaluation": candidate_results,
            }

            # Display analysis summary
            analysis_summary = criteria_analyzer.get_analysis_summary()
            display_analysis_summary(analysis_summary)

            if candidate_results.get("feasible_sites", 0) == 0:
                st.warning(
                    "No feasible sites found with current parameters. Try adjusting criteria."
                )
                return

            # Step 3: MCDA Ranking
            st.header("🏆 Step 3: Multi-Criteria Decision Analysis")
            mcda_engine = MCDAEngine(mcda_weights)

            evaluated_sites = candidate_results["evaluated_sites"]
            ranked_sites = mcda_engine.calculate_site_scores(evaluated_sites)

            if ranked_sites.empty:
                st.error("No sites could be ranked. Check analysis parameters.")
                return

            # Generate recommendations
            mcda_results = mcda_engine.generate_recommendations(
                ranked_sites, top_sites_count
            )

            # Display MCDA results
            display_mcda_results(mcda_results)

            # Step 4: Visualizations
            st.header("📊 Step 4: Analysis Visualizations")
            visualizer = SiteSelectionVisualizer(urban_data)

            # Create main dashboard
            fig_dashboard = visualizer.create_analysis_dashboard(
                analysis_results_dict, mcda_results
            )
            st.pyplot(fig_dashboard)

            # Create score distribution chart
            if not ranked_sites.empty:
                fig_scores = visualizer.create_score_distribution_chart(ranked_sites)
                st.pyplot(fig_scores)

            # Step 5: Export Results - FIXED: Pass the dictionary instead of the analyzer object
            st.header("💾 Step 5: Results Export")
            export_paths = ResultsExporter.export_comprehensive_results(
                urban_data, analysis_results_dict, mcda_results
            )

            st.success("✅ Analysis completed successfully!")

            if export_paths:
                st.info(f"📁 Results exported to the 'output' directory")

                # Download buttons
                provide_download_links(mcda_results, urban_data, analysis_results_dict)
            else:
                st.warning(
                    "No results were exported. Check if there are any feasible sites."
                )

        except Exception as e:
            st.error(f"❌ Analysis failed: {e}")
            st.exception(e)


def display_data_summary(data_summary):
    """Display data loading summary."""
    col1, col2, col3 = st.columns(3)

    with col1:
        critical_count = data_summary.get("critical_infrastructure", {}).get("count", 0)
        st.metric("Critical Infrastructure Points", critical_count)

    with col2:
        candidate_count = data_summary.get("candidate_sites", {}).get("count", 0)
        st.metric("Candidate Sites", candidate_count)

    with col3:
        road_count = data_summary.get("roads", {}).get("count", 0)
        st.metric("Road Segments", road_count)


def display_analysis_summary(analysis_summary):
    """Display criteria analysis summary."""
    st.subheader("Criteria Analysis Summary")

    col1, col2, col3 = st.columns(3)

    with col1:
        demand_info = analysis_summary.get("demand_analysis", {})
        st.metric("Service Radius (m)", demand_info.get("service_radius_m", 0))
        st.metric("Critical Points", demand_info.get("critical_points_covered", 0))

    with col2:
        exclusion_info = analysis_summary.get("exclusion_analysis", {})
        st.metric("Safety Buffer (m)", exclusion_info.get("safety_buffer_m", 0))
        st.metric(
            "Exclusion Area (km²)",
            f"{exclusion_info.get('exclusion_zone_area_km2', 0):.2f}",
        )

    with col3:
        candidate_info = analysis_summary.get("candidate_analysis", {})
        st.metric("Feasible Sites", candidate_info.get("feasible_sites", 0))
        st.metric("Success Rate", f"{candidate_info.get('success_rate_pct', 0):.1f}%")


def display_mcda_results(mcda_results):
    """Display MCDA ranking results."""
    if not mcda_results:
        return

    st.subheader("Top Recommended Sites")

    # Display top sites table
    site_details = mcda_results.get("site_details", [])
    if site_details:
        # Create a DataFrame for display
        import pandas as pd

        display_data = []
        for site in site_details:
            display_data.append(
                {
                    "Rank": site["rank"],
                    "Site Name": site["name"],
                    "Category": site["category"],
                    "Composite Score": site["composite_score"],
                    "Safe Area (m²)": site["safe_area_sq_m"],
                    "Coverage %": site["coverage_percentage"],
                    "Distance to Critical (m)": site["distance_to_critical_m"],
                }
            )

        df_display = pd.DataFrame(display_data)
        st.dataframe(df_display, use_container_width=True)

    # Display summary statistics
    summary_stats = mcda_results.get("summary_stats", {})
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Sites Analyzed", summary_stats.get("total_sites_analyzed", 0))

    with col2:
        st.metric("Sites Recommended", summary_stats.get("sites_recommended", 0))

    with col3:
        st.metric("Best Score", f"{summary_stats.get('best_score', 0):.1f}")


def provide_download_links(mcda_results, urban_data, analysis_results):
    """Provide download links for results with safe JSON serialization."""
    st.subheader("Download Results")

    if mcda_results and "top_sites" in mcda_results:
        import pandas as pd

        # CSV download - this works fine
        csv_data = mcda_results["top_sites"].to_csv(index=False)
        st.download_button(
            label="📥 Download Ranked Sites (CSV)",
            data=csv_data,
            file_name="drone_site_rankings.csv",
            mime="text/csv",
        )

        # GeoJSON download - FIXED: Handle geometry serialization properly
        top_sites_gdf = mcda_results["top_sites"].copy()

        # Ensure we have a geometry column
        if "geometry" not in top_sites_gdf.columns:
            st.warning("No geometry column found for GeoJSON export")
            return

        try:
            # Method 1: Try geopandas to_json with proper handling
            geojson_data = top_sites_gdf.to_json()

            st.download_button(
                label="🗺️ Download Spatial Data (GeoJSON)",
                data=geojson_data,
                file_name="optimal_drone_sites.geojson",
                mime="application/geo+json",
            )

        except Exception as e:
            st.warning(
                f"Standard GeoJSON export failed: {e}. Using alternative method..."
            )

            # Method 2: Alternative using manual GeoJSON construction
            try:
                import geojson
                from shapely.geometry import mapping

                features = []
                for idx, row in top_sites_gdf.iterrows():
                    # Convert geometry to GeoJSON format
                    geom = row["geometry"]

                    # Create properties dict (exclude geometry)
                    properties = {}
                    for col in top_sites_gdf.columns:
                        if col != "geometry":
                            value = row[col]
                            # Convert non-serializable types
                            if hasattr(value, "__geo_interface__"):
                                properties[col] = str(value)
                            elif isinstance(value, (np.integer, np.int64)):
                                properties[col] = int(value)
                            elif isinstance(value, (np.floating, np.float64)):
                                properties[col] = float(value)
                            elif isinstance(value, (np.ndarray,)):
                                properties[col] = value.tolist()
                            else:
                                properties[col] = value

                    # Create feature
                    if hasattr(geom, "__geo_interface__"):
                        feature = geojson.Feature(
                            geometry=geom.__geo_interface__, properties=properties
                        )
                        features.append(feature)

                # Create feature collection
                feature_collection = geojson.FeatureCollection(features)
                geojson_str = geojson.dumps(feature_collection)

                st.download_button(
                    label="🗺️ Download Spatial Data (Alternative GeoJSON)",
                    data=geojson_str,
                    file_name="optimal_drone_sites.geojson",
                    mime="application/geo+json",
                )

            except Exception as alt_e:
                st.error(f"Alternative GeoJSON export also failed: {alt_e}")

                # Method 3: Simplified version - just export as CSV with WKT
                top_sites_gdf["geometry_wkt"] = top_sites_gdf["geometry"].apply(
                    lambda x: x.wkt if x else ""
                )
                simplified_df = top_sites_gdf.drop("geometry", axis=1)
                csv_wkt = simplified_df.to_csv(index=False)

                st.download_button(
                    label="📐 Download Sites with WKT Geometry (CSV)",
                    data=csv_wkt,
                    file_name="optimal_drone_sites_wkt.csv",
                    mime="text/csv",
                )

    # Additional download for all feasible sites
    if (
        analysis_results.get("candidate_evaluation")
        and "evaluated_sites" in analysis_results["candidate_evaluation"]
    ):

        feasible_sites = analysis_results["candidate_evaluation"]["evaluated_sites"]
        if not feasible_sites.empty:
            # Clean the DataFrame for export
            feasible_clean = feasible_sites.copy()

            # Remove any non-serializable columns
            columns_to_keep = []
            for col in feasible_clean.columns:
                try:
                    # Test if column can be serialized
                    sample = (
                        feasible_clean[col].iloc[0] if len(feasible_clean) > 0 else None
                    )
                    if hasattr(sample, "__geo_interface__") and col != "geometry":
                        # Skip additional geometry columns
                        continue
                    columns_to_keep.append(col)
                except:
                    columns_to_keep.append(col)

            feasible_clean = feasible_clean[columns_to_keep]
            feasible_csv = feasible_clean.to_csv(index=False)

            st.download_button(
                label="📋 Download All Feasible Sites (CSV)",
                data=feasible_csv,
                file_name="all_feasible_sites.csv",
                mime="text/csv",
            )


def show_instructions():
    """Show application instructions."""
    st.info(
        """
    ### 🚀 How to Use This Application:

    1. **Enter a location** in the sidebar (city, district, or area name)
    2. **Adjust analysis parameters**:
       - Service Radius: How far drones should reach critical infrastructure
       - Safety Buffer: Minimum distance from major roads
       - Minimum Site Area: Smallest acceptable site size
    3. **Set MCDA weights** to prioritize different criteria
    4. **Click 'Run Spatial Analysis'** to start the process

    The analysis will proceed through these steps:
    - 📥 Data loading from OpenStreetMap
    - 🎯 Spatial criteria analysis
    - 🏆 Multi-criteria decision analysis
    - 📊 Results visualization
    - 💾 Results export
    """
    )

    # Example parameters
    st.subheader("💡 Example Use Cases:")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
        **🆕 Emergency Response Drones:**
        - Service Radius: 500-1000m
        - Safety Buffer: 30-50m
        - Min Area: 100-200 m²
        - Priority: Service Coverage
        """
        )

    with col2:
        st.markdown(
            """
        **📦 Delivery Drones:**
        - Service Radius: 1000-2000m
        - Safety Buffer: 20-30m
        - Min Area: 50-100 m²
        - Priority: Accessibility
        """
        )


if __name__ == "__main__":
    main()
