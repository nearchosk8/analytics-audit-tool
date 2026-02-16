# GTM Container Health Auditor
import json
from config import client, MODEL, MAX_TOKENS
from prompts import GTM_AUDIT_PROMPT

def audit_gtm(setup):
    """Audit GTM container health based on user's setup"""
    
    gtm_data = setup.get("gtm_tags", "")
    
    if not gtm_data:
        gtm_data = f"""No specific GTM data provided.
        Based on a {setup['website_type']} in {setup['industry']},
        using {setup['platform']}, provide a general GTM health checklist
        and flag common issues for this type of setup."""
    
    prompt = GTM_AUDIT_PROMPT.format(gtm_data=gtm_data)
    
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
            "findings": [{"issue": "Failed to parse GTM audit", "severity": "info",
                         "category": "config", "details": response_text,
                         "fix": "Re-run audit", "business_impact": "N/A"}],
            "score": 0,
            "summary": "Audit parsing failed — raw response saved in details"
        }