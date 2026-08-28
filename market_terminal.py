#!/usr/bin/env python3
"""IDeK market — original command-line market module (restored from pre-GUI version).

Run standalone:  python3 market_terminal.py
"""
import random
import os
import time
import csv
import sys
import tty
import termios
from functions_terminal import body_text

MARKET_FIELDS = ["risk_id", "value", "change", "type", "streak", "event"]

# num1 = random.randint(1, total_rows)
def create_markets():
    filename = "market_history.csv"

    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        return

    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=MARKET_FIELDS)
        writer.writeheader()
        for risk_id, upper_bound in ((1, 10.00), (2, 50.00), (3, 100.00)):
            writer.writerow({
                "risk_id": risk_id,
                "value": round(random.uniform(0.01, upper_bound), 2),
                "change": 0,
                "type": "",
                "streak": 0,
                "event": "",
            })


def call_market_update(risk_id, lower_bound, upper_bound, mode, change, current_streak, type=None, current_value=0, event=""): 
    # lower_bound, upper_bound, mode, change, current_streak, current_value
    filename = "market_history.csv"

    with open(filename, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=MARKET_FIELDS)
        #writer.writeheader()

        # Low-Risk: Risk ID: 1
        if current_value == 0:
            current_value = round(random.uniform(lower_bound, upper_bound),2)
        
        #change = 0
        #current_streak = 0
        writer.writerow({"risk_id": risk_id, "value": current_value, "change": change, "type": type, "streak": current_streak, "event": event})




def calc_market():
    market_rows = []
    for risk_id in (1, 2, 3):
        previous = find_recent_market_row(risk_id)
        previous_type = previous.get("type")
        previous_streak = int(previous.get("streak") or 0)

        if risk_id == 1:
            # Low risk: a down move is followed by a 70% chance of an up move.
            up_probability = 0.7 if previous_type == "1" else 0.5
            change_limit = 3
        elif risk_id == 2:
            up_probability = 0.5
            change_limit = 7.5
        else:
            # High risk reverses after three equal moves, but can keep running.
            up_probability = 0.5
            if previous_streak >= 3:
                up_probability = 0.7 if previous_type == "1" else 0.3
            change_floor = 5
            change_limit = 15

        market_type = 0 if random.random() < up_probability else 1
        direction = 1 if market_type == 0 else -1
        change_floor = 0.1 if risk_id != 3 else change_floor
        change = round(random.uniform(change_floor, change_limit) * direction, 1)
        streak = previous_streak + 1 if str(market_type) == previous_type else 1
        event = ""

        if risk_id == 3 and streak >= 5 and random.random() < 0.05:
            event = "break" if market_type == 0 else "crash"
            change = round(random.uniform(5, 15) * direction, 1)

        current_value = round(float(previous["value"]) * (1 + change / 100), 2)
        current_value = max(0, current_value)
        call_market_update(risk_id, 0, 0, "a", change, streak, market_type, current_value, event)
        market_rows.append({
            "risk_id": risk_id,
            "value": current_value,
            "change": change,
            "type": market_type,
            "streak": streak,
            "event": event,
        })

    return market_rows


def view_market(name):
    risk_labels = {
        1: "Low-Risk",
        2: "Medium-Risk",
        3: "High-Risk",
    }
    market_lines = []
    for risk_id, label in risk_labels.items():
        history = find_market_history(risk_id)
        current_value = float(history[-1]["value"])
        previous_value = float(history[-2]["value"]) if len(history) > 1 else current_value
        percent_change = float(history[-1]["change"])
        dollar_change = current_value - previous_value
        dollar_sign = "+$" if dollar_change >= 0 else "-$"
        market_lines.append(
            f"{label}: {current_value:.2f} "
            f"[{percent_change:+.1f}%, {dollar_sign}{abs(dollar_change):.2f}]"
        )
    market_info = "\n".join(market_lines)
    body_text(name, market_info, 3)
    return market_info

def retreive_market(risk_id,find_row):
    risk_history = []
    filename = "market_history.csv"
    with open(filename, mode="r", newline="", encoding="utf-8") as f:
        data_list = list(csv.DictReader(f))
        for row in data_list:
            if row["risk_id"] == str(risk_id):
                risk_history.append(row[find_row])
        return risk_history

def find_recent_market(risk_id):
    return find_recent_market_row(risk_id)["value"]


def find_market_history(risk_id):
    with open("market_history.csv", mode="r", newline="", encoding="utf-8") as f:
        return [row for row in csv.DictReader(f) if row["risk_id"] == str(risk_id)]


def find_recent_market_row(risk_id):
    risk_history = []
    filename = "market_history.csv"
    with open(filename, mode="r", newline="", encoding="utf-8") as f:
        data_list = list(csv.DictReader(f))
        for row in data_list:
            if row["risk_id"] == str(risk_id):
                risk_history.append(row)
        return risk_history[-1]

if __name__ == "__main__":
    create_markets()
    calc_market()
    view_market("Test")