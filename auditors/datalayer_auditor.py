# DataLayer Quality Auditor
import json
from config import client, MODEL, MAX_TOKENS
from prompts import DATALAYER_AUDIT_PROMPT

def audit_datalayer(setup):
    """Audit dataLayer quality based on user's setup"""
    
    datalayer_data = setup.get("datalayer_sample", "")
    
    if not datalayer_data:
        datalayer_data = f"""No dataLayer sample provided.
        Based on a {setup['website_type']} in {setup['industry']} using {setup['platform']},
        provide a recommended dataLayer structure and flag what to watch for."""
    
    prompt = DATALAYER_AUDIT_PROMPT.format(
        website_type=setup["website_type"],
        datalayer_data=datalayer_data
    )
    
    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}]
    )
    
    response_text = response.content[0].text
    
    cleaned = response_text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        cleaned = "\n".join(lines[1:-1])
    
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {
            "findings": [{"issue": "Failed to parse dataLayer audit", "severity": "info",
                         "category": "config", "details": response_text,
                         "fix": "Re-run audit", "business_impact": "N/A"}],
            "score": 0,
            "summary": "Audit parsing failed — raw response saved in details"
        }