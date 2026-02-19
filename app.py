import streamlit as st
import json
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import client, MODEL, MAX_TOKENS, SEVERITY
from prompts import GA4_AUDIT_PROMPT, GTM_AUDIT_PROMPT, DATALAYER_AUDIT_PROMPT
from synthesizer import synthesize_results

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
    
    .header-container {
        text-align: center;
        padding: 2rem 1rem;
        background: linear-gradient(135deg, #1e293b, #334155);
        border-radius: 16px;
        margin-bottom: 2rem;
        border: 1px solid #475569;
    }
    .header-title { font-size: 2rem; font-weight: 700; color: #f8fafc; margin-bottom: 0.3rem; }
    .header-subtitle { color: #94a3b8; font-size: 1rem; }
    
    .score-container { text-align: center; padding: 1.5rem 0; }
    .score-circle {
        display: inline-flex; align-items: center; justify-content: center;
        width: 130px; height: 130px; border-radius: 50%;
        font-size: 2.8rem; font-weight: 800;
    }
    .score-label { color: #94a3b8; font-size: 0.9rem; margin-top: 0.5rem; }
    
    .finding-card {
        background: #1e293b; border-radius: 12px; padding: 1.2rem;
        margin-bottom: 0.75rem; border: 1px solid #334155;
    }
    .finding-title { font-weight: 600; font-size: 1rem; color: #f1f5f9; margin-bottom: 0.5rem; }
    .finding-detail { font-size: 0.85rem; color: #94a3b8; margin-bottom: 0.3rem; }
    .finding-fix { font-size: 0.85rem; color: #60a5fa; margin-top: 0.5rem; }
    
    .badge {
        display: inline-block; padding: 0.15rem 0.5rem; border-radius: 4px;
        font-size: 0.7rem; font-weight: 700; color: white; margin-left: 0.5rem;
    }
    .badge-critical { background: #ef4444; }
    .badge-high { background: #f97316; }
    .badge-medium { background: #f59e0b; }
    .badge-low { background: #22c55e; }
    .badge-info { background: #6b7280; }
    
    .action-item {
        background: #1e293b; border-radius: 10px; padding: 1rem 1.2rem;
        margin-bottom: 0.5rem; border-left: 3px solid #ef4444;
    }
    .action-title { font-weight: 600; color: #f1f5f9; font-size: 0.95rem; }
    .action-fix { color: #60a5fa; font-size: 0.85rem; margin-top: 0.3rem; }
    
    .strategy-card {
        background: #1e293b; border-radius: 12px; padding: 1.5rem;
        margin-bottom: 1rem; border: 1px solid #334155;
    }
    .strategy-title { font-weight: 700; font-size: 1.1rem; color: #f8fafc; margin-bottom: 0.75rem; }
    .strategy-text { font-size: 0.9rem; color: #cbd5e1; line-height: 1.7; }
    
    .health-badge {
        display: inline-block; padding: 0.3rem 1rem; border-radius: 20px;
        font-weight: 700; font-size: 0.85rem; color: white; margin-bottom: 1rem;
    }
    
    .timeline-item {
        background: #0f172a; border-radius: 10px; padding: 1rem 1.2rem;
        margin-bottom: 0.5rem; border-left: 3px solid #3b82f6;
    }
    .timeline-action { font-weight: 600; color: #f1f5f9; font-size: 0.9rem; }
    .timeline-why { color: #94a3b8; font-size: 0.85rem; margin-top: 0.2rem; }
    .timeline-meta { color: #64748b; font-size: 0.8rem; margin-top: 0.3rem; }
    
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    .stDeployButton { display: none; }
</style>
""", unsafe_allow_html=True)


# --- Helper Functions ---
def run_audit(prompt, data_dict):
    formatted_prompt = prompt.format(**data_dict)
    response = client.messages.create(
        model=MODEL, max_tokens=MAX_TOKENS,
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
            "score": 0, "summary": "Could not parse audit results"
        }


def get_score_color(score):
    if score >= 70: return "#22c55e"
    elif score >= 40: return "#f59e0b"
    return "#ef4444"


def get_health_color(health):
    colors = {
        "critical": "#ef4444", "needs_attention": "#f97316",
        "fair": "#f59e0b", "good": "#22c55e", "excellent": "#10b981"
    }
    return colors.get(health, "#6b7280")


def render_findings(findings):
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


def save_audit_history(results, synthesis):
    """Save audit results as JSON for historical comparison"""
    history_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audit_history")
    os.makedirs(history_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"audit-{timestamp}.json"
    filepath = os.path.join(history_dir, filename)
    
    history_entry = {
        "timestamp": datetime.now().isoformat(),
        "setup": results["setup"],
        "scores": {
            "overall": round((results["ga4"].get("score", 0) + results["gtm"].get("score", 0) + results["datalayer"].get("score", 0)) / 3),
            "ga4": results["ga4"].get("score", 0),
            "gtm": results["gtm"].get("score", 0),
            "datalayer": results["datalayer"].get("score", 0)
        },
        "total_findings": (
            len(results["ga4"].get("findings", [])) +
            len(results["gtm"].get("findings", [])) +
            len(results["datalayer"].get("findings", []))
        ),
        "synthesis": synthesis,
        "full_results": {
            "ga4": results["ga4"],
            "gtm": results["gtm"],
            "datalayer": results["datalayer"]
        }
    }
    
    with open(filepath, 'w') as f:
        json.dump(history_entry, f, indent=2)
    
    return filepath


# --- App Layout ---

st.markdown("""
<div class="header-container">
    <div class="header-title">🔍 Analytics Tracking Audit Tool</div>
    <div class="header-subtitle">Powered by Claude AI — Audit your GA4, GTM, and DataLayer implementation</div>
</div>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.header("📋 Setup Details")
    st.caption("Tell us about your tracking implementation")
    
    industry = st.selectbox("Industry", [
        "E-commerce / Retail", "SaaS / Software", "Lead Generation / B2B",
        "Media / Publishing", "Travel / Hospitality", "Other"
    ])
    if industry == "Other":
        industry = st.text_input("Specify industry")
    
    website_type = st.selectbox("Website Type", [
        "E-commerce store", "Multi-page website with forms",
        "Single product / landing page", "Web application (SaaS)", "Content / blog site"
    ])
    
    platform = st.text_input("Platform", placeholder="e.g. Shopify, WordPress, React")
    
    goals = st.multiselect("Analytics Goals", [
        "Track conversions / purchases", "Understand user journey / funnel",
        "Measure marketing campaign performance", "Track engagement / content performance",
        "Generate leads / form submissions"
    ])
    
    st.divider()
    st.header("📎 Paste Config Data")
    st.caption("Optional — improves audit accuracy")
    
    ga4_events = st.text_area("GA4 Events List", height=120,
                              placeholder="Paste from GA4 > Admin > Events...")
    gtm_tags = st.text_area("GTM Tags List", height=120,
                            placeholder="Paste from GTM > Tags overview...")
    datalayer_sample = st.text_area("DataLayer Sample", height=120,
                                    placeholder="Paste from console:\nJSON.stringify(dataLayer, null, 2)")
    
    st.divider()
    run_audit_btn = st.button("🚀 Run Audit", type="primary", use_container_width=True)

# --- Main Content ---
if run_audit_btn:
    if not platform:
        st.warning("Please enter your platform to continue.")
    elif not goals:
        st.warning("Please select at least one analytics goal.")
    else:
        setup = {
            "industry": industry, "website_type": website_type,
            "platform": platform, "goals": goals,
            "ga4_events": ga4_events, "gtm_tags": gtm_tags,
            "datalayer_sample": datalayer_sample
        }
        
        progress = st.progress(0, text="Starting audit...")
        
        # GA4 Audit
        progress.progress(10, text="🔵 Auditing GA4 event coverage...")
        ga4_data = ga4_events if ga4_events else f"No specific event list provided. Industry: {industry}, Type: {website_type}, Platform: {platform}, Goals: {', '.join(goals)}. Recommend what events SHOULD exist."
        ga4_results = run_audit(GA4_AUDIT_PROMPT, {
            "industry": industry, "website_type": website_type,
            "goals": ", ".join(goals), "ga4_data": ga4_data
        })
        
        # GTM Audit
        progress.progress(35, text="🟠 Auditing GTM container health...")
        gtm_data = gtm_tags if gtm_tags else f"No specific GTM data provided. Setup: {website_type} in {industry} using {platform}. Provide general GTM health checklist."
        gtm_results = run_audit(GTM_AUDIT_PROMPT, {"gtm_data": gtm_data})
        
        # DataLayer Audit
        progress.progress(60, text="🟣 Auditing dataLayer quality...")
        dl_data = datalayer_sample if datalayer_sample else f"No dataLayer sample provided. Setup: {website_type} in {industry} using {platform}. Recommend dataLayer structure."
        datalayer_results = run_audit(DATALAYER_AUDIT_PROMPT, {
            "website_type": website_type, "datalayer_data": dl_data
        })
        
        # Synthesis
        progress.progress(85, text="🧠 Generating strategic recommendations...")
        synthesis = synthesize_results(ga4_results, gtm_results, datalayer_results, setup)
        
        progress.progress(100, text="✅ Audit complete!")
        
        # Save to session state
        st.session_state.results = {
            "ga4": ga4_results, "gtm": gtm_results,
            "datalayer": datalayer_results, "setup": setup
        }
        st.session_state.synthesis = synthesis
        
        # Save history
        try:
            save_audit_history(st.session_state.results, synthesis)
        except Exception:
            pass  # Don't break the app if history save fails

# --- Display Results ---
if "results" in st.session_state:
    results = st.session_state.results
    ga4_results = results["ga4"]
    gtm_results = results["gtm"]
    datalayer_results = results["datalayer"]
    synthesis = st.session_state.get("synthesis", {})
    
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
        <div class="score-circle" style="border: 6px solid {score_color}; color: {score_color};">{overall}</div>
        <div class="score-label">Overall Score out of 100</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Score cards
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("🔵 GA4 Events", f"{scores['GA4 Events']}/100")
    with col2: st.metric("🟠 GTM Health", f"{scores['GTM Health']}/100")
    with col3: st.metric("🟣 DataLayer", f"{scores['DataLayer']}/100")
    
    st.divider()
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🧠 Strategy", "🔵 GA4 Events", "🟠 GTM Health",
        "🟣 DataLayer", "🎯 Priority Actions"
    ])
    
    with tab1:
        if synthesis:
            # Health badge
            health = synthesis.get("overall_health", "needs_attention")
            health_color = get_health_color(health)
            st.markdown(f"""
            <span class="health-badge" style="background: {health_color}">
                {health.upper().replace('_', ' ')}
            </span>
            """, unsafe_allow_html=True)
            
            # Executive Summary
            st.markdown(f"""
            <div class="strategy-card">
                <div class="strategy-title">📊 Executive Summary</div>
                <div class="strategy-text">{synthesis.get('executive_summary', 'N/A')}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Immediate Actions
            st.markdown("### ⚡ Immediate Actions")
            for item in synthesis.get("immediate_actions", []):
                effort = item.get("effort", "N/A")
                st.markdown(f"""
                <div class="timeline-item">
                    <div class="timeline-action">{item.get('action', 'N/A')}</div>
                    <div class="timeline-why">{item.get('why', '')}</div>
                    <div class="timeline-meta">⏱️ Effort: {effort} &nbsp;|&nbsp; 📈 {item.get('impact', '')}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Plans
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"""
                <div class="strategy-card">
                    <div class="strategy-title">📅 30-Day Plan</div>
                    <div class="strategy-text">{synthesis.get('30_day_plan', 'N/A')}</div>
                </div>
                """, unsafe_allow_html=True)
            with col_b:
                st.markdown(f"""
                <div class="strategy-card">
                    <div class="strategy-title">🎯 90-Day Plan</div>
                    <div class="strategy-text">{synthesis.get('90_day_plan', 'N/A')}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Impact metrics
            col_c, col_d = st.columns(2)
            with col_c:
                st.markdown(f"""
                <div class="strategy-card">
                    <div class="strategy-title">📈 Expected Improvement</div>
                    <div class="strategy-text">{synthesis.get('estimated_data_quality_improvement', 'N/A')}</div>
                </div>
                """, unsafe_allow_html=True)
            with col_d:
                st.markdown(f"""
                <div class="strategy-card">
                    <div class="strategy-title">⚠️ Risks of Inaction</div>
                    <div class="strategy-text">{synthesis.get('risks_of_inaction', 'N/A')}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Strategy synthesis not available. Re-run the audit to generate.")
    
    with tab2:
        st.subheader(f"GA4 Event Coverage — {ga4_results.get('score', 0)}/100")
        st.caption(ga4_results.get("summary", ""))
        st.progress(ga4_results.get("score", 0) / 100)
        render_findings(ga4_results.get("findings", []))
    
    with tab3:
        st.subheader(f"GTM Container Health — {gtm_results.get('score', 0)}/100")
        st.caption(gtm_results.get("summary", ""))
        st.progress(gtm_results.get("score", 0) / 100)
        render_findings(gtm_results.get("findings", []))
    
    with tab4:
        st.subheader(f"DataLayer Quality — {datalayer_results.get('score', 0)}/100")
        st.caption(datalayer_results.get("summary", ""))
        st.progress(datalayer_results.get("score", 0) / 100)
        render_findings(datalayer_results.get("findings", []))
    
    with tab5:
        st.subheader("Priority Action Items")
        st.caption("Critical and high severity issues requiring immediate attention")
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
    
    # Downloads
    st.divider()
    col_dl1, col_dl2 = st.columns(2)
    
    with col_dl1:
        from export_html import export_report
        filepath = export_report(ga4_results, gtm_results, datalayer_results, results["setup"])
        with open(filepath, 'r') as f:
            html_content = f.read()
        st.download_button(
            label="📄 Download HTML Report",
            data=html_content,
            file_name="analytics-audit-report.html",
            mime="text/html",
            use_container_width=True
        )
        os.remove(filepath)
    
    with col_dl2:
        json_export = {
            "timestamp": datetime.now().isoformat(),
            "setup": results["setup"],
            "scores": {"overall": overall, **scores},
            "synthesis": synthesis,
            "ga4_results": ga4_results,
            "gtm_results": gtm_results,
            "datalayer_results": datalayer_results
        }
        st.download_button(
            label="📊 Download JSON Data",
            data=json.dumps(json_export, indent=2),
            file_name="analytics-audit-data.json",
            mime="application/json",
            use_container_width=True
        )

else:
    st.markdown("""
    <div style="text-align: center; padding: 4rem 2rem; color: #64748b;">
        <p style="font-size: 3rem; margin-bottom: 1rem;">👈</p>
        <p style="font-size: 1.1rem;">Fill in your setup details in the sidebar and click <strong>Run Audit</strong></p>
        <p style="font-size: 0.9rem; margin-top: 1rem;">The tool will analyze your GA4 events, GTM container, and dataLayer — then generate a strategic action plan</p>
    </div>
    """, unsafe_allow_html=True)