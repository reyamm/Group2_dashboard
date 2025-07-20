# Group2
# Saudi Disasters Interactive Dashboard

This project provides an interactive web dashboard for exploring disaster events in Saudi Arabia.  
It allows users to analyze trends, impacts, and patterns of disasters over time, by type, location, and other dimensions.

The dashboard is built with Streamlit and can be run locally or deployed online.

---

## Project Overview

The dashboard enables users to:
- Filter disaster events by year, type, and city
- View key summary metrics such as total deaths, most common disaster, deadliest event
- Explore a variety of interactive visualizations:
  - Bar charts (including stacked and grouped)
  - Pie charts
  - Boxplots
  - Heatmaps
  - Animated scatter plots
  - Interactive maps
- Download filtered datasets as CSV for further analysis

This tool is intended for researchers, students, policymakers, and anyone interested in understanding the patterns of natural and man-made disasters in Saudi Arabia.

---

## Repository Contents

- `Group2_dashboard.py` — Streamlit application code
- `merged_output.csv` — Dataset used by the dashboard
- `requirements.txt` — List of Python dependencies
- `README.md` — This documentation file

---

## Installation and Usage

### Prerequisites

You need:
- Python 3.8 or later
- pip (Python package manager)

---

### Install Dependencies

Clone this repository and install the required packages.

```bash
git clone https://github.com/reyamm/Group2_dashboard.git
cd Group2_dashboard
pip install -r requirements.txt
