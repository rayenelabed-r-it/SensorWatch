"""Génère des mesures de capteurs simulées (température, vibrations, humidité).

Une mesure par minute et par machine, avec du bruit et quelques pannes
(pics et dérives) ajoutées à des moments aléatoires.

Résultat : data/measures.csv (+ data/faults_truth.csv avec les vraies pannes).
"""
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
MACHINES = ["machine_A", "machine_B", "machine_C"]
DAYS = 3
START = "2026-10-01 00:00"
FAULTS_PER_MACHINE = 6

OUT_DIR = Path("data")


def simulate_machine(rng, index):
    """Retourne les mesures normales d'une machine (sans panne)."""
    n = len(index)
    minutes = np.arange(n)
    # Cycle jour/nuit sur 24 h (1440 minutes) + bruit
    daily = np.sin(2 * np.pi * minutes / 1440)
    temperature = 60 + 3 * daily + rng.normal(0, 0.5, n)
    vibration = 2.0 + 0.1 * daily + rng.normal(0, 0.08, n)
    humidity = 45 - 5 * daily + rng.normal(0, 1.0, n)
    return pd.DataFrame(
        {"temperature": temperature, "vibration": vibration, "humidity": humidity},
        index=index,
    )


def inject_faults(rng, df, machine):
    """Ajoute des pannes dans le DataFrame et retourne la liste des pannes."""
    faults = []
    n = len(df)
    # On évite le début (la détection a besoin d'un historique)
    starts = rng.choice(np.arange(200, n - 50), size=FAULTS_PER_MACHINE, replace=False)
    for start in sorted(starts):
        kind = rng.choice(["pic_temperature", "pic_vibration", "derive_temperature"])
        if kind == "pic_temperature":
            df.iloc[start : start + 2, df.columns.get_loc("temperature")] += rng.uniform(8, 12)
        elif kind == "pic_vibration":
            df.iloc[start : start + 3, df.columns.get_loc("vibration")] += rng.uniform(1.0, 1.5)
        else:  # dérive : la température monte vite pendant 10 minutes
            ramp = np.linspace(0, rng.uniform(12, 18), 10)
            df.iloc[start : start + 10, df.columns.get_loc("temperature")] += ramp
        faults.append({"timestamp": df.index[start], "machine": machine, "type": kind})
    return faults


def main():
    rng = np.random.default_rng(SEED)
    index = pd.date_range(START, periods=DAYS * 1440, freq="min")

    frames, all_faults = [], []
    for machine in MACHINES:
        df = simulate_machine(rng, index)
        all_faults += inject_faults(rng, df, machine)
        df.insert(0, "machine", machine)
        frames.append(df)

    data = pd.concat(frames).rename_axis("timestamp").reset_index()
    data = data.round({"temperature": 2, "vibration": 3, "humidity": 2})

    OUT_DIR.mkdir(exist_ok=True)
    data.to_csv(OUT_DIR / "measures.csv", index=False)
    pd.DataFrame(all_faults).to_csv(OUT_DIR / "faults_truth.csv", index=False)
    print(f"{len(data)} mesures générées -> {OUT_DIR / 'measures.csv'}")
    print(f"{len(all_faults)} pannes injectées -> {OUT_DIR / 'faults_truth.csv'}")


if __name__ == "__main__":
    main()
