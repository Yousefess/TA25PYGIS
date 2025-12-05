import os
import sys

import streamlit as st

# Add modules path
sys.path.append(os.path.join(os.path.dirname(__file__), "modules"))

from data_generator import TrafficDataGenerator
from data_processor import TrafficDataProcessor
from utils import (create_download_section, display_analysis_results,
                   display_data_summary)
from visualizer import TrafficVisualizer


def main():
    """
    Main function for the Traffic Analysis Streamlit application.

    This function sets up the Streamlit interface and coordinates
    between different modules for data generation, processing,
    visualization, and user interaction.
    """
    # Page configuration
    st.set_page_config(
        page_title="Urban Traffic Analyzer",
        page_icon="🚦",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Title and introduction
    st.title("🚦 Urban Traffic Pattern Analyzer")
    st.markdown(
        """
    This application provides comprehensive analysis of urban traffic patterns.
    **Features:**
    - Synthetic traffic data generation
    - Traffic pattern analysis
    - Data visualization
    - Results export
    """
    )
    st.markdown("---")

    # Sidebar for settings
    st.sidebar.title("⚙️ Project Settings")
    n_records = st.sidebar.slider("Number of Data Records", 100, 5000, 1000)
    auto_refresh = st.sidebar.checkbox("Auto Refresh", value=True)

    # Analysis start button
    if st.sidebar.button("🚀 Start Traffic Analysis", type="primary"):
        run_analysis(n_records)

    # Project information
    st.sidebar.markdown("---")
    st.sidebar.info(
        """
    **📚 Libraries Used:**
    - Streamlit
    - Pandas
    - NumPy
    - Matplotlib
    - Faker
    """
    )


def run_analysis(n_records):
    """
    Run complete traffic analysis pipeline.

    Args:
        n_records (int): Number of records to generate and analyze
    """

    # Step 1: Data Generation
    with st.status("Generating traffic data...", expanded=True) as status:
        generator = TrafficDataGenerator()
        raw_data = generator.generate_traffic_data(n_records)
        status.update(label="✅ Data successfully generated", state="complete")

    # Step 2: Data Processing
    with st.status("Processing and analyzing data...", expanded=True) as status:
        processor = TrafficDataProcessor(raw_data)
        processed_data = processor.add_calculated_features()
        analysis_results = processor.analyze_traffic_patterns()
        status.update(label="✅ Data processing completed", state="complete")

    # Display success message
    st.success("✅ Analysis completed successfully!")

    # Display summary
    display_data_summary(processed_data, processor)

    # Display data preview
    st.subheader("📋 Data Preview")
    st.dataframe(processed_data.head(10), width="content")

    # Display analysis results
    display_analysis_results(analysis_results)

    # Step 3: Visualizations
    with st.status("Creating visualizations...", expanded=True) as status:
        visualizer = TrafficVisualizer(processed_data, analysis_results)

        # Main charts
        main_fig = visualizer.create_main_dashboard()
        st.subheader("📈 Traffic Analysis Dashboard")
        st.pyplot(main_fig)

        # Supplementary charts
        supplementary_fig = visualizer.create_supplementary_charts()
        st.subheader("📊 Supplementary Analysis")
        st.pyplot(supplementary_fig)

        status.update(label="✅ Visualization completed", state="complete")

    # Download section
    create_download_section(processed_data)


if __name__ == "__main__":
    main()
