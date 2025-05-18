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

Run the example script to see the detector in action:

```bash
python examples/simple_example.py
```

This prints the top anomalies and opens an interactive Plotly graph.
