"""
Compliance Officer Agent and data-safety guardrail pipeline.

Screens for personally identifiable information leaks and medical-liability
constraints before a clinical report can be marked safe for evaluation.
"""

from typing import Any, Dict, List

from src.graph.state import SharedState


class ComplianceAgent:
    """Intercept state variables before compilation to enforce safety boundaries."""

    async def process(self, state: SharedState) -> Dict[str, Any]:
        """
        Audit raw input and compile either a safe report or a blocking alert.

        The method returns a LangGraph-compatible partial state update and keeps
        the token ledger immutable by creating a new list for the response.
        """
        print("[AGENT] Compliance Officer auditing clinical data streams...")
        raw_input = state.raw_symptoms.casefold()
        violations: List[str] = []

        if "@" in raw_input or "ssn" in raw_input:
            violations.append(
                "Potential Personally Identifiable Information (PII) leakage detected."
            )
        if "sue" in raw_input or "lawyer" in raw_input:
            violations.append("Legal liability constraint alert activated.")

        if violations:
            status = f"FAILED: {', '.join(violations)}"
            compiled_report = (
                "CRITICAL PRIVACY VIOLATION: Final clinical compilation halted "
                "due to regulatory audit failure."
            )
        else:
            status = "PASSED"
            compiled_report = (
                "FINAL CLINICAL REPORT\n"
                "=====================\n"
                f"Patient Tracker ID: {state.patient_id}\n"
                f"Symptoms Analysed: {', '.join(state.extracted_symptoms)}\n"
                f"Diagnostic Pathway: {state.initial_diagnosis}\n"
                "Status: Certified safe for clinical evaluation."
            )

        token_log: Dict[str, Any] = {
            "node": "compliance_agent",
            "input_tokens": 350,
            "output_tokens": 140,
            "estimated_cost": 0.00049,
        }
        return {
            "compliance_status": status,
            "final_clinical_report": compiled_report,
            "current_step": "COMPLIANCE_AUDIT_COMPLETE",
            "token_usage_log": state.token_usage_log + [token_log],
        }