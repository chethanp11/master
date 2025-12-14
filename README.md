# master — agentic framework platform

`master/` is a headless, product-agnostic agentic AI framework that powers multiple products from a single deployable service.

- One shared API: `/api/...`
- One common platform UI: `/` and `/{product}`
- Products plug in via `products/<product>/` (flows, agents, tools, prompts, config)

This repo is designed to let teams build **enterprise-grade agentic prototypes fast**, without rewriting orchestration, governance, logging, or deployment logic.

---

## What master is

- A **core runtime** (`core/`) that provides:
  - orchestration & workflow execution
  - agent and tool execution
  - model routing
  - memory & persistence
  - governance & safety
  - logging, tracing, metrics
  - RAG / knowledge access
- A **product layer** (`products/`) where each product defines only:
  - flows (YAML / JSON)
  - agents (Python)
  - tools (Python)
  - prompts & config (YAML)
- A **gateway** (`gateway/`) that exposes:
  - HTTP API (FastAPI)
  - Platform UI (single UI for all products)
  - CLI utilities

---

## Repository layout (high level)

- `core/` — framework runtime (product-agnostic)
- `products/` — product plug-ins (agentaura, remedy, sandbox, etc.)
- `gateway/` — API + platform UI + CLI
- `configs/` — global config (app / models / policies / logging)
- `secrets/` — secrets (gitignored) + templates
- `storage/` — runtime data (gitignored): sqlite db, vectors, artifacts
- `logs/` — logs output (gitignored)
- `tests/` — core + integration tests
- `scripts/` — scaffolding, ingestion, migrations, helpers
- `docs/` — specifications and standards (source of truth)

---

## Prerequisites

- macOS (primary development)
- Python 3.11+ recommended
- Git

---

## Setup (Mac)

### 1) Create virtual environment
```bash
cd /path/to/master
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip

2) Install dependencies

pip install -r requirements.txt

3) Create env + secrets (both gitignored)

cp .env.example .env
cp secrets/secrets.example.yaml secrets/secrets.yaml

Edit:
	•	.env for non-secret environment flags
	•	secrets/secrets.yaml for keys and tokens

⸻

Run locally

Run API (FastAPI)

source .venv/bin/activate
uvicorn gateway.api.http_app:app --reload --port 8000

API base:

http://localhost:8000

Run UI (platform UI)

UI lives under gateway/ui/.

If using Streamlit:

source .venv/bin/activate
streamlit run gateway/ui/platform_app.py --server.port 8501

UI base:

http://localhost:8501

Product pages:
	•	/agentaura
	•	/remedy
	•	/sandbox

⸻

Run tests

source .venv/bin/activate
pytest -q

Optional compile sanity check:

python -m compileall core gateway products


⸻

Add a new product

1) Scaffold product

python scripts/create_product.py --name myproduct

This creates:
	•	products/myproduct/manifest.yaml
	•	products/myproduct/flows/
	•	products/myproduct/agents/
	•	products/myproduct/tools/
	•	products/myproduct/prompts/
	•	products/myproduct/config/product.yaml
	•	products/myproduct/tests/

2) Define a flow

Create a flow YAML under:

products/myproduct/flows/<flow_name>.yaml

3) Implement agents and tools

Add Python implementations under:
	•	products/myproduct/agents/
	•	products/myproduct/tools/

Products are discovered via manifest.yaml.
No hardcoding in core or gateway.

⸻

Golden path demo (v1)

The v1 demo product is sandbox with flow hello_world.

Start API

uvicorn gateway.api.http_app:app --reload --port 8000

Trigger a run

curl -X POST "http://localhost:8000/api/run/sandbox/hello_world" \
  -H "Content-Type: application/json" \
  -d '{"message":"hello"}'

You will receive a run_id.

Check run status

curl "http://localhost:8000/api/run/<run_id>"

If the flow includes a human-approval step, status will be:

PENDING_HUMAN

Resume after approval

curl -X POST "http://localhost:8000/api/resume_run/<run_id>" \
  -H "Content-Type: application/json" \
  -d '{"approved":true,"comment":"ok"}'


⸻

Non-negotiable boundaries
	•	No env/secrets reads outside core/config/loader.py
	•	No tool execution outside core/tools/executor.py
	•	No persistence outside core/memory/*
	•	No direct model vendor calls outside core/models/providers/*
	•	All runs emit traces via core/logging/tracing.py

⸻

Common commands

# activate venv
source .venv/bin/activate

# run API
uvicorn gateway.api.http_app:app --reload --port 8000

# run UI (if Streamlit)
streamlit run gateway/ui/platform_app.py --server.port 8501

# run tests
pytest -q

If you’re ready, say **“Next: Prompt 0.2 — docs/overview.md”** and we’ll continue without breaking momentum.