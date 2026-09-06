import sys
from pathlib import Path
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parent))
from scripts.generate_insights import generate_recommendation

st.set_page_config(page_title="SupplyLens", layout="centered")
st.title("SupplyLens ? AI Fulfilment Insights")
st.caption("Enter KPI numbers from your Looker Studio dashboard to get an AI-generated recommendation.")

with st.form("insight_form"):
    avg_delay = st.number_input("Network avg delay (days, negative = early)", value=-6.7)
    worst_region = st.text_input("Worst region code", value="AL")
    worst_region_late_rate = st.number_input("Worst region late rate (%)", value=27.0)
    worst_seller_id = st.text_input("Worst seller ID", value="df683dfda87bf71ac3fc63063fba369d")
    worst_seller_delay = st.number_input("Worst seller avg delay (days)", value=167.71)
    worst_category = st.text_input("Worst category", value="artes_e_artesanato")
    anomaly_count = st.number_input("Anomaly count", value=3303, step=1)
    anomaly_pct = st.number_input("Anomaly percentage", value=3.0)
    submitted = st.form_submit_button("Generate recommendation")

if submitted:
    kpi_summary = {
        "avg_delay_days_negative_means_early": avg_delay,
        "worst_region": worst_region,
        "worst_region_late_rate_pct": worst_region_late_rate,
        "worst_seller_id": worst_seller_id,
        "worst_seller_avg_delay_days": worst_seller_delay,
        "worst_category": worst_category,
        "anomaly_count": int(anomaly_count),
        "anomaly_pct": anomaly_pct,
    }
    with st.spinner("Calling Claude..."):
        try:
            text = generate_recommendation(kpi_summary)
            st.success(text)
        except Exception as e:
            st.error(f"Something went wrong: {e}")
