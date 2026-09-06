"""Bed Occupancy page for the Hospital Dashboard."""

import streamlit as st
import pandas as pd
from utils.data_generator import get_bed_data, get_hourly_trend
from utils.charts import (
    bed_occupancy_bar,
    bed_stacked_bar,
    hourly_trend_line,
)


def render(branch: str):
    st.subheader("🛏️ Bed Occupancy Tracker")
    st.caption("Live bed utilization across all departments. Data refreshes every 30 seconds.")

    df = get_bed_data(branch)

    # ── Filters ───────────────────────────────────────────────────────────────
    col_f1, col_f2 = st.columns([2, 2])
    with col_f1:
        status_filter = st.multiselect(
            "Filter by Status",
            options=df["Status"].unique().tolist(),
            default=df["Status"].unique().tolist(),
            key="bed_status_filter",
        )
    with col_f2:
        if branch == "All":
            branch_filter = st.multiselect(
                "Filter by Branch",
                options=df["Branch"].unique().tolist(),
                default=df["Branch"].unique().tolist(),
                key="bed_branch_filter",
            )
        else:
            branch_filter = [branch]

    filtered = df[
        df["Status"].isin(status_filter) &
        df["Branch"].isin(branch_filter)
    ]

    if filtered.empty:
        st.warning("No data matches the selected filters.")
        return

    # ── Charts row ────────────────────────────────────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(bed_occupancy_bar(filtered), use_container_width=True)
    with col2:
        st.plotly_chart(bed_stacked_bar(filtered), use_container_width=True)

    # ── 24-hour trend ─────────────────────────────────────────────────────────
    st.markdown("#### 📈 24-Hour Occupancy Trend")
    trend_df = get_hourly_trend(branch)
    st.plotly_chart(hourly_trend_line(trend_df), use_container_width=True)

    # ── Detail table ──────────────────────────────────────────────────────────
    st.markdown("#### 📋 Department Detail")

    def _highlight_status(row):
        if "Critical" in row["Status"]:
            return ["background-color: rgba(239,68,68,0.15)"] * len(row)
        if "High" in row["Status"]:
            return ["background-color: rgba(245,158,11,0.12)"] * len(row)
        return [""] * len(row)

    styled = (
        filtered[["Branch", "Department", "Total Beds", "Occupied",
                   "Reserved", "Available", "Occupancy (%)", "Status"]]
        .sort_values("Occupancy (%)", ascending=False)
        .style
        .apply(_highlight_status, axis=1)
        .format({"Occupancy (%)": "{:.1f}%"})
    )
    st.dataframe(styled, use_container_width=True, hide_index=True)

    # ── Per-branch summary cards ──────────────────────────────────────────────
    if branch == "All":
        st.markdown("#### 🏢 Branch Summary")
        branch_summary = (
            filtered.groupby("Branch")
            .agg(
                Total_Beds=("Total Beds", "sum"),
                Occupied=("Occupied", "sum"),
                Available=("Available", "sum"),
                Avg_Occupancy=("Occupancy (%)", "mean"),
            )
            .reset_index()
        )
        cols = st.columns(len(branch_summary))
        for i, (_, row) in enumerate(branch_summary.iterrows()):
            with cols[i]:
                pct = round(row["Avg_Occupancy"], 1)
                status_icon = "🔴" if pct >= 90 else ("🟡" if pct >= 75 else "🟢")
                st.metric(
                    label=f"{status_icon} {row['Branch']}",
                    value=f"{pct}%",
                    delta=f"{int(row['Available'])} free beds",
                    delta_color="normal",
                )
