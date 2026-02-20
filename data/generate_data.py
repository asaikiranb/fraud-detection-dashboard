import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

SEED = 42
np.random.seed(SEED)
random.seed(SEED)

MERCHANT_CATEGORIES = [
    "Electronics", "Groceries", "Restaurants", "Travel", "Healthcare",
    "Entertainment", "Clothing", "Gas Stations", "Online Retail", "ATM/Cash"
]

FRAUD_TYPES = [
    "Card Not Present", "Account Takeover", "Synthetic Identity",
    "Merchant Fraud", "Skimming"
]

CARD_TYPES = ["Visa", "Mastercard", "American Express", "Discover"]

TRANSACTION_CHANNELS = ["Online", "In-Store", "Mobile App", "Phone Order"]

AGE_GROUPS = ["18-25", "26-35", "36-45", "46-55", "56-65", "65+"]

US_STATES = {
    "CA": "California", "TX": "Texas", "FL": "Florida", "NY": "New York",
    "IL": "Illinois", "PA": "Pennsylvania", "OH": "Ohio", "GA": "Georgia",
    "NC": "North Carolina", "MI": "Michigan", "NJ": "New Jersey",
    "VA": "Virginia", "WA": "Washington", "AZ": "Arizona", "MA": "Massachusetts",
    "TN": "Tennessee", "IN": "Indiana", "MO": "Missouri", "MD": "Maryland",
    "WI": "Wisconsin", "CO": "Colorado", "MN": "Minnesota", "SC": "South Carolina",
    "AL": "Alabama", "LA": "Louisiana", "KY": "Kentucky", "OR": "Oregon",
    "OK": "Oklahoma", "CT": "Connecticut", "UT": "Utah", "NV": "Nevada",
    "AR": "Arkansas", "MS": "Mississippi", "KS": "Kansas", "NM": "New Mexico",
    "NE": "Nebraska", "ID": "Idaho", "WV": "West Virginia", "HI": "Hawaii",
    "NH": "New Hampshire", "ME": "Maine", "MT": "Montana", "RI": "Rhode Island",
    "DE": "Delaware", "SD": "South Dakota", "ND": "North Dakota", "AK": "Alaska",
    "VT": "Vermont", "WY": "Wyoming"
}

CITIES_BY_STATE = {
    "CA": ["Los Angeles", "San Francisco", "San Diego", "Sacramento", "San Jose"],
    "TX": ["Houston", "Dallas", "Austin", "San Antonio", "Fort Worth"],
    "FL": ["Miami", "Orlando", "Tampa", "Jacksonville", "Fort Lauderdale"],
    "NY": ["New York City", "Buffalo", "Albany", "Rochester", "Yonkers"],
    "IL": ["Chicago", "Aurora", "Naperville", "Joliet", "Rockford"],
    "PA": ["Philadelphia", "Pittsburgh", "Allentown", "Erie", "Reading"],
    "OH": ["Columbus", "Cleveland", "Cincinnati", "Toledo", "Akron"],
    "GA": ["Atlanta", "Columbus", "Augusta", "Macon", "Savannah"],
    "NC": ["Charlotte", "Raleigh", "Greensboro", "Durham", "Winston-Salem"],
    "MI": ["Detroit", "Grand Rapids", "Warren", "Sterling Heights", "Ann Arbor"],
}

STATE_FRAUD_MULTIPLIERS = {
    "CA": 1.4, "TX": 1.3, "FL": 1.6, "NY": 1.5, "IL": 1.2,
    "NV": 1.8, "AZ": 1.3, "GA": 1.4, "NC": 1.1, "OH": 1.0,
}

CATEGORY_FRAUD_RATES = {
    "Electronics": 0.035, "Groceries": 0.008, "Restaurants": 0.010,
    "Travel": 0.028, "Healthcare": 0.012, "Entertainment": 0.018,
    "Clothing": 0.015, "Gas Stations": 0.022, "Online Retail": 0.032,
    "ATM/Cash": 0.040
}

CHANNEL_FRAUD_RATES = {
    "Online": 0.030, "In-Store": 0.008, "Mobile App": 0.020, "Phone Order": 0.025
}

HOUR_FRAUD_WEIGHTS = {
    0: 2.5, 1: 3.0, 2: 3.5, 3: 3.2, 4: 2.8, 5: 1.5,
    6: 0.8, 7: 0.6, 8: 0.5, 9: 0.6, 10: 0.7, 11: 0.8,
    12: 0.9, 13: 1.0, 14: 1.0, 15: 1.0, 16: 1.1, 17: 1.2,
    18: 1.3, 19: 1.4, 20: 1.5, 21: 1.8, 22: 2.0, 23: 2.3
}


def generate_fraud_dataset(n_transactions: int = 50000) -> pd.DataFrame:
    """Generate a realistic synthetic credit card fraud dataset."""

    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 12, 31)
    date_range_seconds = int((end_date - start_date).total_seconds())

    timestamps = [
        start_date + timedelta(seconds=random.randint(0, date_range_seconds))
        for _ in range(n_transactions)
    ]
    timestamps.sort()

    merchant_categories = np.random.choice(
        MERCHANT_CATEGORIES,
        n_transactions,
        p=[0.12, 0.18, 0.14, 0.10, 0.08, 0.08, 0.10, 0.08, 0.08, 0.04]
    )

    card_types = np.random.choice(
        CARD_TYPES, n_transactions, p=[0.40, 0.35, 0.15, 0.10]
    )

    channels = np.random.choice(
        TRANSACTION_CHANNELS, n_transactions, p=[0.42, 0.35, 0.18, 0.05]
    )

    age_groups = np.random.choice(
        AGE_GROUPS, n_transactions, p=[0.12, 0.22, 0.25, 0.20, 0.13, 0.08]
    )

    state_keys = list(US_STATES.keys())
    state_weights = [0.12, 0.09, 0.07, 0.06, 0.04, 0.04, 0.04, 0.03, 0.03, 0.03,
                     0.03, 0.03, 0.03, 0.03, 0.03, 0.02, 0.02, 0.02, 0.02, 0.02,
                     0.02, 0.02, 0.02, 0.02, 0.02, 0.01, 0.01, 0.01, 0.01, 0.01,
                     0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01,
                     0.01, 0.01, 0.01, 0.01, 0.01, 0.005, 0.005, 0.005, 0.005]
    state_weights = state_weights[:len(state_keys)]
    state_weights = [w / sum(state_weights) for w in state_weights]
    states = np.random.choice(state_keys, n_transactions, p=state_weights)

    cities = []
    for state in states:
        if state in CITIES_BY_STATE:
            cities.append(random.choice(CITIES_BY_STATE[state]))
        else:
            cities.append(US_STATES[state] + " City")

    amounts = []
    for cat, channel in zip(merchant_categories, channels):
        if cat == "Electronics":
            base = np.random.lognormal(5.5, 0.8)
        elif cat == "Groceries":
            base = np.random.lognormal(3.5, 0.5)
        elif cat == "Travel":
            base = np.random.lognormal(5.8, 0.9)
        elif cat == "ATM/Cash":
            base = np.random.choice([20, 40, 60, 80, 100, 200, 300, 500],
                                    p=[0.15, 0.20, 0.15, 0.10, 0.20, 0.10, 0.05, 0.05])
        else:
            base = np.random.lognormal(3.8, 0.7)

        if channel == "Phone Order":
            base *= 1.2
        amounts.append(round(min(base, 9999.99), 2))

    is_fraud = []
    fraud_types = []

    for i, (cat, channel, state, ts) in enumerate(zip(merchant_categories, channels, states, timestamps)):
        hour = ts.hour
        base_rate = (CATEGORY_FRAUD_RATES.get(cat, 0.015) +
                     CHANNEL_FRAUD_RATES.get(channel, 0.015)) / 2
        hour_mult = HOUR_FRAUD_WEIGHTS.get(hour, 1.0)
        state_mult = STATE_FRAUD_MULTIPLIERS.get(state, 1.0)

        fraud_prob = base_rate * hour_mult * state_mult

        if random.random() < fraud_prob:
            is_fraud.append(1)
            if cat in ["Online Retail", "Electronics"] or channel == "Online":
                fraud_type = np.random.choice(FRAUD_TYPES[:3], p=[0.45, 0.30, 0.25])
            elif cat == "ATM/Cash":
                fraud_type = np.random.choice(["Skimming", "Account Takeover"], p=[0.65, 0.35])
            else:
                fraud_type = np.random.choice(FRAUD_TYPES, p=[0.30, 0.25, 0.20, 0.15, 0.10])
            fraud_types.append(fraud_type)
        else:
            is_fraud.append(0)
            fraud_types.append(None)

    df = pd.DataFrame({
        "transaction_id": [f"TXN{str(i+1).zfill(7)}" for i in range(n_transactions)],
        "timestamp": timestamps,
        "amount": amounts,
        "merchant_category": merchant_categories,
        "card_type": card_types,
        "transaction_channel": channels,
        "age_group": age_groups,
        "state": states,
        "state_name": [US_STATES[s] for s in states],
        "city": cities,
        "is_fraud": is_fraud,
        "fraud_type": fraud_types,
    })

    df["date"] = df["timestamp"].dt.date
    df["hour"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.day_name()
    df["month"] = df["timestamp"].dt.month
    df["month_name"] = df["timestamp"].dt.strftime("%b %Y")
    df["week"] = df["timestamp"].dt.isocalendar().week.astype(int)
    df["quarter"] = df["timestamp"].dt.quarter

    return df


@staticmethod
def get_summary_stats(df: pd.DataFrame) -> dict:
    """Compute top-level summary statistics."""
    total = len(df)
    fraud = df["is_fraud"].sum()
    fraud_amount = df[df["is_fraud"] == 1]["amount"].sum()
    avg_fraud_amount = df[df["is_fraud"] == 1]["amount"].mean()
    total_amount = df["amount"].sum()

    return {
        "total_transactions": total,
        "fraud_count": fraud,
        "fraud_rate": fraud / total * 100,
        "fraud_amount": fraud_amount,
        "avg_fraud_amount": avg_fraud_amount,
        "total_amount": total_amount,
        "legitimate_count": total - fraud,
    }
