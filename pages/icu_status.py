"""ICU Availability page for the Hospital Dashboard."""

import streamlit as st
import pandas as pd
from utils.data_generator import get_icu_data
from utils.charts import icu_gauge, icu_comparison_bar


def render(branch: str):
    st.subheader("🏥 ICU Availability Monitor")
    st.caption("Real-time intensive care unit capacity and ventilator usage across all branches.")

    df = get_icu_data(branch)

    # ── Top-level ICU metrics ────────────────────────────────────────────────
    total_icu      = int(df["ICU Beds Total"].sum())
    total_occupied = int(df["ICU Occupied"].sum())
    total_avail    = int(df["ICU Available"].sum())
    total_vent     = int(df["Ventilated"].sum())
    overall_pct    = round(total_occupied / max(total_icu, 1) * 100, 1)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🏥 Total ICU Beds",   total_icu)
    col2.metric("🔴 Occupied",          total_occupied,
                delta=f"{overall_pct}%", delta_color="inverse")
    col3.metric("🟢 Available",          total_avail)
    col4.metric("💨 On Ventilator",      total_vent)

    st.markdown("---")

    # ── Gauges per branch ────────────────────────────────────────────────────
    st.markdown("#### 🎯 ICU Occupancy Gauges by Branch")
    gauge_cols = st.columns(len(df))
    for i, (_, row) in enumerate(df.iterrows()):
        with gauge_cols[i]:
            st.plotly_chart(
                icu_gauge(row["Occupancy (%)"], row["Branch"]),
                use_container_width=True,
            )

    # ── Comparison bar chart ─────────────────────────────────────────────────
    st.markdown("#### 📊 ICU Capacity Comparison")
    st.plotly_chart(icu_comparison_bar(df), use_container_width=True)

    # ── Ventilator utilisation progress bars ─────────────────────────────────
    st.markdown("#### 💨 Ventilator Utilisation by Branch")
    for _, row in df.iterrows():
        vent_pct = int(row["Ventilated"] / max(row["ICU Occupied"], 1) * 100)
        label = (
            f"**{row['Branch']}** — "
            f"{int(row['Ventilated'])} of {int(row['ICU Occupied'])} occupied beds ventilated"
        )
        st.markdown(label)
        st.progress(vent_pct / 100)

    st.markdown("---")

    # ── Detail table ─────────────────────────────────────────────────────────
    st.markdown("#### 📋 ICU Data Table")

    def _highlight(row):
        if "Critical" in row["Status"]:
            return ["background-color: rgba(239,68,68,0.15)"] * len(row)
        if "High" in row["Status"]:
            return ["background-color: rgba(245,158,11,0.12)"] * len(row)
        return [""] * len(row)

    styled = (
        df.style
        .apply(_highlight, axis=1)
        .format({"Occupancy (%)": "{:.1f}%"})
    )
    st.dataframe(styled, use_container_width=True, hide_index=True)

    # ── Alert cards for critical branches ────────────────────────────────────
    critical = df[df["Occupancy (%)"] >= 90]
    if not critical.empty:
        st.markdown("#### 🚨 Critical ICU Alerts")
        for _, row in critical.iterrows():
            st.error(
                f"🔴 **{row['Branch']}**: ICU at **{row['Occupancy (%)']}%** — "
                f"Only **{int(row['ICU Available'])}** bed(s) remaining. "
                f"Immediate action required."
            )
    else:
        st.success("✅ All branches have ICU availability within acceptable thresholds.")
