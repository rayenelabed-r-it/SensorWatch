"""Nettoie les mesures, détecte les anomalies et déclenche les alertes.

Méthode : pour chaque machine et chaque mesure, on compare la valeur à la
moyenne glissante des WINDOW dernières minutes (score z).
Une mesure est anormale si |z| > THRESHOLD.

Résultat : data/measures_flagged.csv
"""
from pathlib import Path

import pandas as pd

from alert import send_alerts

DATA = Path("data")
METRICS = ["temperature", "vibration", "humidity"]
WINDOW = 60       # nombre de mesures (minutes) pour la moyenne glissante
THRESHOLD = 6.0   # seuil du score z (3 donne trop de fausses alertes, voir README)


def load_and_clean(path):
    df = pd.read_csv(path, parse_dates=["timestamp"])
    df = df.drop_duplicates(subset=["timestamp", "machine"])
    df = df.sort_values(["machine", "timestamp"]).reset_index(drop=True)
    # Valeurs manquantes : on complète avec la valeur précédente de la machine
    df[METRICS] = df.groupby("machine")[METRICS].ffill()
    return df


def add_zscores(df):
    for metric in METRICS:
        grouped = df.groupby("machine")[metric]
        # shift(1) : on compare à l'historique, sans inclure la mesure courante
        mean = grouped.transform(lambda s: s.shift(1).rolling(WINDOW).mean())
        std = grouped.transform(lambda s: s.shift(1).rolling(WINDOW).std())
        df[f"z_{metric}"] = (df[metric] - mean) / std
    return df


def flag_anomalies(df):
    z_cols = [f"z_{m}" for m in METRICS]
    df["anomaly"] = (df[z_cols].abs() > THRESHOLD).any(axis=1)
    return df


def main():
    df = load_and_clean(DATA / "measures.csv")
    df = flag_anomalies(add_zscores(df))
    df.to_csv(DATA / "measures_flagged.csv", index=False)

    print(f"{len(df)} mesures analysées, {int(df['anomaly'].sum())} marquées anormales")
    print(df.groupby("machine")["anomaly"].sum().to_string())
    send_alerts(df[df["anomaly"]])


if __name__ == "__main__":
    main()
