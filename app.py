"""
Clinical Command Center dashboard for the peer-to-peer diagnostic workforce.

This Streamlit entry point provides an enterprise clinical SaaS interface with
patient intake, semantic memory, live P2P worker telemetry, animated execution
states, governance reporting, HITL approval, and infrastructure cost tracking.
"""

from dotenv import load_dotenv

load_dotenv()

import asyncio
from typing import Any, Dict, Mapping, Optional, Set

import streamlit as st

from src.db.vector_store import ClinicalVectorStore
from src.graph.pipeline import compile_workflow
from src.graph.state import SharedState


NODE_ORDER = (
    "triage",
    "researcher",
    "diagnostic",
    "compliance",
    "hitl",
    "final_compile",
)
NODE_LABELS = {
    "triage": "Triage / Content Creator",
    "researcher": "Researcher",
    "diagnostic": "Diagnostic / Finance Analyst",
    "compliance": "Compliance Officer",
    "hitl": "Practitioner Review",
    "final_compile": "Final Compile",
}
NODE_SHORT_LABELS = {
    "triage": "TRIAGE",
    "researcher": "RESEARCH",
    "diagnostic": "DIAGNOSTIC",
    "compliance": "COMPLIANCE",
    "hitl": "HITL REVIEW",
    "final_compile": "FINALIZE",
}


st.set_page_config(
    page_title="Clinical Command Center",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    :root {
        --canvas: #0B0F19;
        --surface: #111827;
        --surface-raised: #172033;
        --surface-soft: #1b2638;
        --line: #2a3a52;
        --muted: #8b9ab0;
        --text: #f3f7fb;
        --success: #10B981;
        --info: #3B82F6;
        --amber: #F59E0B;
        --danger: #F87171;
    }
    .stApp { background: var(--canvas); color: var(--text); font-family: Inter, "Segoe UI", sans-serif; }
    [data-testid="stSidebar"] { background: #0d1420; border-right: 1px solid var(--line); }
    [data-testid="stSidebar"] > div:first-child { padding-top: 1.5rem; }
    .block-container { max-width: 1500px; padding: 2rem 3rem 3rem; }
    h1, h2, h3, h4, p, label { font-family: Inter, "Segoe UI", sans-serif; }
    h1 { letter-spacing: -.03em; font-weight: 760; }
    h2, h3 { letter-spacing: -.02em; }
    .brand-bar { display: flex; justify-content: space-between; align-items: center; gap: 1rem; padding: 0 0 1.4rem; border-bottom: 1px solid var(--line); }
    .brand-kicker { color: #7dd3fc; font-size: .72rem; letter-spacing: .15em; text-transform: uppercase; font-weight: 800; }
    .brand-title { margin: .35rem 0 0; font-size: 2rem; font-weight: 800; letter-spacing: -.04em; }
    .brand-meta { color: var(--muted); font-size: .82rem; text-align: right; line-height: 1.7; }
    .live-dot { display: inline-block; width: 8px; height: 8px; margin-right: 7px; border-radius: 50%; background: var(--success); box-shadow: 0 0 12px var(--success); animation: live-pulse 1.5s ease-in-out infinite; }
    .section-label { color: #7dd3fc; font-size: .7rem; letter-spacing: .14em; text-transform: uppercase; font-weight: 800; margin: .4rem 0 .75rem; }
    .panel { background: linear-gradient(145deg, rgba(23,32,51,.92), rgba(17,24,39,.94)); border: 1px solid var(--line); border-radius: 14px; padding: 1.15rem; box-shadow: 0 16px 38px rgba(0,0,0,.18); }
    .panel-accent { border-color: rgba(59,130,246,.55); }
    .panel-success { border-color: rgba(16,185,129,.6); }
    .panel-title { display: flex; align-items: center; justify-content: space-between; gap: .75rem; margin-bottom: .9rem; color: var(--text); font-size: .98rem; font-weight: 750; }
    .panel-subtitle { color: var(--muted); font-size: .78rem; line-height: 1.5; }
    .metric-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: .7rem; }
    .metric { background: rgba(11,15,25,.72); border: 1px solid var(--line); border-radius: 10px; padding: .8rem; min-height: 76px; }
    .metric-label { color: var(--muted); font-size: .69rem; letter-spacing: .07em; text-transform: uppercase; }
    .metric-value { color: var(--text); font-size: 1.22rem; font-weight: 760; margin-top: .35rem; }
    .metric-value.success { color: #6ee7b7; }
    .metric-value.info { color: #93c5fd; }
    .metric-value.amber { color: #fcd34d; }
    .chip-row { display: flex; flex-wrap: wrap; gap: .45rem; margin-top: .65rem; }
    .chip { display: inline-flex; align-items: center; border-radius: 999px; padding: .35rem .65rem; border: 1px solid rgba(16,185,129,.48); background: rgba(16,185,129,.12); color: #a7f3d0; font-size: .75rem; font-weight: 700; }
    .chip-critical { border-color: rgba(245,158,11,.56); background: rgba(245,158,11,.13); color: #fde68a; }
    .flow-shell { background: #0d1522; border: 1px solid #263b57; border-radius: 14px; padding: 1rem; }
    .agent-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: .75rem; }
    .agent-card { min-height: 112px; padding: .9rem; border: 1px solid #30435d; border-radius: 11px; background: rgba(17,24,39,.9); color: #8190a5; transition: all .25s ease; }
    .agent-card.active { border-color: var(--success); box-shadow: 0 0 22px rgba(16,185,129,.42); animation: telemetry-pulse 1.25s ease-in-out infinite; color: var(--text); }
    .agent-card.done { border-color: rgba(16,185,129,.66); background: rgba(16,185,129,.08); color: #d1fae5; }
    .agent-card.blocked { border-color: var(--danger); background: rgba(248,113,113,.08); color: #fecaca; }
    .agent-index { color: #64748b; font-size: .67rem; letter-spacing: .12em; font-weight: 800; }
    .agent-title { margin-top: .42rem; font-size: .86rem; font-weight: 760; }
    .agent-status { margin-top: .7rem; font-size: .68rem; letter-spacing: .09em; font-weight: 800; }
    .packet { color: #6ee7b7; margin-top: .5rem; font-size: .68rem; animation: packet-blink 1s linear infinite; }
    .ledger-row { display: flex; align-items: center; justify-content: space-between; gap: 1rem; padding: .55rem 0; border-bottom: 1px solid rgba(42,58,82,.65); color: var(--muted); font-size: .78rem; }
    .ledger-row:last-child { border-bottom: 0; }
    .ledger-value { color: var(--text); font-weight: 750; }
    .footer-note { color: #64748b; font-size: .72rem; text-align: center; padding-top: 1.2rem; }
    @keyframes telemetry-pulse { 0%,100% { box-shadow: 0 0 5px rgba(16,185,129,.25); } 50% { box-shadow: 0 0 25px rgba(16,185,129,.75); } }
    @keyframes packet-blink { 0%,100% { opacity: .35; transform: translateX(0); } 50% { opacity: 1; transform: translateX(4px); } }
    @keyframes live-pulse { 0%,100% { opacity: .45; } 50% { opacity: 1; } }
    @media (max-width: 1000px) { .block-container { padding: 1.25rem; } .metric-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } .agent-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
</style>
""",
    unsafe_allow_html=True,
)


def get_vector_store() -> ClinicalVectorStore:
    """Return the session-scoped ChromaDB semantic memory store."""
    if "vector_db" not in st.session_state:
        st.session_state.vector_db = ClinicalVectorStore()
    return st.session_state.vector_db


def get_compiled_graph() -> Any:
    """Return the current compiled P2P graph."""
    if st.session_state.get("compiled_graph_version") != 4:
        st.session_state.compiled_graph = compile_workflow()
        st.session_state.compiled_graph_version = 4
    return st.session_state.compiled_graph


def get_telemetry() -> Dict[str, Any]:
    """Return initialized session-level token and cost counters."""
    if "accumulated_tokens" not in st.session_state:
        st.session_state.accumulated_tokens = {"input": 0, "output": 0, "total_cost": 0.0}
    return st.session_state.accumulated_tokens


def render_metric(label: str, value: str, tone: str = "") -> str:
    """Build one reusable metric card fragment."""
    return f'<div class="metric"><div class="metric-label">{label}</div><div class="metric-value {tone}">{value}</div></div>'


def collaboration_dot(active_node: Optional[str], completed: Set[str]) -> str:
    """Build the live Graphviz representation of the P2P workforce."""
    node_lines = []
    for node_name in NODE_ORDER:
        if node_name == active_node:
            color, fill, status = "#10B981", "#12352f", "PROCESSING"
        elif node_name in completed:
            color, fill, status = "#10B981", "#17352a", "DONE"
        else:
            color, fill, status = "#64748B", "#18202c", "IDLE"
        node_lines.append(
            f'{node_name} [label="{NODE_SHORT_LABELS[node_name]}\\n{status}", color="{color}", fillcolor="{fill}"];'
        )
    edges = (
        'triage -> researcher [dir=both, label="context"];',
        'researcher -> diagnostic [label="evidence"];',
        'diagnostic -> compliance [label="candidate"];',
        'compliance -> hitl [label="clearance"];',
        'hitl -> final_compile [label="approval"];',
    )
    return (
        'digraph P2P { graph [bgcolor="transparent", rankdir=LR, pad="0.2"]; '
        'node [shape=box, style="rounded,filled", fontname="sans", '
        'fontcolor="#f8fafc", penwidth=2, margin="0.18,0.12"]; '
        'edge [color="#10B981", fontcolor="#94a3b8", penwidth=2, arrowsize=.8]; '
        + " ".join(node_lines) + " " + " ".join(edges) + " }"
    )


def render_agent_cards(container: Any, active_node: Optional[str], completed: Set[str], blocked: Set[str]) -> None:
    """Render live worker cards with idle, processing, done, and blocked states."""
    cards = []
    for index, node_name in enumerate(NODE_ORDER, start=1):
        if node_name in blocked:
            state_class, status, packet = "blocked", "⛔ BLOCKED", ""
        elif node_name == active_node:
            state_class, status, packet = "active", "⚡ ACTIVE TELEMETRY", '<div class="packet">● state packet in transit</div>'
        elif node_name in completed:
            state_class, status, packet = "done", "✅ COMPLETE", ""
        else:
            state_class, status, packet = "", "⏸️ IDLE", ""
        cards.append(
            f'<div class="agent-card {state_class}"><div class="agent-index">NODE {index:02d}</div>'
            f'<div class="agent-title">{NODE_LABELS[node_name]}</div><div class="agent-status">{status}</div>{packet}</div>'
        )
    container.markdown('<div class="agent-grid">' + "".join(cards) + "</div>", unsafe_allow_html=True)


def update_telemetry(result_state: Mapping[str, Any]) -> None:
    """Aggregate token and cost records from a graph result."""
    telemetry = get_telemetry()
    logs = result_state.get("token_usage_log", [])
    telemetry["input"] = sum(int(log.get("input_tokens", 0)) for log in logs)
    telemetry["output"] = sum(int(log.get("output_tokens", 0)) for log in logs)
    telemetry["total_cost"] = sum(float(log.get("estimated_cost", 0.0)) for log in logs)


async def stream_graph(graph: Any, initial_state: SharedState, graph_placeholder: Any, cards_placeholder: Any, activity_placeholder: Any) -> Dict[str, Any]:
    """Stream LangGraph updates and animate each direct P2P handoff."""
    completed: Set[str] = set()
    blocked: Set[str] = set()
    final_state: Dict[str, Any] = initial_state.model_dump()
    active_node: Optional[str] = NODE_ORDER[0]
    graph_placeholder.graphviz_chart(collaboration_dot(active_node, completed), use_container_width=True)
    render_agent_cards(cards_placeholder, active_node, completed, blocked)
    activity_placeholder.info("⚡ Triage / Content Creator is processing the admission packet.")

    async for update in graph.astream(initial_state, stream_mode="updates"):
        for node_name, node_update in update.items():
            completed.add(node_name)
            final_state.update(node_update)
            if "FAILED" in str(final_state.get("compliance_status", "")):
                blocked.update({"hitl", "final_compile"})
            next_index = NODE_ORDER.index(node_name) + 1
            active_node = NODE_ORDER[next_index] if next_index < len(NODE_ORDER) else None
            graph_placeholder.graphviz_chart(collaboration_dot(active_node, completed), use_container_width=True)
            render_agent_cards(cards_placeholder, active_node, completed, blocked)
            activity_placeholder.success(f"✅ {NODE_LABELS[node_name]} completed and handed state to its peer.")
            if active_node is not None:
                await asyncio.sleep(.35)
                activity_placeholder.info(f"⚡ {NODE_LABELS[active_node]} is processing the incoming state packet.")
    return final_state


def run_streaming_graph(graph: Any, initial_state: SharedState, graph_placeholder: Any, cards_placeholder: Any, activity_placeholder: Any) -> Dict[str, Any]:
    """Bridge the async graph stream into Streamlit's synchronous execution."""
    return asyncio.run(stream_graph(graph, initial_state, graph_placeholder, cards_placeholder, activity_placeholder))


vector_store = get_vector_store()
compiled_graph = get_compiled_graph()
telemetry = get_telemetry()

st.markdown(
    '<div class="brand-bar"><div><div class="brand-kicker">Clinical Operations Platform / P2P Workforce</div>'
    '<div class="brand-title">Clinical Command Center</div></div>'
    '<div class="brand-meta"><span class="live-dot"></span> SYSTEM OPERATIONAL<br/>Secure diagnostic orchestration</div></div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown('<div class="section-label">Workspace Controls</div>', unsafe_allow_html=True)
    st.selectbox("Inference target", ["openai/gpt-oss-120b"], index=0)
    st.checkbox("Isolated testing context", value=True)
    st.markdown("---")
    st.markdown('<div class="section-label">Infrastructure Ledger</div>', unsafe_allow_html=True)
    st.markdown(render_metric("Input tokens", str(telemetry["input"]), "info"), unsafe_allow_html=True)
    st.markdown(render_metric("Output tokens", str(telemetry["output"]), "info"), unsafe_allow_html=True)
    st.markdown(render_metric("Session cost", f"${telemetry['total_cost']:.5f}", "success"), unsafe_allow_html=True)
    st.markdown("---")
    st.caption("Clinical outputs are decision-support artifacts and require practitioner review before use.")

st.markdown('<div class="section-label">Admission & Context</div>', unsafe_allow_html=True)
intake_column, context_column = st.columns([1.35, 1])
with intake_column:
    st.markdown('<div class="panel panel-accent"><div class="panel-title">Patient Intake Admission Form <span>INTAKE  /  01</span></div><div class="panel-subtitle">Capture the minimum clinical context required to initialize the diagnostic workforce.</div></div>', unsafe_allow_html=True)
    with st.expander("Open admission fields", expanded=True):
        patient_id = st.text_input("Patient tracker ID", value="PT-8849-X")
        full_name = st.text_input("Full name", value="Jordan Morgan")
        age = st.number_input("Age", min_value=0, max_value=125, value=48, step=1)
        vital_column, history_column = st.columns(2)
        with vital_column:
            vital_signs = st.text_input("Vital signs", value="BP 168/102 mmHg")
        with history_column:
            medical_history = st.text_input("Medical history ledger", value="Type-2 diabetes; Metformin")
        symptoms = st.text_area(
            "Presenting symptoms and clinical narrative",
            value=("Sudden severe headache with elevated blood pressure spikes. " "Reports increased thirst and poor sleep."),
            height=118,
        )

with context_column:
    st.markdown('<div class="panel"><div class="panel-title">Semantic Memory <span>CONTEXT  /  02</span></div><div class="panel-subtitle">Retrieve a related historical case before activating the workforce.</div></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Retrieve historical context", use_container_width=True):
        if symptoms.strip():
            st.success("Historical case context recovered.")
            st.code(vector_store.search_similar_cases(symptoms, max_results=1)[0], language="text")
        else:
            st.error("Presenting symptoms are required.")
    else:
        st.info("No prefetch requested. The memory layer remains available to the Researcher peer.")

st.markdown('<div class="section-label">Live Workforce Telemetry</div>', unsafe_allow_html=True)
flow_header_column, flow_action_column = st.columns([3, 1])
with flow_header_column:
    st.markdown('<div class="panel-title">Peer-to-Peer Collaboration Flow <span class="live-dot"></span></div>', unsafe_allow_html=True)
    st.caption("Triage ↔ Researcher → Diagnostic → Compliance → Practitioner Review → Final Compile")
with flow_action_column:
    execute_clicked = st.button("🚀 Activate workforce", use_container_width=True)

graph_placeholder = st.empty()
cards_placeholder = st.empty()
activity_placeholder = st.empty()
graph_placeholder.graphviz_chart(collaboration_dot(None, set()), use_container_width=True)
render_agent_cards(cards_placeholder, None, set(), set())
activity_placeholder.caption("⏸️ Workforce idle. Activate the pipeline to stream live state packets.")

if execute_clicked:
    if not symptoms.strip():
        st.error("Presenting symptoms are required before activation.")
    else:
        raw_input = f"Patient {full_name}, age {age}. Vitals: {vital_signs}. History: {medical_history}. Symptoms: {symptoms}"
        initial_state = SharedState(patient_id=patient_id, raw_symptoms=raw_input, retry_count=0, hitl_approved=None)
        st.session_state.last_request = {"patient_id": patient_id, "raw_symptoms": raw_input}
        with st.spinner("Streaming clinical state across peer nodes..."):
            st.session_state.last_result = run_streaming_graph(compiled_graph, initial_state, graph_placeholder, cards_placeholder, activity_placeholder)
        update_telemetry(st.session_state.last_result)

result_state = st.session_state.get("last_result")
if result_state:
    st.markdown('<div class="section-label">Clinical Insights</div>', unsafe_allow_html=True)
    symptoms_found = result_state.get("extracted_symptoms", [])
    compliance_status = str(result_state.get("compliance_status", "PENDING"))
    status_tone = "success" if compliance_status == "PASSED" else "amber" if compliance_status == "PENDING" else ""
    st.markdown('<div class="metric-grid">' + render_metric("Workflow status", result_state.get("current_step", "UNKNOWN"), status_tone) + render_metric("Symptoms mapped", str(len(symptoms_found)), "info") + render_metric("P2P nodes complete", "6 / 6" if result_state.get("current_step") == "FINAL_COMPILATION_COMPLETE" else "4 / 6", "info") + render_metric("Compliance gate", compliance_status, status_tone) + '</div>', unsafe_allow_html=True)

    insight_column, diagnosis_column = st.columns([1, 1.35])
    with insight_column:
        st.markdown('<div class="panel"><div class="panel-title">Medical Ledger Chips</div><div class="panel-subtitle">Normalized observations emitted by the Triage peer.</div><div class="chip-row">' + "".join(f'<span class="chip">● {item}</span>' for item in symptoms_found) + '</div></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="panel"><div class="panel-title">Governance Clearance</div><div class="panel-subtitle">Compliance peer decision and clinical safety boundary.</div></div>', unsafe_allow_html=True)
        if "FAILED" in compliance_status:
            st.error(compliance_status)
        else:
            st.success(compliance_status)
    with diagnosis_column:
        st.markdown('<div class="panel panel-success"><div class="panel-title">Diagnostic Intelligence Brief <span>DECISION SUPPORT</span></div><div class="panel-subtitle">Best-scored reasoning pathway from the Diagnostic peer.</div></div>', unsafe_allow_html=True)
        st.code(result_state.get("initial_diagnosis", ""), language="text")
        st.info(result_state.get("medical_research_data", ""))

    st.markdown('<div class="panel"><div class="panel-title">Verified Clinical Compilation</div><div class="panel-subtitle">Final output remains a practitioner-reviewed decision-support artifact.</div></div>', unsafe_allow_html=True)
    st.text_area("Secure clinical report", value=result_state.get("final_clinical_report", ""), height=150)

    if compliance_status == "PASSED" and result_state.get("hitl_approved") is not True:
        st.markdown('<div class="panel panel-accent"><div class="panel-title">Practitioner Review Checkpoint <span>HITL REQUIRED</span></div><div class="panel-subtitle">Review the generated evidence before allowing the Final Compile peer to complete.</div></div>', unsafe_allow_html=True)
        st.text_input("Practitioner approval notes", value="Validated for clinical evaluation.")
        approve_clicked = st.button("✅ Approve and continue to final compile", use_container_width=True)
        if approve_clicked:
            request = st.session_state["last_request"]
            approved_state = SharedState(patient_id=request["patient_id"], raw_symptoms=request["raw_symptoms"], retry_count=0, hitl_approved=True)
            with st.spinner("Resuming P2P flow through practitioner approval..."):
                st.session_state.last_result = run_streaming_graph(compiled_graph, approved_state, graph_placeholder, cards_placeholder, activity_placeholder)
            update_telemetry(st.session_state.last_result)
            st.rerun()

st.markdown('<div class="section-label">Infrastructure Cost Optimization Tracker</div>', unsafe_allow_html=True)
footer_column, ledger_column = st.columns([1.25, 1])
with footer_column:
    st.markdown('<div class="panel"><div class="panel-title">Session Efficiency</div><div class="panel-subtitle">Live usage accounting across every worker handoff.</div><br>' + render_metric("Estimated transaction cost", f"${telemetry['total_cost']:.5f}", "success") + '</div>', unsafe_allow_html=True)
with ledger_column:
    st.markdown('<div class="panel"><div class="panel-title">Token Ledger</div>' + f'<div class="ledger-row"><span>Prompt tokens</span><span class="ledger-value">{telemetry["input"]:,}</span></div><div class="ledger-row"><span>Completion tokens</span><span class="ledger-value">{telemetry["output"]:,}</span></div><div class="ledger-row"><span>Total footprint</span><span class="ledger-value">{telemetry["input"] + telemetry["output"]:,}</span></div></div>', unsafe_allow_html=True)

st.markdown('<div class="footer-note">Clinical Command Center · P2P Agentic Workforce · Secure local telemetry · Practitioner oversight required</div>', unsafe_allow_html=True)
