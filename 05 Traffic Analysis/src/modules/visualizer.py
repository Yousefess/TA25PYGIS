import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


class TrafficVisualizer:
    """
    A class for creating traffic data visualizations.

    This class provides methods to create various charts and plots
    for traffic analysis and pattern visualization.
    """

    def __init__(self, data, analysis_results):
        """
        Initialize the TrafficVisualizer.

        Args:
            data (pandas.DataFrame): Traffic data
            analysis_results (dict): Analysis results from TrafficDataProcessor
        """
        self.data = data
        self.analysis_results = analysis_results
        self._setup_plot_style()

    def _setup_plot_style(self):
        """Set up consistent plot styling."""
        plt.rcParams["font.family"] = "DejaVu Sans"
        plt.rcParams["axes.unicode_minus"] = False
        sns.set_style("whitegrid")

    def create_main_dashboard(self):
        """
        Create the main dashboard with multiple subplots.

        Returns:
            matplotlib.figure.Figure: Main dashboard figure
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(
            "Comprehensive Urban Traffic Pattern Analysis",
            fontsize=16,
            fontweight="bold",
        )

        self._plot_hourly_traffic(axes[0, 0])
        self._plot_daily_patterns(axes[0, 1])
        self._plot_traffic_heatmap(axes[1, 0])
        self._plot_congestion_distribution(axes[1, 1])

        plt.tight_layout()
        return fig

    def _plot_hourly_traffic(self, ax):
        """
        Plot hourly traffic patterns.

        Args:
            ax (matplotlib.axes.Axes): Axes to plot on
        """
        hourly_data = self.analysis_results["hourly"]
        hours = hourly_data.index

        ax.plot(
            hours,
            hourly_data[("vehicle_count", "mean")],
            marker="o",
            linewidth=2,
            markersize=4,
            label="Vehicle Count",
            color="blue",
        )
        ax.set_title("Average Vehicle Count by Hour")
        ax.set_xlabel("Hour of Day")
        ax.set_ylabel("Vehicle Count")
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.set_xticks(range(0, 24, 2))

    def _plot_daily_patterns(self, ax):
        """
        Plot daily traffic patterns.

        Args:
            ax (matplotlib.axes.Axes): Axes to plot on
        """
        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        daily_data = self.analysis_results["daily"]

        x_pos = np.arange(len(days))
        bars = ax.bar(
            x_pos,
            daily_data["average_speed"],
            color=plt.cm.Set3(np.linspace(0, 1, len(days))),
        )

        ax.set_title("Average Speed by Day of Week")
        ax.set_xlabel("Day of Week")
        ax.set_ylabel("Average Speed (km/h)")
        ax.set_xticks(x_pos)
        ax.set_xticklabels(days, rotation=45)

        # Add value labels on bars
        for bar, value in zip(bars, daily_data["average_speed"]):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.5,
                f"{value:.1f}",
                ha="center",
                va="bottom",
                fontweight="bold",
            )

    def _plot_traffic_heatmap(self, ax):
        """
        Create a heatmap of traffic distribution.

        Args:
            ax (matplotlib.axes.Axes): Axes to plot on
        """
        scatter = ax.scatter(
            self.data["longitude"],
            self.data["latitude"],
            c=self.data["traffic_index"],
            cmap="Reds",
            s=30,
            alpha=0.6,
            edgecolors="black",
            linewidth=0.5,
        )

        ax.set_title("Traffic Heatmap - Urban Area")
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        plt.colorbar(scatter, ax=ax, label="Traffic Index")

    def _plot_congestion_distribution(self, ax):
        """
        Plot congestion level distribution.

        Args:
            ax (matplotlib.axes.Axes): Axes to plot on
        """
        congestion_counts = self.data["congestion_level"].value_counts()
        colors = ["lightgreen", "gold", "orange", "red"]

        wedges, texts, autotexts = ax.pie(
            congestion_counts.values,
            labels=congestion_counts.index,
            autopct="%1.1f%%",
            startangle=90,
            colors=colors,
            shadow=True,
        )

        # Enhance text appearance
        for autotext in autotexts:
            autotext.set_color("white")
            autotext.set_fontweight("bold")

        ax.set_title("Traffic Congestion Distribution")

    def create_supplementary_charts(self):
        """
        Create supplementary analysis charts.

        Returns:
            matplotlib.figure.Figure: Supplementary charts figure
        """
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))

        self._plot_speed_by_road_type(axes[0])
        self._plot_density_vs_speed(axes[1])

        plt.tight_layout()
        return fig

    def _plot_speed_by_road_type(self, ax):
        """
        Plot speed distribution by road type.

        Args:
            ax (matplotlib.axes.Axes): Axes to plot on
        """
        road_types = self.data["road_type"].unique()
        speed_data = [
            self.data[self.data["road_type"] == road]["average_speed"]
            for road in road_types
        ]

        box_plot = ax.boxplot(speed_data, labels=road_types, patch_artist=True)

        # Color the boxes
        colors = ["lightblue", "lightgreen", "lightcoral", "lightsalmon"]
        for patch, color in zip(box_plot["boxes"], colors):
            patch.set_facecolor(color)

        ax.set_title("Speed Distribution by Road Type")
        ax.set_ylabel("Speed (km/h)")
        ax.tick_params(axis="x", rotation=45)
        ax.grid(True, alpha=0.3)

    def _plot_density_vs_speed(self, ax):
        """
        Plot vehicle density vs speed relationship.

        Args:
            ax (matplotlib.axes.Axes): Axes to plot on
        """
        scatter = ax.scatter(
            self.data["vehicle_count"],
            self.data["average_speed"],
            c=self.data["traffic_index"],
            cmap="viridis",
            alpha=0.6,
            s=30,
        )

        ax.set_title("Vehicle Density vs Average Speed")
        ax.set_xlabel("Vehicle Count")
        ax.set_ylabel("Average Speed (km/h)")
        plt.colorbar(scatter, ax=ax, label="Traffic Index")

        # Add trend line
        z = np.polyfit(self.data["vehicle_count"], self.data["average_speed"], 1)
        p = np.poly1d(z)
        ax.plot(
            self.data["vehicle_count"],
            p(self.data["vehicle_count"]),
            "r--",
            alpha=0.8,
            linewidth=2,
            label="Trend Line",
        )
        ax.legend()
