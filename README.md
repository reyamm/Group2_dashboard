# Saudi Disasters Dashboard

An interactive Streamlit dashboard for exploring, analyzing, and predicting disaster data in Saudi Arabia.

##  Live Demo
[Open the Dashboard](https://group2dashboard-7vn7itznrh6mpodsrx9kxj.streamlit.app)

---

## Features

- **Filters**:
  - Year range
  - Disaster type
  - City
- **Key Metrics**:
  - Total deaths
  - Average deaths per event
  - Most common disaster type
  - Deadliest event
  - Most frequent city
  - Most frequent subgroup
  - Earliest and latest disaster years
- **Exploratory Visualizations**:
  - Deaths and disasters over time
  - Cumulative deaths
  - Disaster type and subtype distributions
  - Top 10 cities with most disasters
  - Deaths by disaster type
  - Damage distribution
  - Magnitude vs deaths
  - Geospatial disaster map
  - Animated trends over years
  - Severity heatmap (cities × disaster types)
- **Predictions**:
  - Deadly events (Yes/No) pie chart
  - Severity levels by disaster type bar chart
  - Severity heatmap of top cities and disaster types
- **Downloadable filtered data**

---

##  Datasets

| File Name                                | Description                                |
|-----------------------------------------|--------------------------------------------|
| `merged_output.csv`                     | Main disaster events dataset              |
| `disaster_predictions_with_severity.csv` | Predicted severity levels (Low, Medium, High) |
| `disaster_predictions_logreg.csv`       | Predicted deadly outcomes (Yes/No)       |

These files must be placed in the same directory as the `Group2_dashboard.py` file.

---

##  Getting Started

### Clone the repository

```bash
git clone https://github.com/<your-username>/Group2_dashboard.git
cd Group2_dashboard
