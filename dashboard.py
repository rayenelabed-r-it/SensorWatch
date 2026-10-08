"""Tableau de bord Streamlit : lancer avec `streamlit run dashboard.py`."""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from alert import group_events

DATA_FILE = Path("data/measures_flagged.csv")
METRICS = {"temperature": "Température (°C)", "vibration": "Vibrations", "humidity": "Humidité (%)"}

st.set_page_config(page_title="SensorWatch", layout="wide")
st.title("SensorWatch")
st.caption("Surveillance de capteurs simulés : mesures, anomalies et alertes")

if not DATA_FILE.exists():
    st.error("Fichier introuvable. Lance d'abord : python generate_data.py puis python detect_anomalies.py")
    st.stop()


@st.cache_data
def load():
    return pd.read_csv(DATA_FILE, parse_dates=["timestamp"])


df = load()

machine = st.sidebar.selectbox("Machine", sorted(df["machine"].unique()))
metric = st.sidebar.selectbox("Mesure", list(METRICS), format_func=METRICS.get)

subset = df[df["machine"] == machine]
anomalies = subset[subset["anomaly"]]
events = group_events(anomalies) if not anomalies.empty else []

col1, col2, col3 = st.columns(3)
col1.metric("Mesures analysées", f"{len(subset):,}".replace(",", " "))
col2.metric("Mesures anormales", int(subset["anomaly"].sum()))
col3.metric("Alertes (événements)", len(events))

fig, ax = plt.subplots(figsize=(11, 4))
ax.plot(subset["timestamp"], subset[metric], linewidth=0.8, label=METRICS[metric])
ax.scatter(anomalies["timestamp"], anomalies[metric], color="red", s=18, label="Anomalie", zorder=3)
ax.set_xlabel("Temps")
ax.set_ylabel(METRICS[metric])
ax.legend()
fig.autofmt_xdate()
st.pyplot(fig)

st.subheader("Dernières alertes")
if events:
    table = pd.DataFrame([{"Heure": e["timestamp"], "Machine": e["machine"]} for e in events[-10:]])
    st.dataframe(table, use_container_width=True)
else:
    st.success("Aucune anomalie pour cette machine.")
