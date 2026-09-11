# AI-Driven Healthcare Diagnostic Loop

**Autonomous P2P Multi-Agent Healthcare Platform with a Live Motion Graph UI**

An enterprise-grade digital multi-agent workforce applied to the healthcare domain. Built with **Python 3.11+**, **Pydantic AI**, **LangGraph**, **ChromaDB**, and **Streamlit**, the system models a production-level clinical command center where decentralized sub-workers coordinate using a pure **peer-to-peer (P2P)** asynchronous workflow — no central supervisor bottleneck.

## Core Architectural Pillars

### 1. Orchestration & State Management
- Strictly-typed, shareable state driven by Pydantic schemas (`src/graph/state.py`)
- Decentralized peer-to-peer routing model (`src/graph/edges.py`, `src/graph/pipeline.py`) instead of a single central supervisor bottleneck

### 2. Self-Healing & Tree of Thoughts
- An autonomous self-healing loop, overseen by an isolated Supervisor node, re-triggers the diagnostic branch (capped at 3 retries) if clinical assessment confidence falls below threshold
- A Tree-of-Thoughts (ToT) approach in the Diagnostic agent scores multiple candidate medical paths concurrently before returning the highest-scoring branch

### 3. Tool Interoperability (MCP) & Strategic Memory
- A custom Model Context Protocol server (`src/mcp_server/server.py`, `tools.py`) exposes analytical tools (e.g. fetching medical guidelines, validating drug interactions)
- An in-memory ChromaDB vector store (`src/db/vector_store.py`) retrieves historical patient context and injects it into agent reasoning

### 4. Governance, Safety & HITL Checkpoint
- A dedicated Compliance agent (`src/agents/compliance.py`) screens data streams for policy breaches, legal liabilities, and PII leakage
- A Human-in-the-Loop (HITL) validation gateway halts execution, requiring direct physician sign-off before finalizing output

### 5. Observability, Cost Control & Real-Time Motion UI
- Live tracking of aggregate token volume and computational cost
- A dark-themed Streamlit UI with live step-trackers and animated connection/data-flow visuals

## Agents (`src/agents/`)

| Agent | Role |
|---|---|
| `triage.py` | Initial intake — classifies and routes incoming cases |
| `researcher.py` | Gathers supporting medical/clinical information |
| `diagnostic.py` | Runs Tree-of-Thoughts diagnostic reasoning |
| `compliance.py` | Screens for policy, legal, and PII risks |
| `supervisor.py` | Isolated node managing the self-healing retry loop |

## Project Structure

```
ai-driven-healthcare-diagnostic-loop/
├── scripts/                          # Utility/setup scripts
├── src/
│   ├── agents/
│   │   ├── triage.py                  # Case intake and routing
│   │   ├── researcher.py              # Clinical research support
│   │   ├── diagnostic.py              # Tree-of-Thoughts diagnostic reasoning
│   │   ├── compliance.py              # Policy/PII/legal screening
│   │   └── supervisor.py              # Self-healing retry supervisor node
│   ├── db/
│   │   └── vector_store.py            # ChromaDB vector store integration
│   ├── graph/
│   │   ├── state.py                   # Pydantic-typed shared state
│   │   ├── nodes.py                   # LangGraph node definitions
│   │   ├── edges.py                   # P2P routing edges
│   │   └── pipeline.py                # Graph assembly / pipeline entry point
│   └── mcp_server/
│       ├── server.py                  # MCP server implementation
│       └── tools.py                   # Exposed MCP tools (guidelines, drug interactions)
├── app.py                             # Streamlit dashboard entry point
├── .env.example                       # Example environment variables
├── pyproject.toml                     # Project metadata and dependencies (uv)
└── uv.lock                            # Locked dependency versions
```

## Getting Started

### 1. Provision Environment Dependencies

Ensure you have [uv](https://github.com/astral-sh/uv) installed, then install the project in editable mode:

```bash
uv pip install -e .
```

### 2. Configure Credentials Securely

Create a `.env` file in the project root and set your execution keys:

```
GROQ_API_KEY="your_production_groq_api_key_here"
```

### 3. Launch the Platform Engine

Run the main Streamlit dashboard:

```bash
streamlit run app.py
```

This starts the live motion graph UI, where cases flow through Triage → Researcher → Diagnostic → Compliance, with self-healing retries and HITL checkpoints visualized in real time.

## Author

**Hailemichael Tesfaye Mekuria**
[LinkedIn](https://www.linkedin.com/in/hailemichael-tesfaye-2b7114401/) · [GitHub](https://github.com/hailemichaeltesfsye-hue)
