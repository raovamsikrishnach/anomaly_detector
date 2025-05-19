import unittest
import pandas as pd
import numpy as np

from anomaly_detection import MetricCleaner, MADZScoreDetector


class TestMetricCleaner(unittest.TestCase):
    def test_filter_dimension_and_split(self):
        index = pd.date_range("2021-01-01", periods=3, freq="H")
        data = {
            "site.scope_aws_us-east1.cpustats{clustertag=c1,podtag=p1}": [1, 2, 3],
            "site.scope_aws_us-east1.memstats{clustertag=c1,podtag=p1}": [3, 4, 5],
            "site.scope_aws_us-east1.cpustats{clustertag=c2,podtag=p1}": [2, 3, 4],
        }
        df = pd.DataFrame(data, index=index)
        cleaner = MetricCleaner(dimension_name="cpu", dataframe=df)
        self.assertIn("c1_aws_us-east1", cleaner.cluster_frames)
        self.assertIn("c2_aws_us-east1", cleaner.cluster_frames)
        # memstats column should be dropped
        self.assertEqual(len(cleaner.df.columns), 2)


class TestMADZScoreDetector(unittest.TestCase):
    def test_zscore_computation(self):
        df = pd.DataFrame({
            "metric1": [1, 2, 3],
            "metric2": [4, 5, 6],
        })
        frames = {"cluster1_scope": df}
        detector = MADZScoreDetector(frames)
        detector.compute()
        self.assertIn("cluster1_scope", detector.zscores)
        result = detector.top_anomalies(n=1)
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]["score"], detector.zscores["cluster1_scope"].abs().max().max())


if __name__ == "__main__":
    unittest.main()
