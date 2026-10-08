# SensorWatch

Simulated industrial sensor monitoring: anomaly detection, alerts and dashboard.

> Personal project, work in progress, inspired by data acquisition and industrial IoT systems.

## Description

SensorWatch simulates sensor readings (temperature, vibration, humidity) from several machines. The program spots abnormal values before a failure happens, triggers an alert and shows the state of the machines on a dashboard.

No hardware is needed: the sensors are simulated with Python.

## Features

- Simulated sensor data generation (noise, spikes and drifts to mimic failures)
- Data cleaning and analysis with Pandas
- Anomaly detection (rolling mean and z-score)
- Automatic alerts (console, email optional)
- Interactive dashboard with Streamlit

## Project structure

```
sensorwatch/
├── data/                  # generated CSV files
├── generate_data.py       # sensor simulation
├── detect_anomalies.py    # cleaning and anomaly detection
├── alert.py               # alert sending
├── dashboard.py           # Streamlit dashboard
├── requirements.txt
└── README.md
```

## Installation

```bash
git clone https://github.com/rayenelabed-r-it/sensorwatch.git
cd sensorwatch
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

```bash
python generate_data.py          # creates data/measures.csv
python detect_anomalies.py       # flags anomalies and sends alerts
streamlit run dashboard.py       # opens the dashboard
```

## Data format

`data/measures.csv` contains one reading per minute and per machine.

| Column        | Description                          |
|---------------|--------------------------------------|
| `timestamp`   | date and time of the reading         |
| `machine`     | machine identifier                   |
| `temperature` | temperature (°C)                     |
| `vibration`   | vibration level                      |
| `humidity`    | humidity (%)                         |
| `anomaly`     | `True` if the reading is abnormal (added by `detect_anomalies.py`) |

## Method

1. One reading is generated every minute for each machine, with some random noise.
2. Failures (spikes or drifts) are injected at random times.
3. For each reading, the z-score is computed against the rolling mean of the latest readings:

   `z = (value - rolling_mean) / rolling_std`

4. A reading is flagged as abnormal if `|z| > 3`.
5. Each anomaly triggers an alert and appears on the dashboard.

## Results

_To complete: add 2 or 3 screenshots (curves with highlighted anomalies, dashboard)._

## Possible improvements

- Replace the z-score with an Isolation Forest model (Scikit-learn)
- Send readings as JSON messages, like a LoRaWAN sensor would
- Store the history in a SQLite database and query it with SQL

## Technologies

Python · NumPy · Pandas · Matplotlib · Streamlit · Git/GitHub

## Author

Rayene Labed, [LinkedIn](https://linkedin.com/in/rayenelabed)
