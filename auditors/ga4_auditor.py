# GA4 Event Coverage Auditor
import json
from config import client, MODEL, MAX_TOKENS
from prompts import GA4_AUDIT_PROMPT

def audit_ga4(setup):
    """Audit GA4 event coverage based on user's setup"""
    
    # Build context from what the user provided
    ga4_data = setup.get("ga4_events", "")
    
    if not ga4_data:
        # If no GA4 data pasted, use the setup info to do a general audit
        ga4_data = f"""No specific event list provided. 
        Audit based on:
        - Industry: {setup['industry']}
        - Website type: {setup['website_type']}
        - Platform: {setup['platform']}
        - Goals: {', '.join(setup['goals'])}
        
        Please recommend what events SHOULD exist and flag them as missing."""
    
    prompt = GA4_AUDIT_PROMPT.format(
        industry=setup["industry"],
        website_type=setup["website_type"],
        goals=", ".join(setup["goals"]),
        ga4_data=ga4_data
    )
    
    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}]
    )
    
    response_text = response.content[0].text
    
    # Clean markdown code blocks if present
    cleaned = response_text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        cleaned = "\n".join(lines[1:-1])
    
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {
            "findings": [{"issue": "Failed to parse GA4 audit", "severity": "info", 
                         "category": "config", "details": response_text,
                         "fix": "Re-run audit", "business_impact": "N/A"}],
            "score": 0,
            "summary": "Audit parsing failed — raw response saved in details"
        }