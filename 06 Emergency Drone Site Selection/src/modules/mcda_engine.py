"""
Multi-Criteria Decision Analysis engine for site ranking.
FIXED: JSON serialization issue with geometry columns.
"""

import numpy as np
import pandas as pd
from config.settings import CRITERIA_WEIGHTS
from sklearn.preprocessing import MinMaxScaler


class MCDAEngine:
    """
    A class to perform Multi-Criteria Decision Analysis for site ranking.
    """

    def __init__(self, criteria_weights=None):
        """
        Initialize the MCDA engine.

        Args:
            criteria_weights (dict): Weights for each criterion
        """
        self.weights = criteria_weights or CRITERIA_WEIGHTS
        self.scaler = MinMaxScaler()

    def calculate_site_scores(self, evaluated_sites):
        """
        Calculate composite scores for evaluated sites.

        Args:
            evaluated_sites (geopandas.GeoDataFrame): Sites from CriteriaAnalyzer

        Returns:
            pandas.DataFrame: Sites with calculated scores and rankings
        """
        print("🏆 Calculating MCDA scores...")

        if evaluated_sites.empty:
            return pd.DataFrame()

        try:
            # Create a copy for calculations
            sites_df = evaluated_sites.copy()

            # FIX: Remove any geometry columns except the main 'geometry' column
            geometry_cols = [
                col
                for col in sites_df.columns
                if col != "geometry" and sites_df[col].dtype == "geometry"
            ]

            for col in geometry_cols:
                sites_df = sites_df.drop(columns=[col])

            # Calculate individual criterion scores
            sites_df["area_score"] = self._normalize_criterion(
                sites_df["safe_area_sq_m"], True
            )
            sites_df["coverage_score"] = self._normalize_criterion(
                sites_df["coverage_percentage"], True
            )
            sites_df["proximity_score"] = self._normalize_criterion(
                sites_df["distance_to_critical_m"], False
            )

            # Calculate composite score using weighted sum
            sites_df["composite_score"] = (
                self.weights["site_area"] * sites_df["area_score"]
                + self.weights["service_coverage"] * sites_df["coverage_score"]
                + self.weights["accessibility"] * sites_df["proximity_score"]
            )

            # Add safety bonus (all sites already passed safety criteria)
            sites_df["composite_score"] += self.weights["safety_distance"]

            # Normalize composite score to 0-100 scale
            sites_df["composite_score"] = self._normalize_to_100(
                sites_df["composite_score"]
            )

            # Rank sites by composite score
            sites_df["rank"] = (
                sites_df["composite_score"]
                .rank(ascending=False, method="dense")
                .astype(int)
            )

            # Calculate category (A, B, C based on score)
            sites_df["category"] = sites_df["composite_score"].apply(
                self._categorize_site
            )

            print(f"✅ Calculated scores for {len(sites_df)} sites")
            return sites_df

        except Exception as e:
            print(f"❌ Error calculating MCDA scores: {e}")
            return pd.DataFrame()

    def _normalize_criterion(self, values, benefit_criterion=True):
        """
        Normalize criterion values to 0-1 scale.

        Args:
            values: Array of criterion values
            benefit_criterion: Whether higher values are better

        Returns:
            numpy.array: Normalized values
        """
        if len(values) == 0:
            return np.array([])

        if benefit_criterion:
            # For benefit criteria (higher is better)
            min_val = values.min()
            max_val = values.max()
            if max_val == min_val:
                return np.ones_like(values)
            return (values - min_val) / (max_val - min_val)
        else:
            # For cost criteria (lower is better)
            min_val = values.min()
            max_val = values.max()
            if max_val == min_val:
                return np.ones_like(values)
            return (max_val - values) / (max_val - min_val)

    def _normalize_to_100(self, values):
        """Normalize values to 0-100 scale."""
        if len(values) == 0:
            return np.array([])

        min_val = values.min()
        max_val = values.max()
        if max_val == min_val:
            return np.full_like(values, 50)  # Middle value if all same

        return ((values - min_val) / (max_val - min_val)) * 100

    def _categorize_site(self, score):
        """Categorize site based on composite score."""
        if score >= 80:
            return "A - Excellent"
        elif score >= 60:
            return "B - Good"
        elif score >= 40:
            return "C - Fair"
        else:
            return "D - Poor"

    def generate_recommendations(self, ranked_sites, top_n=5):
        """
        Generate recommendations based on ranked sites.
        FIXED: Remove any non-serializable geometry columns before returning.

        Args:
            ranked_sites: DataFrame with ranked sites
            top_n: Number of top recommendations to generate

        Returns:
            dict: Recommendation results
        """
        if ranked_sites.empty:
            return {}

        try:
            # Get top N sites
            top_sites = ranked_sites.nlargest(top_n, "composite_score")

            # FIX: Ensure we only have one geometry column and remove any other geometry objects
            # Create a clean copy for download
            top_sites_clean = top_sites.copy()

            # Remove any columns that might contain geometry objects (except the main 'geometry' column)
            for col in top_sites_clean.columns:
                if col != "geometry":
                    # Check if column contains geometry objects
                    try:
                        # Try to check if this column contains geometry-like objects
                        sample = (
                            top_sites_clean[col].dropna().iloc[0]
                            if not top_sites_clean[col].dropna().empty
                            else None
                        )
                        if hasattr(sample, "geom_type") or hasattr(sample, "wkt"):
                            # This is a geometry column - remove it
                            top_sites_clean = top_sites_clean.drop(columns=[col])
                    except:
                        pass

            recommendations = {
                "top_sites": top_sites_clean,
                "summary_stats": {
                    "total_sites_analyzed": len(ranked_sites),
                    "sites_recommended": len(top_sites),
                    "avg_composite_score": ranked_sites["composite_score"].mean(),
                    "best_score": ranked_sites["composite_score"].max(),
                    "category_breakdown": ranked_sites["category"]
                    .value_counts()
                    .to_dict(),
                },
                "site_details": [],
            }

            # Generate detailed recommendations (for display only)
            for idx, site in top_sites.iterrows():
                site_detail = {
                    "rank": site["rank"],
                    "name": site.get("name", f"Site_{idx}"),
                    "composite_score": round(site["composite_score"], 2),
                    "category": site["category"],
                    "safe_area_sq_m": round(site["safe_area_sq_m"], 2),
                    "coverage_percentage": round(site["coverage_percentage"], 2),
                    "distance_to_critical_m": round(site["distance_to_critical_m"], 2),
                }
                recommendations["site_details"].append(site_detail)

            print(f"✅ Generated {len(top_sites)} recommendations")
            return recommendations

        except Exception as e:
            print(f"❌ Error generating recommendations: {e}")
            return {}
