from datetime import datetime

import pandas as pd
import streamlit as st


def display_data_summary(data, processor):
    """
    Display summary statistics of the traffic data.

    Args:
        data (pandas.DataFrame): Traffic data
        processor (TrafficDataProcessor): Data processor instance
    """
    summary = processor.get_summary_statistics()

    # Create metrics columns
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Records", f"{summary['total_records']:,}")
    with col2:
        st.metric("Avg Vehicle Count", f"{summary['avg_vehicle_count']:.1f}")
    with col3:
        st.metric("Average Speed", f"{summary['avg_speed']:.1f} km/h")
    with col4:
        st.metric("Avg Traffic Index", f"{summary['avg_traffic_index']:.2f}")

    # Display date range
    start_date = summary["date_range"]["start"].strftime("%Y-%m-%d %H:%M")
    end_date = summary["date_range"]["end"].strftime("%Y-%m-%d %H:%M")
    st.caption(f"📅 Data Time Range: {start_date} to {end_date}")


def create_download_section(data):
    """
    Create data download section in Streamlit app.

    Args:
        data (pandas.DataFrame): Data to download
    """
    st.subheader("💾 Download Data")

    col1, col2 = st.columns(2)

    with col1:
        # CSV download
        csv = data.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download as CSV",
            data=csv,
            file_name=f"traffic_data_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
        )

    with col2:
        # Excel download
        excel_buffer = pd.ExcelWriter("src/data/traffic_data.xlsx", engine="xlsxwriter")
        data.to_excel(excel_buffer, index=False, sheet_name="TrafficData")
        excel_buffer.close()

        with open("traffic_data.xlsx", "rb") as f:
            excel_data = f.read()

        st.download_button(
            label="Download as Excel",
            data=excel_data,
            file_name=f"traffic_data_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.ms-excel",
        )


def display_analysis_results(analysis_results):
    """
    Display detailed analysis results in tabs.

    Args:
        analysis_results (dict): Analysis results from TrafficDataProcessor
    """
    st.subheader("📊 Detailed Analysis Results")

    tab1, tab2, tab3 = st.tabs(
        ["Hourly Analysis", "Daily Analysis", "Road Type Analysis"]
    )

    with tab1:
        st.write("### Hourly Traffic Patterns")
        st.dataframe(analysis_results["hourly"])

    with tab2:
        st.write("### Daily Traffic Patterns")
        st.dataframe(analysis_results["daily"])

    with tab3:
        st.write("### Road Type Analysis")
        st.dataframe(analysis_results["road_type"])
