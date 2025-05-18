# anomaly_detector

This repository provides a simple approach for detecting anomalies in time
series metrics using a combination of Median Absolute Deviation (MAD) and
z-scores. The module `anomaly_detection.py` contains two helper classes:

- `MetricCleaner` cleans the raw metrics and splits them into per-cluster
  data frames.
- `MADZScoreDetector` calculates MAD-based z-scores for each cluster and
  identifies anomalies.

The `example_usage` function generates synthetic data to demonstrate how the
classes are used and produces a Plotly plot of z-scores.

Run the example with:

```bash
python anomaly_detection.py
```

This will print the top anomalies and open an interactive Plotly graph.
