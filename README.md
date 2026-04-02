# Honeywell-Predictive-Maintenance
AI-powered dashboard for industrial asset health monitoring using the AI4I 2020 dataset.
# 🛡️ Honeywell Industrial Asset Health Monitor

## Project Overview
This project is a **Predictive Maintenance Dashboard** developed as a Capstone for the Honeywell AI course. It provides real-time monitoring and failure prediction for industrial machinery, helping to reduce unplanned downtime and maintenance costs.

## Key Features
* **Real-Time Health Scoring:** Calculates asset health based on thermal and mechanical stress.
* **Failure Prediction:** Uses threshold-based AI logic to estimate probability of failure.
* **Sensor Simulation:** Interactive sliders to test "what-if" scenarios for temperature and speed.
* **Historical Analysis:** Displays past maintenance records and failure logs from real-world data.

## The Dataset
This application utilizes the **AI4I 2020 Predictive Maintenance Dataset**, featuring 10,000 records of:
* Air & Process Temperature (converted from Kelvin to Celsius)
* Rotational Speed (RPM)
* Torque (Nm)
* Tool Wear (Minutes)

## Tech Stack
* **Language:** Python
* **Framework:** Streamlit (Web Dashboard)
* **Visualization:** Plotly Express (Interactive Charts)
* **Data Handling:** Pandas

## How to Run
1. Install requirements: `pip install streamlit pandas plotly`
2. Run the app: `streamlit run honeywell_app.py`
