#!/usr/bin/env python3
"""Tesla Charging Optimizer - Find cheapest Octopus Agile slots for charging."""

import os
import math
import requests
from datetime import datetime
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# Configuration
HA_URL = os.environ.get("HA_URL", "http://192.168.1.162:8123")
HA_TOKEN = os.environ.get("HA_TOKEN")

# Tesla Model Y Long Range specs
BATTERY_CAPACITY_KWH = 75  # Usable battery capacity
CHARGER_POWER_KW = 7  # Home charger power
SLOT_DURATION_HOURS = 0.5  # 30-minute slots
KWH_PER_SLOT = CHARGER_POWER_KW * SLOT_DURATION_HOURS  # 3.5 kWh per slot

# Default target charge
DEFAULT_TARGET_PERCENT = 80


def load_ha_token():
    """Load HA token from environment or config file."""
    global HA_TOKEN
    if HA_TOKEN:
        return HA_TOKEN

    token_file = os.path.expanduser("~/.config/homeassistant/tokens")
    if os.path.exists(token_file):
        with open(token_file) as f:
            for line in f:
                if line.startswith("export HA_TOKEN="):
                    HA_TOKEN = line.split("=", 1)[1].strip().strip('"')
                    return HA_TOKEN
    return None


def ha_api_get(endpoint):
    """Make a GET request to Home Assistant API."""
    token = load_ha_token()
    if not token:
        raise Exception("No Home Assistant token found")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    response = requests.get(f"{HA_URL}/api/{endpoint}", headers=headers, timeout=10)
    response.raise_for_status()
    return response.json()


def get_tesla_battery():
    """Get current Tesla battery level and range."""
    try:
        # Try to get battery level
        battery_state = ha_api_get("states/sensor.tesla_model_y_battery")
        battery_percent = float(battery_state.get("state", 0))

        # Try to get range (optional)
        try:
            range_state = ha_api_get("states/sensor.tesla_model_y_range")
            range_miles = float(range_state.get("state", 0))
        except:
            range_miles = None

        # Try to get charging state (optional)
        try:
            charging_state = ha_api_get("states/sensor.tesla_model_y_charging")
            charging = charging_state.get("state", "unknown")
        except:
            charging = "unknown"

        return {
            "battery_percent": battery_percent,
            "range_miles": range_miles,
            "charging_state": charging,
        }
    except Exception as e:
        return {"error": str(e)}


def get_octopus_rates():
    """Get Octopus Agile rates from Home Assistant.

    Fetches both current day and next day rates (available after 4pm).
    This allows finding optimal charging slots that span overnight.

    Returns dict with 'rates' list and 'includes_next_day' boolean.
    """
    try:
        # Get all states and find the Octopus rates event entities
        states = ha_api_get("states")

        rates_data = []
        seen_starts = set()  # Track seen start times to avoid duplicates
        has_current_day = False
        has_next_day = False

        for state in states:
            entity_id = state.get("entity_id", "")

            # Look for both current_day_rates and next_day_rates entities
            is_current_day = "octopus_energy_electricity" in entity_id and "current_day_rates" in entity_id
            is_next_day = "octopus_energy_electricity" in entity_id and "next_day_rates" in entity_id

            if is_current_day or is_next_day:
                attributes = state.get("attributes", {})
                rates = attributes.get("rates", [])

                if rates:
                    if is_current_day:
                        has_current_day = True
                    if is_next_day:
                        has_next_day = True

                for rate in rates:
                    start = rate.get("start") or rate.get("valid_from")
                    end = rate.get("end") or rate.get("valid_to")
                    value = rate.get("value_inc_vat")

                    # Skip duplicates (next_day might overlap with current_day at midnight)
                    if start in seen_starts:
                        continue

                    if start and value is not None:
                        seen_starts.add(start)
                        # Convert from pounds to pence if value seems to be in pounds
                        rate_pence = value * 100 if value < 1 else value
                        rates_data.append({
                            "start": start,
                            "end": end,
                            "rate": rate_pence,  # p/kWh including VAT
                        })

        # Sort by start time
        rates_data.sort(key=lambda x: x["start"])

        return {
            "rates": rates_data,
            "includes_today": has_current_day,
            "includes_tomorrow": has_next_day,
        }
    except Exception as e:
        return {"error": str(e)}


def calculate_optimal_slots(current_percent, target_percent, rates):
    """Calculate the cheapest slots to charge the Tesla."""
    if isinstance(rates, dict) and "error" in rates:
        return rates

    # Calculate energy needed
    percent_needed = target_percent - current_percent
    if percent_needed <= 0:
        return {
            "message": "Battery already at or above target",
            "kwh_needed": 0,
            "slots_needed": 0,
            "slots": [],
            "total_cost": 0,
        }

    kwh_needed = (percent_needed / 100) * BATTERY_CAPACITY_KWH
    slots_needed = math.ceil(kwh_needed / KWH_PER_SLOT)

    # Filter to future slots only
    now = datetime.now().astimezone()
    future_rates = []
    for rate in rates:
        try:
            start_time = datetime.fromisoformat(rate["start"].replace("Z", "+00:00"))
            if start_time > now:
                future_rates.append(rate)
        except:
            continue

    # Sort by rate (cheapest first)
    sorted_rates = sorted(future_rates, key=lambda x: x["rate"])

    # Select cheapest slots
    selected_slots = sorted_rates[:slots_needed]

    # Sort selected slots by time for display
    selected_slots.sort(key=lambda x: x["start"])

    # Calculate total cost
    total_cost_pence = sum(slot["rate"] * KWH_PER_SLOT for slot in selected_slots)

    # Check if slots are contiguous and group into blocks
    is_contiguous = True
    blocks = []
    if selected_slots:
        current_block = {
            "start": selected_slots[0]["start"],
            "end": selected_slots[0]["end"],
            "slots": [selected_slots[0]],
            "total_cost_pence": selected_slots[0]["rate"] * KWH_PER_SLOT,
        }

        for i in range(1, len(selected_slots)):
            current_end = datetime.fromisoformat(current_block["end"].replace("Z", "+00:00"))
            next_start = datetime.fromisoformat(selected_slots[i]["start"].replace("Z", "+00:00"))

            if current_end == next_start:
                # Contiguous - extend current block
                current_block["end"] = selected_slots[i]["end"]
                current_block["slots"].append(selected_slots[i])
                current_block["total_cost_pence"] += selected_slots[i]["rate"] * KWH_PER_SLOT
            else:
                # Gap - save current block and start new one
                is_contiguous = False
                blocks.append(current_block)
                current_block = {
                    "start": selected_slots[i]["start"],
                    "end": selected_slots[i]["end"],
                    "slots": [selected_slots[i]],
                    "total_cost_pence": selected_slots[i]["rate"] * KWH_PER_SLOT,
                }

        blocks.append(current_block)

        # Add summary info to each block
        for block in blocks:
            block["slot_count"] = len(block["slots"])
            block["kwh"] = block["slot_count"] * KWH_PER_SLOT
            block["avg_rate"] = sum(s["rate"] for s in block["slots"]) / len(block["slots"])
            del block["slots"]  # Remove individual slots to keep response clean

    return {
        "kwh_needed": round(kwh_needed, 1),
        "slots_needed": slots_needed,
        "slots": selected_slots,
        "blocks": blocks,
        "total_cost_pence": round(total_cost_pence, 2),
        "total_cost_pounds": round(total_cost_pence / 100, 2),
        "is_contiguous": is_contiguous,
        "kwh_per_slot": KWH_PER_SLOT,
    }


@app.route("/")
def index():
    """Main dashboard page."""
    return render_template("index.html", default_target=DEFAULT_TARGET_PERCENT)


@app.route("/api/status")
def api_status():
    """Get current Tesla and rates status."""
    tesla = get_tesla_battery()
    rates_result = get_octopus_rates()

    if "error" in rates_result:
        return jsonify({
            "tesla": tesla,
            "rates": [],
            "rates_info": {"error": rates_result["error"]},
            "config": {
                "battery_capacity_kwh": BATTERY_CAPACITY_KWH,
                "charger_power_kw": CHARGER_POWER_KW,
                "kwh_per_slot": KWH_PER_SLOT,
            }
        })

    return jsonify({
        "tesla": tesla,
        "rates": rates_result["rates"],
        "rates_info": {
            "includes_today": rates_result["includes_today"],
            "includes_tomorrow": rates_result["includes_tomorrow"],
            "total_slots": len(rates_result["rates"]),
        },
        "config": {
            "battery_capacity_kwh": BATTERY_CAPACITY_KWH,
            "charger_power_kw": CHARGER_POWER_KW,
            "kwh_per_slot": KWH_PER_SLOT,
        }
    })


@app.route("/api/calculate")
def api_calculate():
    """Calculate optimal charging slots."""
    target = request.args.get("target", DEFAULT_TARGET_PERCENT, type=int)

    tesla = get_tesla_battery()
    if "error" in tesla:
        return jsonify({"error": tesla["error"]}), 500

    rates_result = get_octopus_rates()
    if "error" in rates_result:
        return jsonify({"error": rates_result["error"]}), 500

    current_percent = tesla.get("battery_percent", 0)
    result = calculate_optimal_slots(current_percent, target, rates_result["rates"])
    result["current_percent"] = current_percent
    result["target_percent"] = target
    result["includes_tomorrow"] = rates_result["includes_tomorrow"]

    return jsonify(result)


if __name__ == "__main__":
    # Load token on startup
    load_ha_token()
    app.run(host="0.0.0.0", port=5050, debug=True)
