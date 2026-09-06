# 🏥 Hospital Resource Management Dashboard

An AI-powered, real-time hospital resource management dashboard built with **Streamlit** and **Google Gemini 1.5 Flash**.

---

## Features

| Module | Description |
|---|---|
| 🛏️ **Bed Occupancy** | Live occupancy %, stacked bed distribution, 24-hour trend, colour-coded alerts |
| 🏥 **ICU Availability** | Per-branch gauges, ventilator utilisation, comparison bar charts |
| 🔧 **Equipment Status** | Status pie chart, issues heatmap, per-type availability table, unit-level alerts |
| 🤖 **AI Assistant** | Chat with Gemini 1.5 Flash about any resource concern; one-click auto alert summary |
| 📊 **KPI Bar** | Global headline metrics: total beds, occupancy %, ICU stats, offline equipment count |
| 🔄 **Auto-Refresh** | Toggle 30-second live refresh from the sidebar |

---

## Project Structure

```
hospital_dashboard/
├── app.py                   ← Streamlit entry point
├── requirements.txt
├── .env.example             ← Copy to .env and fill in your key
├── pages/
│   ├── __init__.py
│   ├── bed_occupancy.py     ← Bed occupancy tab
│   ├── icu_status.py        ← ICU availability tab
│   ├── equipment.py         ← Equipment status tab
│   └── ai_assistant.py      ← Gemini AI chat tab
└── utils/
    ├── __init__.py
    ├── data_generator.py    ← Simulated real-time data (swap for real DB/API)
    ├── gemini_helper.py     ← Gemini 1.5 Flash integration
    └── charts.py            ← Reusable Plotly chart builders
```

---

## Quick Start

### 1. Clone / copy the project

```bash
cd hospital_dashboard
```

### 2. Create a virtual environment

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your Gemini API key

```bash
cp .env.example .env
# Open .env and set:
# GEMINI_API_KEY=your_actual_key_here
```

Get a free key at → [aistudio.google.com](https://aistudio.google.com)

> You can also paste the key directly in the dashboard sidebar without editing `.env`.

### 5. Run the dashboard

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## Deploying to Streamlit Community Cloud

1. Push this project folder to a GitHub repository.
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**.
3. Select the repo, set **Main file path** to `hospital_dashboard/app.py`.
4. Under **Secrets**, add:
   ```toml
   GEMINI_API_KEY = "your_actual_key_here"
   ```
5. Click **Deploy** — done!

---

## Swapping Simulated Data for Real Data

All data generation lives in [`utils/data_generator.py`](utils/data_generator.py).  
Replace the functions `get_bed_data()`, `get_icu_data()`, and `get_equipment_data()` with real database queries or REST API calls that return the same `pandas.DataFrame` schema, and the entire dashboard will work without any other changes.

---

## Tech Stack

| Library | Purpose |
|---|---|
| `streamlit` | UI framework and interactive widgets |
| `google-generativeai` | Gemini 1.5 Flash LLM |
| `plotly` | Interactive charts (bar, gauge, pie, heatmap, line) |
| `pandas` | Data manipulation |
| `numpy` | Numerical data simulation |
| `python-dotenv` | Secure API key loading |

---

## AI Capabilities

The **AI Assistant** tab provides:

- **One-click Operational Alert** — Gemini reads the live snapshot and writes a 3–5 sentence brief for the charge nurse or administrator.
- **Interactive Chat** — Ask anything: resource reallocation, contingency planning, staffing recommendations, risk analysis.
- **8 Suggested Question Chips** — Quick-fire prompts covering the most common operational scenarios.
- **Live Context Inspector** — Expand to see exactly what data snapshot is sent to Gemini.

---

*Built with ❤️ using IBM Bob · Gemini 1.5 Flash · Streamlit*
