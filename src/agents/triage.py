"""Triage parsing and structural symptom extraction agent node."""

from typing import Any, Dict, List

from src.graph.state import SharedState


class TriageAgent:
    """Extract unstructured patient descriptions into normalized symptom labels."""

    async def process(self, state: SharedState) -> Dict[str, Any]:
        """
        Analyze raw symptoms using deterministic, auditable keyword rules.

        The result is a LangGraph-compatible partial state update. It preserves
        the existing token ledger instead of mutating the caller's Pydantic model.
        """
        print("[AGENT] Triage processing raw inputs...")
        raw = state.raw_symptoms.casefold()
        extracted: List[str] = []

        if "pressure" in raw or "headache" in raw or "hypertension" in raw:
            extracted.append("Hypertension")
        if "sugar" in raw or "diabetes" in raw or "thirst" in raw:
            extracted.append("Diabetes")
        if "migraine" in raw or "throbbing" in raw:
            extracted.append("Migraine")
        if "sleep" in raw or "insomnia" in raw:
            extracted.append("Insomnia")

        if not extracted:
            extracted.append("General_Observation")

        token_log: Dict[str, Any] = {
            "node": "triage_agent",
            "input_tokens": 150,
            "output_tokens": 45,
            "estimated_cost": 0.00015,
        }
        return {
            "extracted_symptoms": extracted,
            "current_step": "TRIAGE_COMPLETE",
            "token_usage_log": state.token_usage_log + [token_log],
        }