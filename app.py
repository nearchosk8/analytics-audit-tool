import streamlit as st
import json
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import client, MODEL, MAX_TOKENS, SEVERITY
from prompts import GA4_AUDIT_PROMPT, GTM_AUDIT_PROMPT, DATALAYER_AUDIT_PROMPT

# --- Page Config ---
st.set_page_config(
    page_title="Analytics Tracking Audit Tool",
    page_icon="🔍",
    layout="wide"
)

# --- Custom CSS ---
st.markdown("""
<style>
    .main { padding-top: 1rem; }
    .stApp { background-color: #0f172a; }
    
    /* Header */
    .header-container {
        text-align: center;
        padding: 2rem 1rem;
        background: linear-gradient(135deg, #1e293b, #334155);
        border-radius: 16px;
        margin-bottom: 2rem;
        border: 1px solid #475569;
    }
    .header-title { 
        font-size: 2rem; 
        font-weight: 700; 
        color: #f8fafc;
        margin-bottom: 0.3rem;
    }
    .header-subtitle { color: #94a3b8; font-size: 1rem; }
    
    /* Score circle */
    .score-container { text-align: center; padding: 1.5rem 0; }
    .score-circle {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 130px;
        height: 130px;
        border-radius: 50%;
        font-size: 2.8rem;
        font-weight: 800;
    }
    .score-label { color: #94a3b8; font-size: 0.9rem; margin-top: 0.5rem; }
    
    /* Finding cards */
    .finding-card {
        background: #1e293b;
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 0.75rem;
        border: 1px solid #334155;
    }
    .finding-title {
        font-weight: 600;
        font-size: 1rem;
        color: #f1f5f9;
        margin-bottom: 0.5rem;
    }
    .finding-detail {
        font-size: 0.85rem;
        color: #94a3b8;
        margin-bottom: 0.3rem;
    }
    .finding-fix {
        font-size: 0.85rem;
        color: #60a5fa;
        margin-top: 0.5rem;
    }
    
    /* Severity badges */
    .badge {
        display: inline-block;
        padding: 0.15rem 0.5rem;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: 700;
        color: white;
        margin-left: 0.5rem;
    }
    .badge-critical { background: #ef4444; }
    .badge-high { background: #f97316; }
    .badge-medium { background: #f59e0b; }
    .badge-low { background: #22c55e; }
    .badge-info { background: #6b7280; }
    
    /* Section headers */
    .section-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    
    /* Action items */
    .action-item {
        background: #1e293b;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.5rem;
        border-left: 3px solid #ef4444;
    }
    .action-title { font-weight: 600; color: #f1f5f9; font-size: 0.95rem; }
    .action-fix { color: #60a5fa; font-size: 0.85rem; margin-top: 0.3rem; }
    
    /* Hide Streamlit defaults */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    .stDeployButton { display: none; }
</style>
""", unsafe_allow_html=True)


# --- Helper Functions ---
def run_audit(prompt, data_dict):
    """Run a single audit and return parsed results"""
    formatted_prompt = prompt.format(**data_dict)
    
    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": formatted_prompt}]
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
            "findings": [{"issue": "Audit parsing failed", "severity": "info",
                         "category": "error", "details": response_text[:500],
                         "fix": "Try running again", "business_impact": "N/A"}],
            "score": 0,
            "summary": "Could not parse audit results"
        }


def get_score_color(score):
    if score >= 70:
        return "#22c55e"
    elif score >= 40:
        return "#f59e0b"
    return "#ef4444"


def render_findings(findings):
    """Render finding cards"""
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
    findings.sort(key=lambda x: severity_order.get(x.get("severity", "info"), 5))
    
    for i, finding in enumerate(findings, 1):
        sev = finding.get("severity", "info")
        badge_class = f"badge-{sev}"
        
        st.markdown(f"""
        <div class="finding-card">
            <div class="finding-title">
                #{i} {finding.get('issue', 'N/A')}
                <span class="badge {badge_class}">{sev.upper()}</span>
            </div>
            <div class="finding-detail"><strong>Category:</strong> {finding.get('category', 'N/A')}</div>
            <div class="finding-detail"><strong>Details:</strong> {finding.get('details', 'N/A')}</div>
            <div class="finding-fix"><strong>How to Fix:</strong> {finding.get('fix', 'N/A')}</div>
            <div class="finding-detail" style="margin-top: 0.3rem;"><strong>Business Impact:</strong> {finding.get('business_impact', 'N/A')}</div>
        </div>
        """, unsafe_allow_html=True)


# --- App Layout ---

# Header
st.markdown("""
<div class="header-container">
    <div class="header-title">🔍 Analytics Tracking Audit Tool</div>
    <div class="header-subtitle">Powered by Claude AI — Audit your GA4, GTM, and DataLayer implementation</div>
</div>
""", unsafe_allow_html=True)

# --- Sidebar: Intake Form ---
with st.sidebar:
    st.header("📋 Setup Details")
    st.caption("Tell us about your tracking implementation")
    
    industry = st.selectbox("Industry", [
        "E-commerce / Retail",
        "SaaS / Software",
        "Lead Generation / B2B",
        "Media / Publishing",
        "Travel / Hospitality",
        "Other"
    ])
    
    if industry == "Other":
        industry = st.text_input("Specify industry")
    
    website_type = st.selectbox("Website Type", [
        "E-commerce store",
        "Multi-page website with forms",
        "Single product / landing page",
        "Web application (SaaS)",
        "Content / blog site"
    ])
    
    platform = st.text_input("Platform", placeholder="e.g. Shopify, WordPress, React")
    
    goals = st.multiselect("Analytics Goals", [
        "Track conversions / purchases",
        "Understand user journey / funnel",
        "Measure marketing campaign performance",
        "Track engagement / content performance",
        "Generate leads / form submissions"
    ])
    
    st.divider()
    st.header("📎 Paste Config Data")
    st.caption("Optional — improves audit accuracy")
    
    ga4_events = st.text_area("GA4 Events List", height=120, 
                              placeholder="Paste from GA4 > Admin > Events\nor your measurement plan...")
    
    gtm_tags = st.text_area("GTM Tags List", height=120,
                            placeholder="Paste from GTM > Tags overview\nor describe your tags...")
    
    datalayer_sample = st.text_area("DataLayer Sample", height=120,
                                    placeholder="Paste from browser console:\nJSON.stringify(dataLayer, null, 2)")
    
    st.divider()
    run_audit_btn = st.button("🚀 Run Audit", type="primary", use_container_width=True)

# --- Main Content ---
if run_audit_btn:
    if not platform:
        st.warning("Please enter your platform to continue.")
    elif not goals:
        st.warning("Please select at least one analytics goal.")
    else:
        # Build setup dict
        setup = {
            "industry": industry,
            "website_type": website_type,
            "platform": platform,
            "goals": goals,
            "ga4_events": ga4_events,
            "gtm_tags": gtm_tags,
            "datalayer_sample": datalayer_sample
        }
        
        # Run audits with progress
        progress = st.progress(0, text="Starting audit...")
        
        # GA4 Audit
        progress.progress(10, text="🔵 Auditing GA4 event coverage...")
        ga4_data = ga4_events if ga4_events else f"No specific event list provided. Industry: {industry}, Type: {website_type}, Platform: {platform}, Goals: {', '.join(goals)}. Recommend what events SHOULD exist."
        ga4_results = run_audit(GA4_AUDIT_PROMPT, {
            "industry": industry,
            "website_type": website_type,
            "goals": ", ".join(goals),
            "ga4_data": ga4_data
        })
        
        # GTM Audit
        progress.progress(40, text="🟠 Auditing GTM container health...")
        gtm_data = gtm_tags if gtm_tags else f"No specific GTM data provided. Setup: {website_type} in {industry} using {platform}. Provide general GTM health checklist."
        gtm_results = run_audit(GTM_AUDIT_PROMPT, {"gtm_data": gtm_data})
        
        # DataLayer Audit
        progress.progress(70, text="🟣 Auditing dataLayer quality...")
        dl_data = datalayer_sample if datalayer_sample else f"No dataLayer sample provided. Setup: {website_type} in {industry} using {platform}. Recommend dataLayer structure."
        datalayer_results = run_audit(DATALAYER_AUDIT_PROMPT, {
            "website_type": website_type,
            "datalayer_data": dl_data
        })
        
        progress.progress(100, text="✅ Audit complete!")
        
        # Store results in session state
        st.session_state.results = {
            "ga4": ga4_results,
            "gtm": gtm_results,
            "datalayer": datalayer_results,
            "setup": setup
        }

# --- Display Results ---
if "results" in st.session_state:
    results = st.session_state.results
    ga4_results = results["ga4"]
    gtm_results = results["gtm"]
    datalayer_results = results["datalayer"]
    
    scores = {
        "GA4 Events": ga4_results.get("score", 0),
        "GTM Health": gtm_results.get("score", 0),
        "DataLayer": datalayer_results.get("score", 0)
    }
    overall = round(sum(scores.values()) / len(scores))
    score_color = get_score_color(overall)
    
    # Overall Score
    st.markdown(f"""
    <div class="score-container">
        <div class="score-circle" style="border: 6px solid {score_color}; color: {score_color};">
            {overall}
        </div>
        <div class="score-label">Overall Score out of 100</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Score cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🔵 GA4 Events", f"{scores['GA4 Events']}/100")
    with col2:
        st.metric("🟠 GTM Health", f"{scores['GTM Health']}/100")
    with col3:
        st.metric("🟣 DataLayer", f"{scores['DataLayer']}/100")
    
    st.divider()
    
    # Audit sections in tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔵 GA4 Events", 
        "🟠 GTM Health", 
        "🟣 DataLayer",
        "🎯 Priority Actions"
    ])
    
    with tab1:
        st.subheader(f"GA4 Event Coverage — {ga4_results.get('score', 0)}/100")
        st.caption(ga4_results.get("summary", ""))
        st.progress(ga4_results.get("score", 0) / 100)
        render_findings(ga4_results.get("findings", []))
    
    with tab2:
        st.subheader(f"GTM Container Health — {gtm_results.get('score', 0)}/100")
        st.caption(gtm_results.get("summary", ""))
        st.progress(gtm_results.get("score", 0) / 100)
        render_findings(gtm_results.get("findings", []))
    
    with tab3:
        st.subheader(f"DataLayer Quality — {datalayer_results.get('score', 0)}/100")
        st.caption(datalayer_results.get("summary", ""))
        st.progress(datalayer_results.get("score", 0) / 100)
        render_findings(datalayer_results.get("findings", []))
    
    with tab4:
        st.subheader("Priority Action Items")
        st.caption("Critical and high severity issues that need immediate attention")
        
        all_findings = (
            ga4_results.get("findings", []) +
            gtm_results.get("findings", []) +
            datalayer_results.get("findings", [])
        )
        critical_high = [f for f in all_findings if f.get("severity") in ("critical", "high")]
        critical_high.sort(key=lambda x: 0 if x.get("severity") == "critical" else 1)
        
        if critical_high:
            for i, item in enumerate(critical_high, 1):
                sev = item.get("severity", "info")
                border_color = "#ef4444" if sev == "critical" else "#f97316"
                st.markdown(f"""
                <div class="action-item" style="border-left-color: {border_color}">
                    <div class="action-title">{i}. {item.get('issue', 'N/A')}</div>
                    <div class="action-fix">→ {item.get('fix', 'N/A')}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("No critical or high severity issues found!")
    
    # Download HTML report
    st.divider()
    
    from export_html import export_report
    filepath = export_report(ga4_results, gtm_results, datalayer_results, results["setup"])
    
    with open(filepath, 'r') as f:
        html_content = f.read()
    
    st.download_button(
        label="📄 Download Full HTML Report",
        data=html_content,
        file_name="analytics-audit-report.html",
        mime="text/html",
        use_container_width=True
    )
    
    # Cleanup the generated file
    os.remove(filepath)

else:
    # Empty state
    st.markdown("""
    <div style="text-align: center; padding: 4rem 2rem; color: #64748b;">
        <p style="font-size: 3rem; margin-bottom: 1rem;">👈</p>
        <p style="font-size: 1.1rem;">Fill in your setup details in the sidebar and click <strong>Run Audit</strong></p>
        <p style="font-size: 0.9rem; margin-top: 1rem;">The tool will analyze your GA4 events, GTM container, and dataLayer implementation</p>
    </div>
    """, unsafe_allow_html=True)