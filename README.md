This package implements a simple approach for detecting anomalies in time
series metrics using Median Absolute Deviation (MAD) based z-scores.

## Installation

Install the package in editable mode:

```bash
pip install -e .
```

## Usage

Two helper classes are provided:

- `MetricCleaner` cleans the raw metrics and splits them into per-cluster
  data frames.
- `MADZScoreDetector` calculates MAD-based z-scores and identifies anomalies.

Run the example script or execute the package directly to see the detector in
action:

```bash
python examples/simple_example.py
# or
python -m anomaly_detector
```

Both commands print the top anomalies and open an interactive Plotly graph.
