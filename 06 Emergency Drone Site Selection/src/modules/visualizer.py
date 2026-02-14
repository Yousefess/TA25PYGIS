"""
Visualization module for drone site selection analysis.
"""

import geopandas as gpd
import matplotlib.pyplot as plt
from config.settings import COLOR_SCHEME


class SiteSelectionVisualizer:
    """
    A class for creating visualizations for drone site selection analysis.
    """

    def __init__(self, urban_data):
        """
        Initialize the visualizer.

        Args:
            urban_data (dict): Urban data from OSMDataLoader
        """
        self.data = urban_data
        self._setup_plot_style()

    def _setup_plot_style(self):
        """Set up consistent plot styling."""
        plt.rcParams["font.size"] = 10
        plt.rcParams["figure.figsize"] = (12, 8)

    def create_analysis_dashboard(self, analysis_results, mcda_results, save_path=None):
        """
        Create comprehensive analysis dashboard.

        Args:
            analysis_results: Results from CriteriaAnalyzer
            mcda_results: Results from MCDAEngine
            save_path: Path to save the figure
        """
        fig, axes = plt.subplots(2, 2, figsize=(20, 16))
        fig.suptitle(
            "Drone Site Selection Analysis Dashboard", fontsize=16, fontweight="bold"
        )

        # Plot 1: Initial Data Overview
        self._plot_initial_data(axes[0, 0])

        # Plot 2: Demand and Exclusion Zones
        self._plot_zones_analysis(axes[0, 1], analysis_results)

        # Plot 3: Candidate Site Evaluation
        self._plot_candidate_evaluation(axes[1, 0], analysis_results)

        # Plot 4: Final Recommendations
        self._plot_final_recommendations(axes[1, 1], mcda_results)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"✅ Dashboard saved to {save_path}")

        return fig

    def _plot_initial_data(self, ax):
        """Plot initial OSM data overview."""
        # Plot roads
        if not self.data["roads"].empty:
            self.data["roads"].plot(
                ax=ax,
                color=COLOR_SCHEME["roads"],
                linewidth=0.5,
                alpha=0.6,
                label="Major Roads",
            )

        # Plot candidate sites
        if not self.data["candidate_sites"].empty:
            self.data["candidate_sites"].plot(
                ax=ax,
                color=COLOR_SCHEME["candidate_sites"],
                alpha=0.4,
                edgecolor="darkgreen",
                label="Candidate Sites",
            )

        # Plot critical infrastructure
        if not self.data["critical_infrastructure"].empty:
            self.data["critical_infrastructure"].plot(
                ax=ax,
                color=COLOR_SCHEME["critical_infrastructure"],
                markersize=50,
                marker="^",
                label="Critical Infrastructure",
            )

        ax.set_title("Initial Data: Critical Infrastructure & Candidate Sites")
        ax.axis("off")
        ax.legend(loc="upper left")

    def _plot_zones_analysis(self, ax, analysis_results):
        """Plot demand and exclusion zones analysis."""
        # Plot base data
        if not self.data["roads"].empty:
            self.data["roads"].plot(
                ax=ax, color=COLOR_SCHEME["roads"], linewidth=0.5, alpha=0.3
            )

        # Plot demand zones
        if "demand_zones" in analysis_results:
            demand_results = analysis_results["demand_zones"]
            if not demand_results["unified_demand_zone"].empty:
                demand_results["unified_demand_zone"].plot(
                    ax=ax,
                    color=COLOR_SCHEME["demand_zones"],
                    alpha=0.3,
                    edgecolor="blue",
                    label="Demand Zone",
                )

        # Plot exclusion zones
        if "exclusion_zones" in analysis_results:
            exclusion_results = analysis_results["exclusion_zones"]
            if not exclusion_results["unified_exclusion_zone"].empty:
                exclusion_results["unified_exclusion_zone"].plot(
                    ax=ax,
                    color=COLOR_SCHEME["exclusion_zones"],
                    alpha=0.3,
                    edgecolor="orange",
                    label="Exclusion Zone",
                )

        # Plot critical infrastructure
        if not self.data["critical_infrastructure"].empty:
            self.data["critical_infrastructure"].plot(
                ax=ax,
                color=COLOR_SCHEME["critical_infrastructure"],
                markersize=30,
                marker="^",
                label="Critical Infrastructure",
            )

        ax.set_title("Demand & Exclusion Zones Analysis")
        ax.axis("off")
        ax.legend(loc="upper left")

    def _plot_candidate_evaluation(self, ax, analysis_results):
        """Plot candidate site evaluation results."""
        # Plot base data
        if not self.data["roads"].empty:
            self.data["roads"].plot(
                ax=ax, color=COLOR_SCHEME["roads"], linewidth=0.5, alpha=0.2
            )

        # Plot all candidate sites (light)
        if not self.data["candidate_sites"].empty:
            self.data["candidate_sites"].plot(
                ax=ax,
                color="lightgray",
                alpha=0.3,
                edgecolor="gray",
                label="All Candidates",
            )

        # Plot feasible sites
        if "candidate_evaluation" in analysis_results:
            candidate_results = analysis_results["candidate_evaluation"]
            if not candidate_results["evaluated_sites"].empty:
                candidate_results["evaluated_sites"].plot(
                    ax=ax,
                    color=COLOR_SCHEME["candidate_sites"],
                    alpha=0.7,
                    edgecolor="darkgreen",
                    label="Feasible Sites",
                )

        ax.set_title("Candidate Site Evaluation")
        ax.axis("off")
        ax.legend(loc="upper left")

    def _plot_final_recommendations(self, ax, mcda_results):
        """Plot final recommended sites."""
        # Plot base data
        if not self.data["roads"].empty:
            self.data["roads"].plot(
                ax=ax, color=COLOR_SCHEME["roads"], linewidth=0.5, alpha=0.2
            )

        # Plot critical infrastructure
        if not self.data["critical_infrastructure"].empty:
            self.data["critical_infrastructure"].plot(
                ax=ax,
                color=COLOR_SCHEME["critical_infrastructure"],
                markersize=30,
                marker="^",
                label="Critical Infrastructure",
            )

        # Plot recommended sites
        if mcda_results and "top_sites" in mcda_results:
            top_sites = mcda_results["top_sites"]
            if not top_sites.empty:
                # Color by rank
                for rank, site in top_sites.iterrows():
                    color = "gold" if site["rank"] == 1 else "purple"
                    alpha = 0.9 if site["rank"] == 1 else 0.7

                    gpd.GeoDataFrame([site], crs=top_sites.crs).plot(
                        ax=ax,
                        color=color,
                        alpha=alpha,
                        edgecolor="black",
                        label=f"Rank {site['rank']}: {site.get('name', 'Site')}",
                    )

        ax.set_title("Final Recommended Sites (Ranked)")
        ax.axis("off")
        ax.legend(loc="upper left")

    def create_score_distribution_chart(self, ranked_sites, save_path=None):
        """
        Create score distribution chart for ranked sites.

        Args:
            ranked_sites: DataFrame with ranked sites
            save_path: Path to save the figure
        """
        if ranked_sites.empty:
            return None

        fig, ax = plt.subplots(figsize=(10, 6))

        # Create bar chart of composite scores
        sites_sorted = ranked_sites.sort_values("composite_score", ascending=True)
        y_pos = range(len(sites_sorted))

        bars = ax.barh(
            y_pos,
            sites_sorted["composite_score"],
            color=[
                "gold" if rank == 1 else "lightblue" for rank in sites_sorted["rank"]
            ],
            alpha=0.7,
        )

        # Add value labels
        for i, (bar, score) in enumerate(zip(bars, sites_sorted["composite_score"])):
            ax.text(
                bar.get_width() + 1,
                bar.get_y() + bar.get_height() / 2,
                f"{score:.1f}",
                va="center",
                ha="left",
                fontweight="bold",
            )

        ax.set_yticks(y_pos)
        ax.set_yticklabels([f"Rank {rank}" for rank in sites_sorted["rank"]])
        ax.set_xlabel("Composite Score (0-100)")
        ax.set_title("Drone Site Rankings - Composite Scores")
        ax.grid(True, alpha=0.3, axis="x")

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")

        return fig
