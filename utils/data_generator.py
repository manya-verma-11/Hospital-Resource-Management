"""
Simulated real-time hospital resource data generator.
In production, replace these functions with actual database / API calls.
"""

import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# ─── Constants ────────────────────────────────────────────────────────────────

BRANCHES = ["Main Campus", "North Wing", "South Annex", "East Pavilion"]

DEPARTMENTS = {
    "Main Campus":   ["Emergency", "Cardiology", "Neurology",  "Oncology", "Orthopedics"],
    "North Wing":    ["Pediatrics", "Maternity",  "Surgery",    "Urology",  "Nephrology"],
    "South Annex":   ["Psychiatry", "Dermatology","Pulmonology","Gastro",   "Endocrinology"],
    "East Pavilion": ["Geriatrics", "Ophthalmology","ENT",      "Rheumatology","Hematology"],
}

EQUIPMENT_LIST = [
    "Ventilator", "ECG Monitor", "Defibrillator", "CT Scanner",
    "MRI Machine", "Dialysis Unit", "Infusion Pump", "X-Ray Machine",
    "Ultrasound",  "Anesthesia Machine",
]

EQUIPMENT_STATUS_OPTIONS = ["Operational", "In Use", "Under Maintenance", "Offline"]
EQUIPMENT_STATUS_WEIGHTS = [0.50, 0.30, 0.12, 0.08]

# ─── Seed for reproducible "snapshot" within a session ────────────────────────

def _seed() -> int:
    """Return a seed that changes every 30 seconds so data 'updates' live."""
    return int(datetime.now().timestamp() // 30)


# ─── Bed Occupancy ────────────────────────────────────────────────────────────

def get_bed_data(branch: str | None = None) -> pd.DataFrame:
    """Return bed occupancy figures for every department across all (or one) branch."""
    rng = random.Random(_seed())
    rows = []
    branches = [branch] if branch and branch != "All" else BRANCHES
    for br in branches:
        for dept in DEPARTMENTS[br]:
            total    = rng.randint(20, 60)
            occupied = rng.randint(int(total * 0.40), int(total * 0.95))
            reserved = rng.randint(0, max(1, total - occupied - 2))
            available = total - occupied - reserved
            occupancy_pct = round(occupied / total * 100, 1)
            rows.append({
                "Branch":        br,
                "Department":    dept,
                "Total Beds":    total,
                "Occupied":      occupied,
                "Reserved":      reserved,
                "Available":     available,
                "Occupancy (%)": occupancy_pct,
                "Status":        _bed_status(occupancy_pct),
            })
    return pd.DataFrame(rows)


def _bed_status(pct: float) -> str:
    if pct >= 90:
        return "🔴 Critical"
    if pct >= 75:
        return "🟡 High"
    return "🟢 Normal"


# ─── ICU Availability ─────────────────────────────────────────────────────────

def get_icu_data(branch: str | None = None) -> pd.DataFrame:
    rng = random.Random(_seed() + 1)
    rows = []
    branches = [branch] if branch and branch != "All" else BRANCHES
    for br in branches:
        total    = rng.randint(8, 20)
        occupied = rng.randint(int(total * 0.50), int(total * 0.98))
        available = total - occupied
        ventilated = rng.randint(0, occupied)
        rows.append({
            "Branch":            br,
            "ICU Beds Total":    total,
            "ICU Occupied":      occupied,
            "ICU Available":     available,
            "Ventilated":        ventilated,
            "Occupancy (%)":     round(occupied / total * 100, 1),
            "Status":            _bed_status(round(occupied / total * 100, 1)),
        })
    return pd.DataFrame(rows)


# ─── Equipment Status ─────────────────────────────────────────────────────────

def get_equipment_data(branch: str | None = None) -> pd.DataFrame:
    rng = random.Random(_seed() + 2)
    rows = []
    branches = [branch] if branch and branch != "All" else BRANCHES
    for br in branches:
        for equip in EQUIPMENT_LIST:
            qty = rng.randint(2, 8)
            statuses = rng.choices(EQUIPMENT_STATUS_OPTIONS,
                                   weights=EQUIPMENT_STATUS_WEIGHTS, k=qty)
            for i, status in enumerate(statuses, start=1):
                last_checked = datetime.now() - timedelta(minutes=rng.randint(5, 180))
                rows.append({
                    "Branch":        br,
                    "Equipment":     equip,
                    "Unit #":        f"{equip[:3].upper()}-{i:02d}",
                    "Status":        status,
                    "Last Checked":  last_checked.strftime("%H:%M"),
                    "Department":    rng.choice(DEPARTMENTS[br]),
                })
    return pd.DataFrame(rows)


# ─── Historical Trend (last 24 hours, hourly) ─────────────────────────────────

def get_hourly_trend(branch: str | None = None) -> pd.DataFrame:
    """Simulated hourly bed-occupancy trend for the past 24 hours."""
    rng = np.random.default_rng(_seed() + 3)
    hours = [datetime.now() - timedelta(hours=h) for h in range(23, -1, -1)]
    labels = [h.strftime("%H:00") for h in hours]
    branches = [branch] if branch and branch != "All" else BRANCHES

    data = {"Hour": labels}
    for br in branches:
        base = rng.integers(55, 75)
        noise = rng.integers(-8, 8, size=24).cumsum()
        values = np.clip(base + noise, 40, 98).tolist()
        data[br] = values
    return pd.DataFrame(data)


# ─── KPI Summary ──────────────────────────────────────────────────────────────

def get_kpi_summary(branch: str | None = None) -> dict:
    bed_df   = get_bed_data(branch)
    icu_df   = get_icu_data(branch)
    equip_df = get_equipment_data(branch)

    total_beds       = int(bed_df["Total Beds"].sum())
    occupied_beds    = int(bed_df["Occupied"].sum())
    available_beds   = int(bed_df["Available"].sum())
    avg_occupancy    = round(bed_df["Occupancy (%)"].mean(), 1)

    icu_total        = int(icu_df["ICU Beds Total"].sum())
    icu_occupied     = int(icu_df["ICU Occupied"].sum())
    icu_available    = int(icu_df["ICU Available"].sum())

    op_equipment     = int((equip_df["Status"] == "Operational").sum())
    in_use_equip     = int((equip_df["Status"] == "In Use").sum())
    maint_equip      = int((equip_df["Status"] == "Under Maintenance").sum())
    offline_equip    = int((equip_df["Status"] == "Offline").sum())
    total_equip      = len(equip_df)

    critical_depts   = bed_df[bed_df["Status"] == "🔴 Critical"]["Department"].tolist()

    return {
        "total_beds":       total_beds,
        "occupied_beds":    occupied_beds,
        "available_beds":   available_beds,
        "avg_occupancy":    avg_occupancy,
        "icu_total":        icu_total,
        "icu_occupied":     icu_occupied,
        "icu_available":    icu_available,
        "icu_pct":          round(icu_occupied / max(icu_total, 1) * 100, 1),
        "op_equipment":     op_equipment,
        "in_use_equip":     in_use_equip,
        "maint_equip":      maint_equip,
        "offline_equip":    offline_equip,
        "total_equip":      total_equip,
        "critical_depts":   critical_depts,
        "last_updated":     datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
