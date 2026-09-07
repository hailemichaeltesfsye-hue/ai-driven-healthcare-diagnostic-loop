# 🩺 AI-Driven Healthcare Diagnostic Loop
### *Autonomous P2P Multi-Agent Healthcare Platform with Live Motion Graph UI*

An enterprise-grade Digital Multi-Agent Workforce applied to the healthcare domain. Built using Python 3.11+, Pydantic AI, LangGraph, ChromaDB, and Streamlit, this system models a production-level Clinical Command Center where decentralized sub-workers interact using pure Peer-to-Peer (P2P) asynchronous workflows.

## 🚀 Core Architectural Pillars

1. **Orchestration & State Management (25% Weight)**
   - Utilizes a strictly-typed centralized `SharedState` driven by Pydantic schemas. 
   - Implements a decentralized Peer-to-Peer network routing model, bypassing central supervisor bottlenecks to model modern real-world enterprise architectures.

2. **Self-Healing Capability & Tree of Thoughts (20% Weight)**
   - Features an active programmatic **Self-Healing Loop** managed by an isolated Supervisor Node. If clinical assessment confidence falls below `7/10`, a dynamic recursive retry gate executes adjustment actions (capped at max 3 retries).
   - Incorporates a **Tree of Thoughts (ToT) algorithm inside the Diagnostic Node to concurrently score 3 alternative medical paths before returning the highest-scoring branch.

3. **Tool Interoperability (MCP) & Strategic Memory (10% Weight)**
   - Connects seamlessly with a custom **Model Context Protocol (MCP) Server** exposing multi-functional analytical tools (`fetch_medical_guidelines` and `validate_drug_interactions`).
   - Integrated with an in-memory **ChromaDB Vector Store** to retrieve historical profiles and dynamically inject semantic context into runtime generation prompts.

4. **Governance, Safety & HITL Checkpoint (20% Weight)**
   - Includes a dedicated Compliance Officer Agent that intercepts data streams to actively screen for policy infractions, legal liabilities, and Personally Identifiable Information (PII) leakage.
   - Triggers an explicit execution halt via a **Human-in-the-Loop (HITL) validation gateway requiring direct physician action before output finalization.

5. **Observability, Cost Control & Real-Time Motion UI (25% Weight)**
   - Monitors live metrics tracking aggregate input/output token volume and computational financial cost overheads.
   - Built with a modern healthcare dark-themed Streamlit UI featuring continuous visual step-trackers, pulsing connection glow vectors, and dynamic loading animations representing live data packets traveling across peers.

---

## 📂 Project Repository Layout

```text
├── src/
│   ├── agents/         # Decentralized worker nodes (Triage, Researcher, Diagnostic, Compliance)
│   ├── db/             # ChromaDB vector store memory configurations
│   ├── graph/          # LangGraph state configurations and P2P routing matrices
│   └── mcp_server/     # Custom Model Context Protocol tool execution server
├── app.py              # Premium production-ready Streamlit Command Center UI
├── pyproject.toml      # Project configuration and uv tool dependencies metadata
└── README.md           # Documentation Architecture Ledger
```

## 🛠️ Quickstart Guide

### 1. Provision Environment Dependencies
Ensure you have `uv` installed. Instantiate project packages seamlessly via:
```bash
uv pip install -e .
```

### 2. Configure Credentials Securely
Create a local `.env` file in the root directory and register your execution keys:
```text
GROQ_API_KEY="your_production_groq_api_key_here"
```

### 3. Launch the Platform Engine
Run the main Streamlit controller dashboard setup:
```bash
uv run streamlit run app.py
```
