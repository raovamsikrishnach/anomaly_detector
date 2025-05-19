"""MAD-based z-score detector for anomaly detection."""

from __future__ import annotations

from typing import Dict

import numpy as np
import pandas as pd
import plotly.express as px


class MADZScoreDetector:
    """Compute MAD-based z-scores for each cluster frame."""

    def __init__(self, cluster_frames: Dict[str, pd.DataFrame]):
        self.cluster_frames = cluster_frames
        self.zscores: Dict[str, pd.DataFrame] = {}

    @staticmethod
    def _mad(series: pd.Series) -> float:
        median = series.median()
        mad = np.median(np.abs(series - median))
        return mad

    @staticmethod
    def _zscore(series: pd.Series) -> pd.Series:
        median = series.median()
        mad = MADZScoreDetector._mad(series)
        if mad == 0:
            mad = 1e-9
        return 0.6745 * (series - median) / mad

    def compute(self) -> None:
        for key, df in self.cluster_frames.items():
            scores = df.apply(self._zscore)
            self.zscores[key] = scores

    def top_anomalies(self, n: int = 3) -> pd.DataFrame:
        records = []
        for key, df in self.zscores.items():
            for col in df.columns:
                max_score = df[col].abs().max()
                records.append({"cluster": key, "metric": col, "score": max_score})
        result = pd.DataFrame(records).sort_values(by="score", ascending=False)
        return result.head(n)

    def plot(self) -> None:
        if not self.zscores:
            raise ValueError("Z-scores have not been computed")
        combined = pd.concat(
            {
                cluster: df.stack()
                for cluster, df in self.zscores.items()
            },
            names=["cluster", "metric"]
        ).reset_index(name="zscore")
        fig = px.line(
            combined,
            x="index",
            y="zscore",
            color="cluster",
            title="MAD Z-Scores by Cluster",
        )
        fig.show()
