#!/usr/bin/env python3
"""Generate pass_list.csv — original utility script (restored from pre-GUI version).

Run:  python3 gen_pass_terminal.py
"""
import csv
import random

# Seed for reproducibility
random.seed(42)

# Word lists suitable for game passwords/passphrases
words = [
    "Dragon", "Shadow", "Falcon", "Mystic", "Crystal", "Knight", "Blaze", "Viper",
    "Storm", "Frost", "Thunder", "Echo", "Silver", "Crimson", "Phantom", "Lunar",
    "Solar", "Rogue", "Titan", "Nova", "Cosmic", "Iron", "Silent", "Golden",
    "Abyss", "Chaos", "Radiant", "Vortex", "Cobra", "Phoenix", "Raven", "Hunter",
    "Breeze", "Warlock", "Archer", "Shield", "Blade", "Crown", "Ghost", "Nebula",
    "Onyx", "Ruby", "Sapphire", "Emerald", "Apex", "Zenith", "Spire", "Rift",
    "Haven", "Dusk", "Dawn", "Rune", "Glyph", "Gorgon", "Oracle", "Valiant"
]

data = []
num_entries = 60  # Generate 60 entries (meets the "at least 50" requirement)

for i in range(1, num_entries + 1):
    w1 = random.choice(words)
    w2 = random.choice(words)
    # Ensure two distinct words if possible
    while w2 == w1:
        w2 = random.choice(words)
    num = f"{random.randint(10, 99)}"
    password = f"{w1}{num}{w2}"
    data.append({"id": i, "pass": password})

filename = "pass_list.csv"
with open(filename, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "pass"])
    writer.writeheader()
    writer.writerows(data)

print(f"Generated {len(data)} rows in {filename}")