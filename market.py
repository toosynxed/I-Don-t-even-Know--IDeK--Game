#!/usr/bin/env python3
"""IDeK market board — run with: /usr/bin/python3 market.py

Homebrew Python builds often lack Tk; macOS system Python includes it.
"""
import random
import os
import csv
import sys
from collections import defaultdict

try:
    import tkinter as tk
    from tkinter import messagebox
    HAS_TK = True
except ModuleNotFoundError:
    HAS_TK = False
    tk = None
    messagebox = None

MARKET_FIELDS = ["risk_id", "value", "change", "type", "streak", "event"]
RISK_LABELS = {
    1: "Low-Risk",
    2: "Medium-Risk",
    3: "High-Risk",
}
RISK_BOUNDS = {
    1: (0.01, 10.00),
    2: (0.01, 50.00),
    3: (0.01, 100.00),
}
HISTORY_FILE = "market_history.csv"
WALLET_FILE = "user_wallets.csv"
HOLDINGS_FILE = "user_holdings.csv"
WALLET_FIELDS = ["username", "cash"]
HOLDINGS_FIELDS = ["username", "risk_id", "cost", "quantity"]
MAX_HOLDINGS = 5  # max buy-lots (orders) per risk level — quantity is separate
STARTING_CASH = 500.00
TICK_MS = 5000
GRAPH_POINTS = 40


def _ensure_csv(path, fieldnames):
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return
    with open(path, mode="w", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=fieldnames).writeheader()


def _holding_qty(holding):
    try:
        return max(1, int(holding.get("quantity") or 1))
    except (TypeError, ValueError):
        return 1


def _normalize_holding(holding):
    return {
        "cost": round(float(holding["cost"]), 2),
        "quantity": _holding_qty(holding),
    }


def load_user_wallet(username):
    """Return cash for username, creating a starting balance if new."""
    _ensure_csv(WALLET_FILE, WALLET_FIELDS)
    key = (username or "").strip().lower()
    if not key:
        return STARTING_CASH

    with open(WALLET_FILE, mode="r", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("username", "").strip().lower() == key:
                try:
                    return round(float(row.get("cash") or STARTING_CASH), 2)
                except ValueError:
                    return STARTING_CASH

    save_user_wallet(username, STARTING_CASH)
    return STARTING_CASH


def save_user_wallet(username, cash):
    _ensure_csv(WALLET_FILE, WALLET_FIELDS)
    key = (username or "").strip().lower()
    if not key:
        return

    rows = []
    found = False
    with open(WALLET_FILE, mode="r", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("username", "").strip().lower() == key:
                rows.append({"username": username.strip(), "cash": f"{round(float(cash), 2):.2f}"})
                found = True
            else:
                rows.append({
                    "username": row.get("username", ""),
                    "cash": row.get("cash", f"{STARTING_CASH:.2f}"),
                })
    if not found:
        rows.append({"username": username.strip(), "cash": f"{round(float(cash), 2):.2f}"})

    with open(WALLET_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=WALLET_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def load_user_holdings(username):
    """Return defaultdict(list) of {risk_id: [{"cost", "quantity"}, ...]} — one entry per buy."""
    _ensure_csv(HOLDINGS_FILE, HOLDINGS_FIELDS)
    holdings = defaultdict(list)
    key = (username or "").strip().lower()
    if not key:
        return holdings

    with open(HOLDINGS_FILE, mode="r", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("username", "").strip().lower() != key:
                continue
            try:
                risk_id = int(row["risk_id"])
                cost = round(float(row["cost"]), 2)
                quantity = max(1, int(float(row.get("quantity") or 1)))
            except (KeyError, ValueError, TypeError):
                continue
            if risk_id in RISK_LABELS and len(holdings[risk_id]) < MAX_HOLDINGS:
                holdings[risk_id].append({"cost": cost, "quantity": quantity})
    return holdings


def save_user_holdings(username, holdings):
    """Rewrite this user's holdings rows (keeps other users intact)."""
    _ensure_csv(HOLDINGS_FILE, HOLDINGS_FIELDS)
    key = (username or "").strip().lower()
    if not key:
        return

    other_rows = []
    with open(HOLDINGS_FILE, mode="r", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("username", "").strip().lower() != key:
                try:
                    qty = max(1, int(float(row.get("quantity") or 1)))
                except (TypeError, ValueError):
                    qty = 1
                other_rows.append({
                    "username": row.get("username", ""),
                    "risk_id": row.get("risk_id", ""),
                    "cost": row.get("cost", ""),
                    "quantity": str(qty),
                })

    user_rows = []
    for risk_id, items in sorted(holdings.items()):
        for item in items:
            h = _normalize_holding(item)
            user_rows.append({
                "username": username.strip(),
                "risk_id": str(risk_id),
                "cost": f"{h['cost']:.2f}",
                "quantity": str(h["quantity"]),
            })

    with open(HOLDINGS_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=HOLDINGS_FIELDS)
        writer.writeheader()
        writer.writerows(other_rows + user_rows)


def save_user_portfolio(username, cash, holdings):
    save_user_wallet(username, cash)
    save_user_holdings(username, holdings)


def create_markets():
    if os.path.exists(HISTORY_FILE) and os.path.getsize(HISTORY_FILE) > 0:
        return

    with open(HISTORY_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=MARKET_FIELDS)
        writer.writeheader()
        for risk_id, (_, upper_bound) in RISK_BOUNDS.items():
            writer.writerow({
                "risk_id": risk_id,
                "value": round(random.uniform(0.01, upper_bound), 2),
                "change": 0,
                "type": "",
                "streak": 0,
                "event": "",
            })


def call_market_update(
    risk_id,
    lower_bound,
    upper_bound,
    mode,
    change,
    current_streak,
    type=None,
    current_value=0,
    event="",
):
    with open(HISTORY_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=MARKET_FIELDS)
        if current_value == 0:
            current_value = round(random.uniform(lower_bound, upper_bound), 2)
        writer.writerow({
            "risk_id": risk_id,
            "value": current_value,
            "change": change,
            "type": type,
            "streak": current_streak,
            "event": event,
        })


def _apply_price(previous_value, change_pct):
    current_value = round(float(previous_value) * (1 + change_pct / 100), 2)
    return max(0.0, current_value)


def parse_event(raw):
    """Return (kind, ticks_left). kind is 'crash', 'break', or ''."""
    raw = (raw or "").strip()
    if not raw:
        return "", 0
    if ":" in raw:
        kind, left = raw.split(":", 1)
        try:
            return kind.strip().lower(), max(0, int(left))
        except ValueError:
            return kind.strip().lower(), 0
    return raw.lower(), 1


def format_event(kind, ticks_left):
    if not kind or ticks_left <= 0:
        return ""
    return f"{kind}:{ticks_left}"


def _high_risk_event_move(kind):
    if kind == "crash":
        magnitude = round(random.uniform(5, 10), 1)
        return -magnitude, "1"
    # break = ups use the high-risk increase range
    magnitude = round(random.uniform(5, 12.5), 1)
    return magnitude, "0"


def _append_market_row(market_rows, risk_id, change, streak, market_type, current_value, event):
    # No max cap on ticks — RISK_BOUNDS only apply when seeding initial prices.
    current_value = max(0.0, round(float(current_value), 2))
    call_market_update(
        risk_id, 0, 0, "a", change, streak, market_type, current_value, event
    )
    market_rows.append({
        "risk_id": risk_id,
        "value": current_value,
        "change": change,
        "type": market_type,
        "streak": streak,
        "event": event,
    })


def calc_market():
    market_rows = []
    for risk_id in (1, 2, 3):
        previous = find_recent_market_row(risk_id)
        previous_type = str(previous.get("type") or "")
        previous_streak = int(previous.get("streak") or 0)
        previous_value = float(previous["value"])
        event = ""

        if risk_id == 1:
            # After a down move, bias toward rebound (70% up); otherwise 50/50.
            up_probability = 0.7 if previous_type == "1" else 0.5
            change_floor, change_limit = 0.1, 3.0
        elif risk_id == 2:
            up_probability = 0.5
            change_floor, change_limit = 0.1, 7.5
        else:
            event_kind, ticks_left = parse_event(previous.get("event"))

            # Ongoing crash/break: keep forcing moves for the remaining ticks.
            # Event ticks do not advance the market-reversal streak.
            if event_kind in ("crash", "break") and ticks_left > 1:
                change, market_type = _high_risk_event_move(event_kind)
                streak = previous_streak
                current_value = _apply_price(previous_value, change)
                event = format_event(event_kind, ticks_left - 1)
                _append_market_row(
                    market_rows, risk_id, change, streak, market_type, current_value, event
                )
                continue

            # Each tick: roll crash first, then break if no crash.
            # A hit starts a fixed 5-tick run of downs (crash) or ups (break).
            started = None
            if random.random() < 0.025:
                started = "crash"
            elif random.random() < 0.0125:
                started = "break"

            if started:
                duration = 5
                change, market_type = _high_risk_event_move(started)
                streak = previous_streak
                current_value = _apply_price(previous_value, change)
                event = format_event(started, duration)
                _append_market_row(
                    market_rows, risk_id, change, streak, market_type, current_value, event
                )
                continue

            # After 3+ same-direction moves, bias toward reversal.
            up_probability = 0.5
            if previous_streak >= 3:
                up_probability = 0.7 if previous_type == "1" else 0.3
            # Downs stay 5–10%; ups use 5–12.5%.
            change_floor, change_limit = 5.0, 10.0

        market_type = 0 if random.random() < up_probability else 1
        direction = 1 if market_type == 0 else -1
        if risk_id == 3 and market_type == 0:
            change = round(random.uniform(5.0, 12.5) * direction, 1)
        else:
            change = round(random.uniform(change_floor, change_limit) * direction, 1)
        streak = previous_streak + 1 if str(market_type) == previous_type else 1
        current_value = _apply_price(previous_value, change)
        _append_market_row(
            market_rows, risk_id, change, streak, market_type, current_value, event
        )

    return market_rows


def retreive_market(risk_id, find_row):
    risk_history = []
    with open(HISTORY_FILE, mode="r", newline="", encoding="utf-8") as f:
        data_list = list(csv.DictReader(f))
        for row in data_list:
            if row["risk_id"] == str(risk_id):
                risk_history.append(row[find_row])
        return risk_history


def find_recent_market(risk_id):
    return find_recent_market_row(risk_id)["value"]


def find_market_history(risk_id):
    with open(HISTORY_FILE, mode="r", newline="", encoding="utf-8") as f:
        return [row for row in csv.DictReader(f) if row["risk_id"] == str(risk_id)]


def find_recent_market_row(risk_id):
    risk_history = find_market_history(risk_id)
    return risk_history[-1]


def get_market_snapshot():
    snapshot = []
    for risk_id, label in RISK_LABELS.items():
        history = find_market_history(risk_id)
        prices = [float(row["value"]) for row in history]
        current = history[-1]
        current_value = prices[-1]
        previous_value = prices[-2] if len(prices) > 1 else current_value
        percent_change = float(current["change"] or 0)
        dollar_change = current_value - previous_value
        event_kind, event_ticks = parse_event(current.get("event"))
        snapshot.append({
            "risk_id": risk_id,
            "label": label,
            "value": current_value,
            "percent_change": percent_change,
            "dollar_change": dollar_change,
            "streak": int(current.get("streak") or 0),
            "event": event_kind,
            "event_ticks": event_ticks,
            "session_high": max(prices),
            "session_low": min(prices),
            "prices": prices[-GRAPH_POINTS:],
        })
    return snapshot


def portfolio_state(username):
    """JSON-serializable market + wallet snapshot for a user."""
    create_markets()
    cash = load_user_wallet(username)
    holdings = load_user_holdings(username)
    snapshot = get_market_snapshot()
    columns = []
    portfolio_value = 0.0
    for item in snapshot:
        rid = item["risk_id"]
        owned = [_normalize_holding(h) for h in holdings.get(rid, [])]
        invested = sum(h["cost"] * h["quantity"] for h in owned)
        shares = sum(h["quantity"] for h in owned)
        market_value = item["value"] * shares
        pl = market_value - invested
        gain = (pl / invested * 100) if invested else 0.0
        portfolio_value += market_value
        columns.append({
            **item,
            "holdings": owned,
            "pl": round(pl, 2),
            "gain": round(gain, 2),
            "holding_count": len(owned),
            "share_count": shares,
        })
    return {
        "username": username,
        "cash": cash,
        "net_worth": round(cash + portfolio_value, 2),
        "columns": columns,
        "max_holdings": MAX_HOLDINGS,
    }


def buy_stock(username, risk_id, quantity=1):
    """One Buy press = one holding lot with the given share quantity."""
    risk_id = int(risk_id)
    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        return {"ok": False, "error": "Quantity must be a whole number."}
    if quantity < 1:
        return {"ok": False, "error": "Quantity must be at least 1."}
    if risk_id not in RISK_LABELS:
        return {"ok": False, "error": "Invalid risk level."}
    create_markets()
    cash = load_user_wallet(username)
    holdings = load_user_holdings(username)
    if len(holdings[risk_id]) >= MAX_HOLDINGS:
        return {
            "ok": False,
            "error": f"Max {MAX_HOLDINGS} holdings (buy lots) for this risk level.",
        }
    price = float(find_recent_market(risk_id))
    if price <= 0:
        return {"ok": False, "error": "This stock is worth $0 and cannot be bought."}
    total_cost = round(price * quantity, 2)
    if cash < total_cost:
        return {"ok": False, "error": f"Need ${total_cost:.2f}, have ${cash:.2f}."}
    cash = round(cash - total_cost, 2)
    holdings[risk_id].append({"cost": price, "quantity": quantity})
    save_user_portfolio(username, cash, holdings)
    state = portfolio_state(username)
    state["ok"] = True
    state["message"] = (
        f"Opened holding: {quantity} share(s) at ${price:.2f} "
        f"(${total_cost:.2f}) — {len(holdings[risk_id])}/{MAX_HOLDINGS} lots"
    )
    return state


def sell_stock(username, risk_id, index):
    risk_id = int(risk_id)
    index = int(index)
    create_markets()
    cash = load_user_wallet(username)
    holdings = load_user_holdings(username)
    owned = holdings.get(risk_id, [])
    if not owned:
        return {"ok": False, "error": "Nothing to sell."}
    if index < 0 or index >= len(owned):
        return {"ok": False, "error": "Select a valid holding."}
    price = float(find_recent_market(risk_id))
    holding = _normalize_holding(owned.pop(index))
    qty = holding["quantity"]
    proceeds = round(price * qty, 2)
    cash = round(cash + proceeds, 2)
    pl = proceeds - holding["cost"] * qty
    save_user_portfolio(username, cash, holdings)
    state = portfolio_state(username)
    state["ok"] = True
    state["message"] = (
        f"Sold holding #{index + 1} ({qty} share(s)): "
        f"{'+' if pl >= 0 else '-'}${abs(pl):.2f}"
    )
    return state


def sell_all_stock(username, risk_id):
    risk_id = int(risk_id)
    if risk_id not in RISK_LABELS:
        return {"ok": False, "error": "Invalid risk level."}
    create_markets()
    cash = load_user_wallet(username)
    holdings = load_user_holdings(username)
    owned = [_normalize_holding(h) for h in holdings.get(risk_id, [])]
    if not owned:
        return {"ok": False, "error": "Nothing to sell."}
    price = float(find_recent_market(risk_id))
    lots = len(owned)
    shares = sum(h["quantity"] for h in owned)
    invested = sum(h["cost"] * h["quantity"] for h in owned)
    proceeds = round(price * shares, 2)
    pl = proceeds - invested
    holdings[risk_id] = []
    cash = round(cash + proceeds, 2)
    save_user_portfolio(username, cash, holdings)
    state = portfolio_state(username)
    state["ok"] = True
    state["message"] = (
        f"Sold all {lots} {RISK_LABELS[risk_id]} lot(s) / {shares} share(s) "
        f"for ${proceeds:.2f} ({'+' if pl >= 0 else '-'}${abs(pl):.2f})"
    )
    return state


if HAS_TK:

    class RiskColumn(tk.Frame):
        """One risk tier: Canvas-drawn stats/graph + Buy/Sell buttons."""

        CANVAS_H = 520

        def __init__(self, master, app, risk_id, label, colors):
            super().__init__(master, bg="#111111", highlightthickness=0, bd=0)
            self.app = app
            self.risk_id = risk_id
            self.label = label
            self.colors = colors
            self.selected_index = None
            self._holdings = []
            self._item = {
                "value": 0.0,
                "percent_change": 0.0,
                "dollar_change": 0.0,
                "session_high": 0.0,
                "session_low": 0.0,
                "event": "",
                "event_ticks": 0,
                "prices": [0.0],
            }
            self._holding_hitboxes = []

            self.canvas = tk.Canvas(
                self,
                height=self.CANVAS_H,
                bg="#111111",
                highlightthickness=1,
                highlightbackground="#666666",
                bd=0,
            )
            self.canvas.pack(fill="both", expand=True, padx=4, pady=4)
            self.canvas.bind("<Configure>", lambda _e: self.redraw())
            self.canvas.bind("<Button-1>", self._on_click)

            buttons = tk.Frame(self, bg="#111111")
            buttons.pack(fill="x", padx=4, pady=(0, 8))

            self.buy_btn = tk.Button(
                buttons,
                text="Buy",
                font=("Helvetica", 12, "bold"),
                command=lambda: app.buy(risk_id),
            )
            self.buy_btn.pack(side="left", expand=True, fill="x", padx=(0, 4))

            self.sell_btn = tk.Button(
                buttons,
                text="Sell Selected",
                font=("Helvetica", 12, "bold"),
                command=lambda: app.sell_selected(risk_id),
            )
            self.sell_btn.pack(side="left", expand=True, fill="x", padx=(4, 0))

        def update_market(self, item):
            self._item = item
            self.redraw()

        def update_portfolio(self, holdings, current_price):
            self._holdings = list(holdings)
            self._current_price = current_price
            if self.selected_index is not None and self.selected_index >= len(holdings):
                self.selected_index = None
            at_cap = len(holdings) >= MAX_HOLDINGS
            self.buy_btn.configure(state="disabled" if at_cap else "normal")
            self.sell_btn.configure(state="normal" if holdings else "disabled")
            self.redraw()

        def _on_click(self, event):
            for index, (x1, y1, x2, y2) in enumerate(self._holding_hitboxes):
                if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                    self.selected_index = index
                    self.redraw()
                    return

        def redraw(self):
            c = self.canvas
            c.delete("all")
            w = max(int(c.winfo_width()), 220)
            h = max(int(c.winfo_height()), self.CANVAS_H)
            pad = 12
            item = self._item
            colors = self.colors

            c.create_rectangle(2, 2, w - 2, h - 2, fill="#1a1a1a", outline="#888888", width=2)

            y = pad
            c.create_text(
                pad, y, anchor="nw", text=self.label.upper(),
                fill="#66ccff", font=("Courier", 14, "bold"),
            )
            y += 28

            graph_top = y
            graph_h = 150
            graph_bottom = graph_top + graph_h
            c.create_rectangle(pad, graph_top, w - pad, graph_bottom, fill="#000000", outline="#555555")
            prices = item.get("prices") or [item.get("value", 0.0)]
            lo = min(prices)
            hi = max(prices)
            if hi <= lo:
                hi = lo + 1.0
            gpad = 8
            usable_w = (w - 2 * pad) - 2 * gpad
            usable_h = graph_h - 2 * gpad
            points = []
            n = len(prices)
            for i, price in enumerate(prices):
                x = pad + gpad if n == 1 else pad + gpad + usable_w * i / (n - 1)
                gy = graph_top + gpad + usable_h * (1 - (price - lo) / (hi - lo))
                points.extend((x, gy))
            line = colors["up"] if prices[-1] >= prices[0] else colors["down"]
            if len(points) >= 4:
                c.create_line(*points, fill=line, width=2)
            c.create_text(pad + 6, graph_top + 4, anchor="nw", text=f"${hi:.2f}", fill="#888888", font=("Courier", 9))
            c.create_text(pad + 6, graph_bottom - 4, anchor="sw", text=f"${lo:.2f}", fill="#888888", font=("Courier", 9))
            y = graph_bottom + 14

            pct = item.get("percent_change", 0.0)
            dollar = item.get("dollar_change", 0.0)
            ch_color = colors["up"] if pct >= 0 else colors["down"]
            dollar_sign = "+$" if dollar >= 0 else "-$"
            c.create_text(
                pad, y, anchor="nw", text=f"${item.get('value', 0):.2f}",
                fill="#ffffff", font=("Courier", 22, "bold"),
            )
            y += 32
            c.create_text(
                pad, y, anchor="nw",
                text=f"{pct:+.1f}%  ({dollar_sign}{abs(dollar):.2f})",
                fill=ch_color, font=("Courier", 12),
            )
            y += 26

            holdings = self._holdings
            current_price = getattr(self, "_current_price", item.get("value", 0.0))
            invested = sum(h["cost"] * _holding_qty(h) for h in holdings)
            shares = sum(_holding_qty(h) for h in holdings)
            market_value = current_price * shares
            pl = market_value - invested
            gain = (pl / invested * 100) if invested > 0 else 0.0
            pl_color = colors["up"] if pl >= 0 else colors["down"]

            stats = [
                ("High", f"${item.get('session_high', 0):.2f}", "#dddddd"),
                ("Low", f"${item.get('session_low', 0):.2f}", "#dddddd"),
                ("Total P/L", f"{'+' if pl >= 0 else '-'}${abs(pl):.2f}", pl_color),
                ("% Gain", f"{gain:+.1f}%", pl_color),
                ("Lots", f"{len(holdings)} / {MAX_HOLDINGS}", "#dddddd"),
                ("Shares", str(shares), "#dddddd"),
            ]
            for title, value, color in stats:
                c.create_text(pad, y, anchor="nw", text=title, fill="#888888", font=("Courier", 11))
                c.create_text(w - pad, y, anchor="ne", text=value, fill=color, font=("Courier", 11))
                y += 18

            event = item.get("event") or ""
            if event:
                ticks = item.get("event_ticks") or 0
                tick_bit = f" · {ticks} tick{'s' if ticks != 1 else ''} left" if ticks else ""
                y += 6
                c.create_text(
                    pad, y, anchor="nw",
                    text=f"EVENT: {event.upper()}{tick_bit}",
                    fill="#ffcc66", font=("Courier", 11, "bold"),
                )
                y += 20

            y += 8
            c.create_text(pad, y, anchor="nw", text="YOUR HOLDINGS (click to select)", fill="#66ccff", font=("Courier", 11))
            y += 20

            self._holding_hitboxes = []
            if not holdings:
                c.create_text(pad, y, anchor="nw", text="(no holdings yet)", fill="#666666", font=("Courier", 11))
            else:
                for i, holding in enumerate(holdings):
                    h = _normalize_holding(holding)
                    qty = h["quantity"]
                    holding_pl = (current_price - h["cost"]) * qty
                    sign = "+" if holding_pl >= 0 else "-"
                    line_txt = f"#{i + 1}  {qty} @ ${h['cost']:.2f}  ({sign}${abs(holding_pl):.2f})"
                    selected = self.selected_index == i
                    row_top = y
                    row_bot = y + 18
                    if selected:
                        c.create_rectangle(pad - 2, row_top - 1, w - pad + 2, row_bot, fill="#1f6feb", outline="")
                    fill = "#ffffff" if selected else "#33ff66"
                    c.create_text(pad, y, anchor="nw", text=line_txt, fill=fill, font=("Courier", 11))
                    self._holding_hitboxes.append((pad - 2, row_top - 1, w - pad + 2, row_bot))
                    y += 20


    class MarketApp(tk.Toplevel):
        COLORS = {
            "up": "#33ff66",
            "down": "#ff5555",
            "accent": "#66ccff",
        }

        def __init__(self, master, player_name=None):
            super().__init__(master)
            self.player_name = (player_name or "guest").strip() or "guest"
            self.title(f"IDeK Market — {self.player_name}")
            self.configure(bg="#111111")
            self.geometry("1100x760")
            self.minsize(900, 640)
            self.resizable(True, True)
            self.transient(master)
            self.protocol("WM_DELETE_WINDOW", self._on_close)

            self.cash = load_user_wallet(self.player_name)
            self.holdings = load_user_holdings(self.player_name)
            self._tick_count = 0
            self._auto_job = None
            self.columns = {}
            self._status_text = "Auto every 5s"

            self._build_ui()
            create_markets()
            self.refresh_display()
            self.after(100, self._finish_layout)
            self._start_auto()
            self.focus_set()

        def _persist(self):
            save_user_portfolio(self.player_name, self.cash, self.holdings)

        def _on_close(self):
            self._persist()
            if self._auto_job is not None:
                self.after_cancel(self._auto_job)
                self._auto_job = None
            self.destroy()

        def _finish_layout(self):
            self.update_idletasks()
            for column in self.columns.values():
                column.redraw()
            self._draw_header()

        def _build_ui(self):
            c = self.COLORS
            self.header = tk.Canvas(self, height=48, bg="#111111", highlightthickness=0)
            self.header.pack(fill="x", padx=8, pady=(8, 0))

            board = tk.Frame(self, bg="#111111")
            board.pack(fill="both", expand=True, padx=8, pady=8)
            board.columnconfigure((0, 1, 2), weight=1, uniform="risk")
            board.rowconfigure(0, weight=1)

            for col, (risk_id, label) in enumerate(RISK_LABELS.items()):
                column = RiskColumn(board, self, risk_id, label, c)
                column.grid(row=0, column=col, sticky="nsew", padx=4)
                self.columns[risk_id] = column

            footer = tk.Frame(self, bg="#111111")
            footer.pack(fill="x", padx=12, pady=(0, 12))

            tk.Button(footer, text="Tick Now", font=("Helvetica", 12, "bold"), command=self.tick_market).pack(
                side="left"
            )

            self.auto_var = tk.BooleanVar(value=True)
            tk.Checkbutton(
                footer,
                text="Auto (5s)",
                variable=self.auto_var,
                command=self._toggle_auto,
                font=("Helvetica", 12),
                bg="#111111",
                fg="#eeeeee",
                activebackground="#111111",
                activeforeground="#eeeeee",
                selectcolor="#333333",
                highlightthickness=0,
            ).pack(side="left", padx=(16, 0))

            self.net_canvas = tk.Canvas(footer, height=28, width=220, bg="#111111", highlightthickness=0)
            self.net_canvas.pack(side="right")

        def _draw_header(self):
            h = self.header
            h.delete("all")
            w = max(int(h.winfo_width()), 400)
            h.create_text(12, 24, anchor="w", text="IDeK MARKET", fill="#66ccff", font=("Courier", 18, "bold"))
            h.create_text(w - 12, 14, anchor="e", text=f"Cash: ${self.cash:.2f}", fill="#33ff66", font=("Courier", 13))
            h.create_text(w - 12, 34, anchor="e", text=self._status_text, fill="#aaaaaa", font=("Courier", 11))

        def _draw_net(self, net):
            n = self.net_canvas
            n.delete("all")
            n.create_text(210, 14, anchor="e", text=f"Net worth: ${net:.2f}", fill="#ffffff", font=("Courier", 12))

        def _start_auto(self):
            if self._auto_job is not None:
                self.after_cancel(self._auto_job)
            self._auto_job = self.after(TICK_MS, self._auto_tick)

        def _toggle_auto(self):
            if self.auto_var.get():
                self._start_auto()
                self._status_text = "Auto every 5s"
            elif self._auto_job is not None:
                self.after_cancel(self._auto_job)
                self._auto_job = None
                self._status_text = "Auto paused"
            self._draw_header()

        def _auto_tick(self):
            self._auto_job = None
            if not self.auto_var.get():
                return
            self.tick_market()
            self._auto_job = self.after(TICK_MS, self._auto_tick)

        def tick_market(self):
            calc_market()
            self._tick_count += 1
            self.refresh_display()

        def buy(self, risk_id):
            result = buy_stock(self.player_name, risk_id)
            if not result.get("ok"):
                messagebox.showwarning("Buy failed", result.get("error", "Could not buy."))
                return
            self.cash = result["cash"]
            self.holdings = load_user_holdings(self.player_name)
            self.refresh_display()

        def sell_selected(self, risk_id):
            column = self.columns[risk_id]
            if column.selected_index is None:
                messagebox.showinfo("Select a holding", "Click a holding in the list, then Sell Selected.")
                return
            result = sell_stock(self.player_name, risk_id, column.selected_index)
            if not result.get("ok"):
                messagebox.showwarning("Sell failed", result.get("error", "Could not sell."))
                return
            self.cash = result["cash"]
            self.holdings = load_user_holdings(self.player_name)
            column.selected_index = None
            self._status_text = result.get("message", "Sold")
            self.refresh_display()

        def refresh_display(self):
            self.cash = load_user_wallet(self.player_name)
            self.holdings = load_user_holdings(self.player_name)
            snapshot = get_market_snapshot()
            portfolio_value = 0.0

            for item in snapshot:
                column = self.columns[item["risk_id"]]
                holdings = self.holdings[item["risk_id"]]
                column.update_market(item)
                column.update_portfolio(holdings, item["value"])
                portfolio_value += item["value"] * sum(_holding_qty(h) for h in holdings)

            net = self.cash + portfolio_value
            if self.auto_var.get() and not self._status_text.startswith("Sold"):
                self._status_text = f"Tick #{self._tick_count} · auto 5s"
            self._draw_header()
            self._draw_net(net)

        def destroy(self):
            try:
                self._persist()
            except Exception:
                pass
            if self._auto_job is not None:
                try:
                    self.after_cancel(self._auto_job)
                except tk.TclError:
                    pass
                self._auto_job = None
            super().destroy()


    def view_market(name=None, parent=None):
        """Open the market board (Tk). Prefer the browser UI from main.py on macOS."""
        create_markets()
        owns_loop = parent is None
        if owns_loop:
            parent = tk.Tk()
            parent.withdraw()
        app = MarketApp(parent, player_name=name)
        if owns_loop:
            parent.wait_window(app)
            parent.destroy()
        return get_market_snapshot()


    if __name__ == "__main__":
        view_market()
else:
    def view_market(name=None, parent=None):
        raise RuntimeError("Tkinter is not available. Run: /usr/bin/python3 main.py")

