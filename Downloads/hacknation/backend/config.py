"""Configuration for the Ferrari Supply Chain Agents system."""

import os

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

OPENAI_MODEL = "gpt-4o-mini"

HOST = "0.0.0.0"
PORT = 8000

FERRARI_ASSEMBLY_PLANT = {
    "name": "Ferrari Maranello Plant",
    "address": "Via Abetone Inferiore 4, 41053 Maranello MO, Italy",
    "city": "Maranello",
    "country": "IT",
    "lat": 44.5294,
    "lon": 10.8633,
}

BUDGET_CEILING_EUR = 500000
TRUST_THRESHOLD = 0.70
MIN_ESG_SCORE = 50
