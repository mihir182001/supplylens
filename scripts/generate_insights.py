import json
import os
from dotenv import load_dotenv
import anthropic

load_dotenv()

MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-5")

SYSTEM_PROMPT = """You are a supply chain analyst producing a short, prescriptive
recommendation for a warehouse operations audience. You will be given a JSON
summary of fulfilment KPIs from a Brazilian e-commerce marketplace (Olist):
average delivery delay, percentage of late orders, number of anomalous
deliveries, the worst-performing sellers, and the worst-performing product
category or region. Region codes are Brazilian state abbreviations (e.g. AL
= Alagoas, SP = Sao Paulo, RJ = Rio de Janeiro) -- never assume US states.

Write 1-2 short paragraphs, plain English, no headers or bullet lists:
1. State the single biggest problem, citing the specific numbers given.
2. Name the most likely root cause based on which sellers/categories/regions are implicated.
3. Give one concrete, actionable recommendation.

Do not invent numbers that are not in the input. Be direct, like an analyst
who has already done the digging."""

def generate_recommendation(kpi_summary, model=MODEL):
    client = anthropic.Anthropic()
    message = client.messages.create(
        model=model,
        max_tokens=400,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": json.dumps(kpi_summary, default=str)}],
    )
    return "".join(block.text for block in message.content if block.type == "text")

if __name__ == "__main__":
    example_summary = {
        "avg_delay_days_negative_means_early": -6.7,
        "worst_region": "AL",
        "worst_region_late_rate_pct": 27,
        "worst_seller_id": "df683dfda87bf71ac3fc63063fba369d",
        "worst_seller_avg_delay_days": 167.71,
        "worst_category": "artes_e_artesanato",
        "anomaly_count": 3303,
        "anomaly_pct": 3.0,
    }
    print(generate_recommendation(example_summary))
