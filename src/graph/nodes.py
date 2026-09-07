"""Peer-to-peer adapters for the diagnostic workforce StateGraph."""

from typing import Any, Dict

from src.agents.compliance import ComplianceAgent
from src.agents.diagnostic import DiagnosticAgent
from src.agents.researcher import ResearcherAgent
from src.agents.triage import TriageAgent
from src.graph.state import SharedState


triage_worker = TriageAgent()
researcher_worker = ResearcherAgent()
diagnostic_worker = DiagnosticAgent()
compliance_worker = ComplianceAgent()


async def triage_node(state: SharedState) -> Dict[str, Any]:
    """Execute triage and return its validated partial state update."""
    return await triage_worker.process(state)


async def researcher_node(state: SharedState) -> Dict[str, Any]:
    """Execute medical research and return its validated partial state update."""
    return await researcher_worker.process(state)


async def diagnostic_node(state: SharedState) -> Dict[str, Any]:
    """Execute diagnostic reasoning and return its partial state update."""
    return await diagnostic_worker.process(state)


async def compliance_node(state: SharedState) -> Dict[str, Any]:
    """Execute compliance auditing and return its partial state update."""
    return await compliance_worker.process(state)


async def hitl_node(state: SharedState) -> Dict[str, Any]:
    """
    Represent the human checkpoint without introducing a central supervisor.

    A caller supplies ``hitl_approved=True`` when a practitioner approves the
    report. Until then, the node leaves the workflow in an explicit pending
    state; a subsequent run can resume the same peer path with approval.
    """
    if "FAILED" in state.compliance_status:
        return {
            "hitl_approved": False,
            "current_step": "HITL_BLOCKED_BY_COMPLIANCE",
        }
    if state.hitl_approved is True:
        return {"current_step": "HITL_APPROVED"}
    return {"hitl_approved": None, "current_step": "HITL_PENDING"}


async def final_compile_node(state: SharedState) -> Dict[str, Any]:
    """Compile the final report only after compliance and HITL approval pass."""
    if "FAILED" in state.compliance_status:
        return {
            "final_clinical_report": (
                "FINAL COMPILATION BLOCKED: Compliance requirements were not met."
            ),
            "current_step": "FINAL_COMPILATION_BLOCKED",
        }
    if state.hitl_approved is not True:
        return {
            "final_clinical_report": (
                "FINAL COMPILATION PENDING: Practitioner approval is required "
                "before clinical deployment."
            ),
            "current_step": "FINAL_COMPILATION_PENDING_HITL",
        }
    return {
        "final_clinical_report": (
            f"{state.final_clinical_report}\n\n"
            "HITL STATUS: Approved by practitioner for clinical evaluation."
        ),
        "current_step": "FINAL_COMPILATION_COMPLETE",
    }