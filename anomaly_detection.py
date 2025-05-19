import re
from dataclasses import dataclass
from typing import Dict, Optional

import numpy as np
import pandas as pd
import plotly.express as px


@dataclass
class MetricCleaner:
    """Clean and split raw metrics into per-cluster data frames."""

    dimension_name: str
    dataframe: pd.DataFrame
    drop_incomplete: bool = False
    separator_tag: str = "clustertag"

    def __post_init__(self) -> None:
        self.df = self.dataframe.copy()
        self._clean_dimension()
        self.cluster_frames = self._split_by_cluster()

    def _clean_dimension(self) -> None:
        pattern = re.compile(self.dimension_name, re.IGNORECASE)
        columns_to_keep = [c for c in self.df.columns if pattern.search(c)]
        self.df = self.df[columns_to_keep]

    def _split_by_cluster(self) -> Dict[str, pd.DataFrame]:
        cluster_frames: Dict[str, pd.DataFrame] = {}
        for col in self.df.columns:
            info = self._parse_column(col)
            if info is None:
                continue
            cluster_key = f"{info['cluster']}_{info['scope']}"
            cluster_frames.setdefault(cluster_key, pd.DataFrame())
            cluster_frames[cluster_key][col] = self.df[col]
        if self.drop_incomplete:
            cluster_frames = {
                k: df.dropna(axis=1, how="any") for k, df in cluster_frames.items()
            }
        return cluster_frames

    def _parse_column(self, column: str) -> Optional[Dict[str, str]]:
        pattern = (
            r"\.scope_(?P<scope>[^.]+)\.(?P<metric>[^{]+){(?P<tags>[^}]+)}"
        )
        m = re.search(pattern, column)
        if not m:
            return None
        scope = m.group("scope")
        tags = m.group("tags")
        tags_dict = {}
        for tag in tags.split(','):
            if '=' in tag:
                k, v = tag.split('=', 1)
                tags_dict[k.strip()] = v.strip()
        cluster = tags_dict.get(self.separator_tag)
        if not cluster:
            # try clustertag with or without suffix
            cluster = tags_dict.get(f"{self.separator_tag}") or tags_dict.get(
                f"{self.separator_tag}tag"
            )
        if cluster is None:
            return None
        return {"scope": scope, "cluster": cluster}


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


def example_usage() -> None:
    time_index = pd.date_range("2021-01-01", periods=100, freq="H")
    data = {
        f"site.scope_aws_us-east1.cpustats{{clustertag=cluster1,podtag=pod{i}}}": np.random.rand(100)
        for i in range(1, 4)
    }
    data.update(
        {
            f"site.scope_aws_us-west2.cpustats{{clustertag=cluster2,podtag=pod{i}}}": np.random.rand(100)
            for i in range(1, 4)
        }
    )
    df = pd.DataFrame(data, index=time_index)
    cleaner = MetricCleaner(dimension_name="cpu", dataframe=df)
    detector = MADZScoreDetector(cleaner.cluster_frames)
    detector.compute()
    print(detector.top_anomalies())
    detector.plot()


if __name__ == "__main__":
    example_usage()
