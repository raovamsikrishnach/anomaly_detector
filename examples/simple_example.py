"""Example demonstrating the anomaly detector package."""

import pandas as pd
import numpy as np

from anomaly_detector import MetricCleaner, MADZScoreDetector


def main() -> None:
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
    main()
