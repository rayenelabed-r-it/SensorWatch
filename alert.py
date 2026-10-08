"""Envoie des alertes quand des anomalies sont détectées.

Par défaut : messages dans la console.
Option : email, si les variables d'environnement ALERT_EMAIL_TO,
SMTP_HOST, SMTP_USER et SMTP_PASSWORD sont définies.
"""
import os
import smtplib
from email.message import EmailMessage

import pandas as pd

MAX_GAP_MINUTES = 5  # deux anomalies éloignées de plus de 5 min = deux événements


def group_events(anomalies):
    """Regroupe les anomalies consécutives d'une même machine en un seul événement."""
    events = []
    for machine, rows in anomalies.sort_values("timestamp").groupby("machine"):
        last_time = None
        for _, row in rows.iterrows():
            if last_time is None or (row["timestamp"] - last_time) > pd.Timedelta(minutes=MAX_GAP_MINUTES):
                events.append(row)
            last_time = row["timestamp"]
    return sorted(events, key=lambda r: r["timestamp"])


def describe(row):
    z_cols = [c for c in row.index if c.startswith("z_")]
    worst = max(z_cols, key=lambda c: abs(row[c]) if pd.notna(row[c]) else 0)
    metric = worst.replace("z_", "")
    return (f"[ALERTE] {row['timestamp']} | {row['machine']} | "
            f"{metric} = {row[metric]} (z = {row[worst]:.1f})")


def send_email(lines):
    to = os.getenv("ALERT_EMAIL_TO")
    host = os.getenv("SMTP_HOST")
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")
    if not all([to, host, user, password]):
        return False
    msg = EmailMessage()
    msg["Subject"] = f"SensorWatch : {len(lines)} alerte(s)"
    msg["From"], msg["To"] = user, to
    msg.set_content("\n".join(lines))
    with smtplib.SMTP_SSL(host, 465) as server:
        server.login(user, password)
        server.send_message(msg)
    return True


def send_alerts(anomalies):
    if anomalies.empty:
        print("Aucune anomalie détectée.")
        return
    lines = [describe(row) for row in group_events(anomalies)]
    print(f"\n{len(lines)} alerte(s) :")
    for line in lines:
        print(line)
    if send_email(lines):
        print("Email d'alerte envoyé.")
