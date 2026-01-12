from __future__ import annotations

import csv
import math
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


SEED = 42
ROW_COUNT = 1000
TZ = timezone(timedelta(hours=5, minutes=30))

CARD_NETWORKS = ["VISA", "MASTERCARD", "AMEX", "RUPAY"]
CARD_TYPES = ["CREDIT", "DEBIT"]
MERCHANT_CATEGORIES = [
    "Grocery",
    "Fuel",
    "Travel",
    "Ecomm",
    "Dining",
    "Utilities",
    "Pharmacy",
    "Entertainment",
    "Other",
]
CITIES = [
    "Bangalore",
    "Mumbai",
    "Delhi",
    "Pune",
    "Hyderabad",
    "Chennai",
    "Kolkata",
    "Ahmedabad",
]
COUNTRY_CHOICES = ["US", "SG", "AE", "GB", "DE"]
CURRENCY_BY_COUNTRY = {"US": "USD", "SG": "SGD", "AE": "AED", "GB": "GBP", "DE": "EUR"}
FX_RANGES = {
    "USD": (74.0, 92.0),
    "SGD": (54.0, 72.0),
    "EUR": (82.0, 98.0),
    "GBP": (95.0, 112.0),
    "AED": (20.0, 26.0),
}
DECLINE_REASONS = [
    "INSUFFICIENT_FUNDS",
    "SUSPECTED_FRAUD",
    "INVALID_PIN",
    "NETWORK_ERROR",
    "LIMIT_EXCEEDED",
]

CITY_COORDS = {
    "Bangalore": (12.9716, 77.5946),
    "Mumbai": (19.076, 72.8777),
    "Delhi": (28.7041, 77.1025),
    "Pune": (18.5204, 73.8567),
    "Hyderabad": (17.385, 78.4867),
    "Chennai": (13.0827, 80.2707),
    "Kolkata": (22.5726, 88.3639),
    "Ahmedabad": (23.0225, 72.5714),
}

MERCHANTS_BY_CATEGORY = {
    "Grocery": ["FreshBasket", "DailyMart", "GreenLeaf Grocers"],
    "Fuel": ["SpeedFuel", "MetroPetro", "FuelPoint"],
    "Travel": ["SkyRoute", "CityCab", "RailEase"],
    "Ecomm": ["ShopSphere", "UrbanCart", "ClickBazaar"],
    "Dining": ["SpiceTrail", "Cafe Mosaic", "TasteHub"],
    "Utilities": ["PowerGrid", "AquaFlow", "NetConnect"],
    "Pharmacy": ["MediPlus", "HealthFirst", "WellnessRx"],
    "Entertainment": ["StarCinemas", "FunZone", "PlayArena"],
    "Other": ["QuickServices", "LocalStore", "CityServices"],
}


def _right_skewed_amount(category: str, rng: random.Random) -> float:
    base = rng.lognormvariate(4.3, 0.6)
    if category in {"Travel", "Ecomm"}:
        base *= rng.uniform(2.0, 4.5)
    elif category == "Fuel":
        base *= rng.uniform(0.8, 1.5)
    elif category == "Utilities":
        base *= rng.uniform(1.0, 2.0)
    amount = min(base, 150000.0)
    return round(max(amount, 75.0), 2)


def _choose_time(now: datetime, rng: random.Random) -> datetime:
    days_back = rng.randint(0, 179)
    seconds = rng.randint(0, 86399)
    return now - timedelta(days=days_back, seconds=seconds)


def _risk_score(amount: float, channel: str, is_international: int, ip_mismatch: bool, rng: random.Random) -> int:
    score = rng.randint(5, 55)
    if amount > 50000:
        score += 20
    elif amount > 20000:
        score += 12
    if channel == "ECOM":
        score += 12
    if is_international:
        score += 18
    if ip_mismatch:
        score += 20
    return min(score, 100)


def _format_decimal(value: float) -> str:
    return f"{value:.2f}"


def generate_rows(count: int) -> List[Dict[str, Any]]:
    rng = random.Random(SEED)
    now = datetime.now(tz=TZ)
    rows: List[Dict[str, Any]] = []

    for idx in range(count):
        card_network = rng.choice(CARD_NETWORKS)
        card_type = rng.choice(CARD_TYPES)
        category = rng.choice(MERCHANT_CATEGORIES)
        merchant_name = rng.choice(MERCHANTS_BY_CATEGORY[category])
        city = rng.choice(CITIES)
        channel = rng.choices(["POS", "ECOM", "ATM"], weights=[0.62, 0.30, 0.08])[0]
        auth_type = "chip_pin"
        if channel == "ECOM":
            auth_type = "online"
        elif channel == "ATM":
            auth_type = "atm_pin"
        else:
            auth_type = rng.choice(["chip_pin", "contactless"])

        status = "APPROVED" if rng.random() > 0.08 else "DECLINED"
        decline_reason = "" if status == "APPROVED" else rng.choice(DECLINE_REASONS)

        is_international = 1 if rng.random() < 0.06 else 0
        merchant_country = "IN"
        currency = "INR"
        fx_rate: Optional[float] = None

        if is_international:
            merchant_country = rng.choice(COUNTRY_CHOICES)
            currency = CURRENCY_BY_COUNTRY.get(merchant_country, "USD")
            fx_low, fx_high = FX_RANGES[currency]
            fx_rate = rng.uniform(fx_low, fx_high)

        amount = _right_skewed_amount(category, rng)
        amount_base_inr = amount
        if is_international and fx_rate is not None:
            amount_base_inr = amount * fx_rate

        ip_country = "IN"
        ip_mismatch = False
        if channel == "ECOM" and rng.random() < 0.08:
            ip_country = rng.choice([c for c in COUNTRY_CHOICES if c != "IN"])
            ip_mismatch = True

        device_id = ""
        if channel == "ECOM":
            device_id = f"dev_{rng.getrandbits(40):010x}"

        risk = _risk_score(amount_base_inr, channel, is_international, ip_mismatch, rng)

        latitude = ""
        longitude = ""
        if channel != "ECOM":
            coords = CITY_COORDS.get(city)
            if coords and rng.random() < 0.85:
                latitude = f"{coords[0] + rng.uniform(-0.05, 0.05):.6f}"
                longitude = f"{coords[1] + rng.uniform(-0.05, 0.05):.6f}"

        row = {
            "transaction_id": f"txn_{idx + 1:05d}_{rng.getrandbits(32):08x}",
            "account_id": f"ACC{rng.randint(1000, 9999)}",
            "customer_id": f"CUST{rng.randint(10000, 99999)}",
            "card_network": card_network,
            "card_type": card_type,
            "product": "Branded Cards",
            "txn_ts": _choose_time(now, rng).isoformat(),
            "amount_inr": _format_decimal(amount),
            "currency": currency,
            "merchant_name": merchant_name,
            "merchant_category": category,
            "merchant_city": city,
            "merchant_country": merchant_country,
            "channel": channel,
            "auth_type": auth_type,
            "status": status,
            "decline_reason": decline_reason,
            "is_international": str(is_international),
            "fx_rate": "" if not is_international else _format_decimal(fx_rate or 0.0),
            "amount_base_inr": _format_decimal(amount_base_inr),
            "risk_score": str(risk),
            "fraud_label": "0",
            "device_id": device_id,
            "ip_country": ip_country,
            "latitude": latitude,
            "longitude": longitude,
        }
        rows.append(row)

    _assign_fraud_labels(rows, rng)
    return rows


def _assign_fraud_labels(rows: List[Dict[str, Any]], rng: random.Random) -> None:
    candidates = []
    for idx, row in enumerate(rows):
        risk = int(row["risk_score"])
        is_international = row["is_international"] == "1"
        channel = row["channel"]
        ip_mismatch = row["ip_country"] != "IN"
        score = risk
        if channel == "ECOM":
            score += 10
        if is_international:
            score += 10
        if ip_mismatch:
            score += 15
        candidates.append((score, idx))

    candidates.sort(reverse=True)
    target = max(10, int(math.ceil(len(rows) * 0.015)))

    fraud_indices = set()
    for score, idx in candidates:
        if score >= 90 and rng.random() < 0.6:
            fraud_indices.add(idx)
        if len(fraud_indices) >= target:
            break

    if len(fraud_indices) < target:
        for _, idx in candidates:
            fraud_indices.add(idx)
            if len(fraud_indices) >= target:
                break

    for idx in fraud_indices:
        rows[idx]["fraud_label"] = "1"
        rows[idx]["risk_score"] = str(max(int(rows[idx]["risk_score"]), rng.randint(85, 100)))
        if rows[idx]["channel"] != "ECOM":
            rows[idx]["channel"] = "ECOM"
            rows[idx]["auth_type"] = "online"
            rows[idx]["device_id"] = rows[idx]["device_id"] or f"dev_{rng.getrandbits(40):010x}"
        if rows[idx]["ip_country"] == "IN" and rng.random() < 0.6:
            rows[idx]["ip_country"] = rng.choice(COUNTRY_CHOICES)


def write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    fieldnames = [
        "transaction_id",
        "account_id",
        "customer_id",
        "card_network",
        "card_type",
        "product",
        "txn_ts",
        "amount_inr",
        "currency",
        "merchant_name",
        "merchant_category",
        "merchant_city",
        "merchant_country",
        "channel",
        "auth_type",
        "status",
        "decline_reason",
        "is_international",
        "fx_rate",
        "amount_base_inr",
        "risk_score",
        "fraud_label",
        "device_id",
        "ip_country",
        "latitude",
        "longitude",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    product_root = Path(__file__).resolve().parents[1]
    data_path = product_root / "data" / "branded_cards_transactions.csv"
    rows = generate_rows(ROW_COUNT)
    write_csv(data_path, rows)


if __name__ == "__main__":
    main()
