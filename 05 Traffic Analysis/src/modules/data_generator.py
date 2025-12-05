from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from faker import Faker


class TrafficDataGenerator:
    """
    A class to generate synthetic traffic data for urban traffic analysis.

    This class uses Faker to create realistic traffic data including
    location information, vehicle counts, speeds, and congestion levels.
    """

    def __init__(self, locale="en_US"):
        """
        Initialize the TrafficDataGenerator.

        Args:
            locale (str): Locale for Faker data generation
        """
        self.fake = Faker(locale)
        np.random.seed(42)

    def generate_traffic_data(self, n_records=1000):
        """
        Generate synthetic traffic data records.

        Args:
            n_records (int): Number of records to generate

        Returns:
            pandas.DataFrame: DataFrame containing traffic data
        """
        print(f"Generating {n_records} traffic data records...")

        data = []
        base_date = datetime(2024, 1, 1)

        for i in range(n_records):
            record = self._generate_single_record(i, base_date)
            data.append(record)

        df = pd.DataFrame(data)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df

    def _generate_single_record(self, record_id, base_date):
        """
        Generate a single traffic data record.

        Args:
            record_id (int): Unique identifier for the record
            base_date (datetime): Base date for timestamp generation

        Returns:
            dict: Single traffic data record
        """
        congestion_level = np.random.choice(
            ["Light", "Medium", "Heavy", "Very Heavy"], p=[0.3, 0.4, 0.2, 0.1]
        )

        # Generate speed based on congestion level
        if congestion_level == "Light":
            speed = np.random.normal(60, 10)
        elif congestion_level == "Medium":
            speed = np.random.normal(40, 8)
        elif congestion_level == "Heavy":
            speed = np.random.normal(20, 5)
        else:  # Very Heavy
            speed = np.random.normal(10, 3)

        record = {
            "id": record_id + 1,
            "timestamp": base_date + timedelta(hours=record_id),
            "location_name": self.fake.street_name(),
            "latitude": np.random.uniform(35.6, 35.8),  # Tehran area
            "longitude": np.random.uniform(51.2, 51.5),
            "vehicle_count": np.random.poisson(50),
            "average_speed": max(5, speed),  # Speed cannot be negative
            "congestion_level": congestion_level,
            "road_type": np.random.choice(
                ["Arterial", "Secondary", "Primary", "Expressway"],
                p=[0.4, 0.3, 0.2, 0.1],
            ),
            "weather": np.random.choice(
                ["Sunny", "Cloudy", "Rainy", "Snowy"], p=[0.6, 0.2, 0.15, 0.05]
            ),
        }

        return record
