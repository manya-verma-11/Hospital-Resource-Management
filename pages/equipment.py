"""Critical Equipment Status page for the Hospital Dashboard."""

import streamlit as st
import pandas as pd
from utils.data_generator import get_equipment_data, EQUIPMENT_LIST
from utils.charts import equipment_pie, equipment_heatmap


_STATUS_ICON = {
    "Operational":       "🟢",
    "In Use":            "🔵",
    "Under Maintenance": "🟡",
    "Offline":           "🔴",
}


def render(branch: str):
    st.subheader("🔧 Critical Equipment Status")
    st.caption("Real-time availability of life-critical hospital equipment across all branches.")

    df = get_equipment_data(branch)

    # ── Top-level equipment KPIs ─────────────────────────────────────────────
    total     = len(df)
    op        = int((df["Status"] == "Operational").sum())
    in_use    = int((df["Status"] == "In Use").sum())
    maint     = int((df["Status"] == "Under Maintenance").sum())
    offline   = int((df["Status"] == "Offline").sum())
    avail_pct = round((op + in_use) / max(total, 1) * 100, 1)

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("🔧 Total Units",        total)
    col2.metric("🟢 Operational",        op)
    col3.metric("🔵 In Use",             in_use)
    col4.metric("🟡 Under Maintenance",  maint,
                delta=f"-{maint} unavailable", delta_color="inverse")
    col5.metric("🔴 Offline",            offline,
                delta=f"⚠️ Critical" if offline > 3 else "Within threshold",
                delta_color="inverse" if offline > 3 else "off")

    st.markdown("---")

    # ── Filters ───────────────────────────────────────────────────────────────
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        equip_filter = st.multiselect(
            "Equipment Type",
            options=sorted(df["Equipment"].unique()),
            default=sorted(df["Equipment"].unique()),
            key="equip_type_filter",
        )
    with col_f2:
        status_filter = st.multiselect(
            "Status",
            options=df["Status"].unique().tolist(),
            default=df["Status"].unique().tolist(),
            key="equip_status_filter",
        )
    with col_f3:
        if branch == "All":
            branch_filter = st.multiselect(
                "Branch",
                options=df["Branch"].unique().tolist(),
                default=df["Branch"].unique().tolist(),
                key="equip_branch_filter",
            )
        else:
            branch_filter = [branch]

    filtered = df[
        df["Equipment"].isin(equip_filter) &
        df["Status"].isin(status_filter) &
        df["Branch"].isin(branch_filter)
    ]

    if filtered.empty:
        st.warning("No equipment matches the selected filters.")
        return

    # ── Charts ────────────────────────────────────────────────────────────────
    col1, col2 = st.columns([1, 2])
    with col1:
        st.plotly_chart(equipment_pie(filtered), use_container_width=True)
    with col2:
        st.plotly_chart(equipment_heatmap(df), use_container_width=True)

    # ── Equipment availability per type ──────────────────────────────────────
    st.markdown("#### 📊 Availability by Equipment Type")
    avail_by_type = (
        filtered.groupby(["Equipment", "Status"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )
    # Ensure all status columns exist
    for col in ["Operational", "In Use", "Under Maintenance", "Offline"]:
        if col not in avail_by_type.columns:
            avail_by_type[col] = 0

    avail_by_type["Total"] = (
        avail_by_type["Operational"] +
        avail_by_type["In Use"] +
        avail_by_type.get("Under Maintenance", pd.Series([0]*len(avail_by_type))).values +
        avail_by_type["Offline"]
    )
    avail_by_type["Available (%)"] = (
        (avail_by_type["Operational"] + avail_by_type["In Use"])
        / avail_by_type["Total"].replace(0, 1)
        * 100
    ).round(1)

    def _highlight_avail(row):
        styles = [""] * len(row)
        col_names = list(row.index)
        if "Available (%)" in col_names:
            pct = row["Available (%)"]
            color = (
                "rgba(239,68,68,0.20)" if pct < 50 else
                "rgba(245,158,11,0.15)" if pct < 80 else
                "rgba(34,197,94,0.15)"
            )
            styles[col_names.index("Available (%)")] = f"background-color: {color}"
        if "Offline" in col_names:
            offline_val = row["Offline"]
            if offline_val >= 3:
                styles[col_names.index("Offline")] = "background-color: rgba(239,68,68,0.20)"
            elif offline_val >= 1:
                styles[col_names.index("Offline")] = "background-color: rgba(245,158,11,0.15)"
        return styles

    styled_avail = (
        avail_by_type.style
        .apply(_highlight_avail, axis=1)
        .format({"Available (%)": "{:.1f}%"})
    )
    st.dataframe(styled_avail, use_container_width=True, hide_index=True)

    # ── Offline / Maintenance alert list ──────────────────────────────────────
    problem_units = filtered[filtered["Status"].isin(["Offline", "Under Maintenance"])]
    if not problem_units.empty:
        st.markdown("#### 🚨 Units Requiring Attention")
        for _, row in problem_units.iterrows():
            icon = _STATUS_ICON.get(row["Status"], "⚪")
            st.warning(
                f"{icon} **{row['Unit #']}** ({row['Equipment']}) — "
                f"**{row['Status']}** | Branch: {row['Branch']} | "
                f"Department: {row['Department']} | Last checked: {row['Last Checked']}"
            )
    else:
        st.success("✅ All filtered equipment units are currently operational or in use.")

    # ── Full data table ───────────────────────────────────────────────────────
    with st.expander("📋 Full Equipment Data Table", expanded=False):
        def _highlight_equip(row):
            if row["Status"] == "Offline":
                return ["background-color: rgba(239,68,68,0.15)"] * len(row)
            if row["Status"] == "Under Maintenance":
                return ["background-color: rgba(245,158,11,0.12)"] * len(row)
            return [""] * len(row)

        styled_full = (
            filtered.sort_values(["Status", "Branch", "Equipment"])
            .style
            .apply(_highlight_equip, axis=1)
        )
        st.dataframe(styled_full, use_container_width=True, hide_index=True)
