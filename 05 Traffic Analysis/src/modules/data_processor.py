import numpy as np
import pandas as pd


class TrafficDataProcessor:
    """
    A class to process and analyze traffic data.

    This class provides methods for feature engineering,
    traffic pattern analysis, and statistical calculations.
    """

    def __init__(self, data):
        """
        Initialize the TrafficDataProcessor.

        Args:
            data (pandas.DataFrame): Traffic data to process
        """
        self.data = data
        self.analysis_results = {}

    def add_calculated_features(self):
        """
        Add calculated features to the traffic data.

        Returns:
            pandas.DataFrame: Data with added features
        """
        print("Adding calculated features...")

        # Calculate traffic index
        self.data["traffic_index"] = self._calculate_traffic_index()

        # Add time-based features
        self._add_time_features()

        # Calculate traffic efficiency
        self.data["efficiency"] = self._calculate_efficiency()

        return self.data

    def _calculate_traffic_index(self):
        """
        Calculate traffic index based on speed and vehicle count.

        Returns:
            pandas.Series: Traffic index values
        """
        normalized_speed = (100 - self.data["average_speed"]) / 100
        normalized_volume = self.data["vehicle_count"] / 100
        return (normalized_speed * normalized_volume) * 100

    def _add_time_features(self):
        """Add time-based features to the data."""
        self.data["hour"] = self.data["timestamp"].dt.hour
        self.data["day_of_week"] = self.data["timestamp"].dt.day_name()
        self.data["time_of_day"] = self.data["hour"].apply(self._categorize_time_of_day)

    def _categorize_time_of_day(self, hour):
        """
        Categorize hours into time of day segments.

        Args:
            hour (int): Hour of the day (0-23)

        Returns:
            str: Time of day category
        """
        if 6 <= hour < 10:
            return "Morning"
        elif 10 <= hour < 14:
            return "Noon"
        elif 14 <= hour < 18:
            return "Afternoon"
        elif 18 <= hour < 22:
            return "Evening"
        else:
            return "Midnight"

    def _calculate_efficiency(self):
        """
        Calculate traffic efficiency metric.

        Returns:
            pandas.Series: Efficiency values
        """
        return np.where(
            self.data["average_speed"] > 20,
            self.data["average_speed"] / np.maximum(self.data["vehicle_count"], 1),
            0,
        )

    def analyze_traffic_patterns(self):
        """
        Analyze traffic patterns from the data.

        Returns:
            dict: Dictionary containing analysis results
        """
        print("Analyzing traffic patterns...")

        analysis = {}

        # Hourly analysis
        analysis["hourly"] = self._analyze_hourly_patterns()

        # Daily analysis
        analysis["daily"] = self._analyze_daily_patterns()

        # Road type analysis
        analysis["road_type"] = self._analyze_road_type_patterns()

        # Weather impact analysis
        analysis["weather"] = self._analyze_weather_impact()

        self.analysis_results = analysis
        return analysis

    def _analyze_hourly_patterns(self):
        """
        Analyze hourly traffic patterns.

        Returns:
            pandas.DataFrame: Hourly statistics
        """
        return (
            self.data.groupby("hour")
            .agg(
                {
                    "vehicle_count": ["mean", "std"],
                    "average_speed": ["mean", "std"],
                    "traffic_index": "mean",
                }
            )
            .round(2)
        )

    def _analyze_daily_patterns(self):
        """
        Analyze daily traffic patterns.

        Returns:
            pandas.DataFrame: Daily statistics
        """
        weekday_order = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        daily_stats = self.data.groupby("day_of_week").agg(
            {"vehicle_count": "mean", "average_speed": "mean", "traffic_index": "mean"}
        )
        return daily_stats.reindex(weekday_order)

    def _analyze_road_type_patterns(self):
        """
        Analyze patterns by road type.

        Returns:
            pandas.DataFrame: Road type statistics
        """
        return (
            self.data.groupby("road_type")
            .agg(
                {
                    "vehicle_count": "mean",
                    "average_speed": "mean",
                    "traffic_index": "mean",
                    "efficiency": "mean",
                }
            )
            .round(2)
        )

    def _analyze_weather_impact(self):
        """
        Analyze weather impact on traffic.

        Returns:
            pandas.DataFrame: Weather impact statistics
        """
        return (
            self.data.groupby("weather")
            .agg(
                {
                    "vehicle_count": "mean",
                    "average_speed": "mean",
                    "traffic_index": "mean",
                }
            )
            .round(2)
        )

    def get_summary_statistics(self):
        """
        Get summary statistics for the data.

        Returns:
            dict: Summary statistics
        """
        return {
            "total_records": len(self.data),
            "avg_vehicle_count": self.data["vehicle_count"].mean(),
            "avg_speed": self.data["average_speed"].mean(),
            "avg_traffic_index": self.data["traffic_index"].mean(),
            "most_common_congestion": self.data["congestion_level"].mode()[0],
            "date_range": {
                "start": self.data["timestamp"].min(),
                "end": self.data["timestamp"].max(),
            },
        }
