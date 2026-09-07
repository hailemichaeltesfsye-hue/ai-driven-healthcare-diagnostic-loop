"""Compile the peer-to-peer healthcare diagnostic workforce graph."""

from langgraph.graph import END, StateGraph

from src.graph.nodes import (
    compliance_node,
    diagnostic_node,
    final_compile_node,
    hitl_node,
    researcher_node,
    triage_node,
)
from src.graph.state import SharedState


def compile_workflow() -> StateGraph:
    """Build direct peer-to-peer handoffs without a supervisor bottleneck."""
    workflow = StateGraph(SharedState)
    workflow.add_node("triage", triage_node)
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("diagnostic", diagnostic_node)
    workflow.add_node("compliance", compliance_node)
    workflow.add_node("hitl", hitl_node)
    workflow.add_node("final_compile", final_compile_node)

    workflow.set_entry_point("triage")
    workflow.add_edge("triage", "researcher")
    workflow.add_edge("researcher", "diagnostic")
    workflow.add_edge("diagnostic", "compliance")
    workflow.add_edge("compliance", "hitl")
    workflow.add_edge("hitl", "final_compile")
    workflow.add_edge("final_compile", END)
    return workflow.compile()


print("Part 3 LangGraph Multi-Agent Orchestration fabric successfully compiled.")