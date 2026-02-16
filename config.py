# Analytics Audit Tool - Configuration
import anthropic

# Claude client (reads ANTHROPIC_API_KEY from environment)
client = anthropic.Anthropic()

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