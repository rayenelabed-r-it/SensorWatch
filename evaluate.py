"""Compare les alertes détectées aux vraies pannes injectées (data/faults_truth.csv).

À lancer après detect_anomalies.py. Permet de tester d'autres valeurs de
THRESHOLD ou de WINDOW et de voir leur effet.
"""
import pandas as pd

from alert import group_events

TOLERANCE_MIN = 12  # une alerte compte si elle tombe dans les 12 min après le début d'une panne


def main():
    flagged = pd.read_csv("data/measures_flagged.csv", parse_dates=["timestamp"])
    truth = pd.read_csv("data/faults_truth.csv", parse_dates=["timestamp"])
    events = group_events(flagged[flagged["anomaly"]])

    def matches(event, fault):
        delta = (event["timestamp"] - fault["timestamp"]).total_seconds() / 60
        return event["machine"] == fault["machine"] and 0 <= delta <= TOLERANCE_MIN

    caught = sum(any(matches(e, f) for e in events) for _, f in truth.iterrows())
    useful = sum(any(matches(e, f) for _, f in truth.iterrows()) for e in events)

    print(f"Pannes réelles           : {len(truth)}")
    print(f"Alertes envoyées         : {len(events)}")
    print(f"Pannes détectées         : {caught}/{len(truth)}  (rappel = {caught / len(truth):.0%})")
    print(f"Alertes justifiées       : {useful}/{len(events)}  (précision = {useful / max(len(events), 1):.0%})")


if __name__ == "__main__":
    main()
