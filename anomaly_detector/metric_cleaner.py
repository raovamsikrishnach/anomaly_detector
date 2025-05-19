"""Utilities for cleaning and splitting raw metrics into per-cluster frames."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, Optional

import pandas as pd


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
        tags_dict: Dict[str, str] = {}
        for tag in tags.split(','):
            if '=' in tag:
                k, v = tag.split('=', 1)
                tags_dict[k.strip()] = v.strip()
        cluster = tags_dict.get(self.separator_tag)
        if not cluster:
            cluster = tags_dict.get(f"{self.separator_tag}") or tags_dict.get(
                f"{self.separator_tag}tag"
            )
        if cluster is None:
            return None
        return {"scope": scope, "cluster": cluster}
