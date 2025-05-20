"""Command line interface for the anomaly_detector package."""

import numpy as np
import pandas as pd

from . import MetricCleaner, MADZScoreDetector


def example_usage() -> None:
    """Run a simple demonstration using randomly generated data."""
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


def main() -> None:
    example_usage()


if __name__ == "__main__":
    main()
