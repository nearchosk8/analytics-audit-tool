# Synthesizer - combines all audit results into a strategic action plan
import json
from config import client, MODEL, MAX_TOKENS
from prompts import SYNTHESIS_PROMPT


def synthesize_results(ga4_results, gtm_results, datalayer_results, setup):
    """Generate a strategic synthesis of all audit findings"""
    
    def get_critical_high(findings):
        items = [f for f in findings if f.get("severity") in ("critical", "high")]
        return "; ".join([f.get("issue", "") for f in items]) or "None"
    
    prompt = SYNTHESIS_PROMPT.format(
        industry=setup.get("industry", "N/A"),
        website_type=setup.get("website_type", "N/A"),
        platform=setup.get("platform", "N/A"),
        goals=", ".join(setup.get("goals", [])),
        ga4_score=ga4_results.get("score", 0),
        ga4_summary=ga4_results.get("summary", "N/A"),
        ga4_critical=get_critical_high(ga4_results.get("findings", [])),
        gtm_score=gtm_results.get("score", 0),
        gtm_summary=gtm_results.get("summary", "N/A"),
        gtm_critical=get_critical_high(gtm_results.get("findings", [])),
        datalayer_score=datalayer_results.get("score", 0),
        datalayer_summary=datalayer_results.get("summary", "N/A"),
        datalayer_critical=get_critical_high(datalayer_results.get("findings", []))
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
            "executive_summary": "Could not generate synthesis. Please review individual audit sections.",
            "overall_health": "needs_attention",
            "immediate_actions": [],
            "30_day_plan": "Review individual audit findings.",
            "90_day_plan": "Implement all recommended fixes.",
            "estimated_data_quality_improvement": "N/A",
            "risks_of_inaction": "N/A"
        }