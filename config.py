# Analytics Audit Tool - Configuration
import os
import anthropic

# Try Streamlit secrets first (for cloud deployment), fall back to env var
try:
    import streamlit as st
    api_key = st.secrets.get("ANTHROPIC_API_KEY", None)
except Exception:
    api_key = None

if not api_key:
    api_key = os.environ.get("ANTHROPIC_API_KEY")

# Claude client
client = anthropic.Anthropic(api_key=api_key)

# Model settings
MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 4096

# Audit categories
AUDIT_CATEGORIES = ["ga4_events", "gtm_health", "datalayer_quality"]

# Severity levels
SEVERITY = {
    "critical": "🔴",
    "high": "🟠",
    "medium": "🟡",
    "low": "🟢",
    "info": "ℹ️"
}