# TechKart AI Customer Support Agent

> An AI-powered customer support agent for a fictional Indian electronics retailer
> built with **LangGraph**, **RAG**, **Human-in-the-Loop approvals**, and running
> entirely on **local Ollama models** (no cloud API keys required).

---

## Table of Contents

1. [What It Does](#what-it-does)
2. [Architecture Overview](#architecture-overview)
3. [Tech Stack](#tech-stack)
4. [Project Structure](#project-structure)
5. [Prerequisites](#prerequisites)
6. [Quick Start](#quick-start)
7. [Environment Variables Reference](#environment-variables-reference)
8. [Changing the LLM (Chat) Model](#changing-the-llm-chat-model)
9. [Changing the Embedding Model](#changing-the-embedding-model)
10. [Switching Between Providers](#switching-between-providers)
11. [LangGraph Workflow Deep-Dive](#langgraph-workflow-deep-dive)
12. [Tools Reference](#tools-reference)
13. [RAG Pipeline](#rag-pipeline)
14. [Human-in-the-Loop (HITL) Approval Flow](#human-in-the-loop-hitl-approval-flow)
15. [API Reference](#api-reference)
16. [Frontend Pages](#frontend-pages)
17. [Seeded Demo Data](#seeded-demo-data)
18. [Guardrails](#guardrails)
19. [Troubleshooting](#troubleshooting)
20. [Development Guide](#development-guide)

---

## What It Does

Customers can chat with an AI agent to:

- **Look up orders** -- "Show me my recent orders" / "What's the status of TK10001?"
- **Track shipments** -- "Where is my iPhone 15 Pro Max?"
- **Request refunds** -- "I received a damaged iPhone, I want a refund"
- **Ask policy questions** -- "What is your return policy?" (answered via RAG)
- **Create support tickets** -- "Create a ticket for my issue"

**Refund requests flow through a Human-in-the-Loop approval pipeline:**

1. AI evaluates refund eligibility from the database
2. If eligible, a refund proposal is created
3. Risk evaluation marks it as "risky"
4. An approval record is inserted into the database
5. A human agent reviews and approves/rejects/edits via the Approvals UI

---

## Architecture Overview

```
+---------------+     HTTP      +---------------+     HTTP      +-------------------+
|   Next.js     | ----------->  |   FastAPI     | <-----------  |  Ollama Server    |
|   Frontend    |               |   Backend     |               |  (llama3.2 +      |
|  :3000        |               |   :8000       |               |  nomic-embed)     |
+---------------+               +-------+-------+               +-------------------+
                                       |
                                       v
                               +----------------+
                               |   LangGraph    |
                               |   Workflow     |
                               |  +---------+   |
                               |  | Guard-  |   |
                               |  | rails   |   |
                               |  +----+----+   |
                               |       v        |
                               |  +---------+   |
                               |  |  Agent  |-- +-> Tools (orders, refunds, etc.)
                               |  |  (LLM)  |   |
                               |  +----+----+   |
                               |       v        |
                               |  +---------+   |
                               |  |   RAG   |   | <-- ChromaDB (policy docs)
                               |  +----+----+   |
                               |       v        |
                               |  +---------+   |
                               |  |  Risk   |   |
                               |  | Evaluator|  |
                               |  +----+----+   |
                               |       v        |
                               |  +-----------+ |
                               |  |  Human    | +-> SQLite (approvals)
                               |  | Approval  | |
                               |  +-----------+ |
                               +----------------+
                                       |
                                       v
                               +----------------+
                               |  SQLite DB     |
                               |  (techkart.db) |
                               +----------------+
```


---

## Tech Stack

### Backend

| Component | Technology | Purpose |
|---|---|---|
| **Web Framework** | FastAPI 0.111.0 | REST API, async request handling |
| **Agent Framework** | LangGraph 0.2.15 | Multi-step agent workflow with state machine |
| **LLM Orchestration** | LangChain 0.2.12 | Tool binding, prompt management, chat models |
| **LLM (local)** | Ollama + llama3.2 | Chat inference (CPU OK, no GPU needed) |
| **Embeddings (local)** | Ollama + nomic-embed-text | Vector embeddings for RAG |
| **Vector Store** | ChromaDB 0.5.5 | Persistent vector storage for policy docs |
| **Database** | SQLite + SQLAlchemy 2.0 | Async ORM for orders, approvals, tickets |
| **Settings** | Pydantic Settings | Type-safe env var loading |

### Frontend

| Component | Technology | Purpose |
|---|---|---|
| **Framework** | Next.js 14.2 (App Router) | React SSR, client components |
| **Styling** | Tailwind CSS 3.4 | Utility-first CSS |
| **Icons** | Lucide React | UI icons |

### Infrastructure

| Component | Technology | Purpose |
|---|---|---|
| **Containerization** | Docker + Docker Compose | One-command deployment |
| **Architecture** | Multi-container | Separate backend/frontend containers |
| **Network** | host.docker.internal | Backend reaches host Ollama |

---

## Project Structure

```
customer_support_agent/
|-- docker-compose.yml
|-- README.md
|-- backend/
|   |-- Dockerfile, requirements.txt, .env.example
|   |-- app/
|   |   |-- main.py              # FastAPI app + lifespan
|   |   |-- config/settings.py   # All env vars typed here
|   |   |-- agents/state.py      # AgentState TypedDict
|   |   |-- agents/prompts.py    # System prompts for agent + RAG
|   |   |-- graph/workflow.py    # LangGraph StateGraph definition
|   |   |-- graph/nodes.py       # Node implementations
|   |   |-- graph/routing.py     # Routing functions (read-only state)
|   |   |-- tools/               # 11 LangChain tools
|   |   |-- rag/                 # documents, embeddings, vectorstore, retriever
|   |   |-- database/            # ORM models, seed data, async engine
|   |   |-- services/            # Business logic (orders, approvals, refunds)
|   |   |-- guardrails/          # Input + output safety checks
|   |   |-- api/routes/          # chat, orders, approvals, customers
|   |   |-- middleware/          # Observability (request ID + timing)
|   |   +-- utils/               # Structured logging
|   |-- scripts/seed_database.py
|   |-- tests/
|   +-- chroma_db/               # Persisted vector store (auto-created)
|-- frontend/
|   |-- Dockerfile, package.json
|   |-- app/page.tsx             # Home: customer selector
|   |-- app/chat/page.tsx        # Chat UI
|   |-- app/orders/page.tsx      # Order lookup
|   |-- app/approvals/page.tsx   # Approvals dashboard
|   |-- components/chat/ChatWindow.tsx
|   +-- lib/api.ts               # Typed API client
+-- data/
    |-- policies/                # refund, return, cancellation, shipping, warranty
    +-- faq/faq.md
```

---

## Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| **Docker** | 20.10+ | Docker Desktop or Docker Engine |
| **Docker Compose** | 2.0+ | Included with Docker Desktop |
| **Ollama** | 0.3+ | Install from ollama.ai |
| **Disk Space** | ~4 GB | Backend + Frontend + Ollama models |

> No Python or Node.js installations are needed on the host -- everything runs
> inside Docker containers. The only host requirement is Ollama.

---

## Quick Start

### 1. Install and start Ollama

```bash
# Install Ollama (macOS/Linux)
curl -fsSL https://ollama.ai/install.sh | sh
# Or download from https://ollama.ai for Windows

# Pull required models (~2 GB download)
ollama pull llama3.2
ollama pull nomic-embed-text

# Start Ollama (runs on port 11434 by default)
ollama serve
```

### 2. Clone and start the stack

```bash
git clone <repo-url>
cd customer_support_agent
docker compose up -d --build    # First run takes ~2 min
```

### 3. Verify it works

```bash
curl http://localhost:8000/health
# -> {"status":"healthy","service":"techkart-ai-support"}

curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is your refund policy?", "customer_id": "CUS1001"}'

# Open the frontend -> http://localhost:3000
```

### 4. Test the refund flow end-to-end

```bash
# Step A: Request a refund
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "I want a refund for TK10001. Cracked screen.", "customer_id": "CUS1001"}'

# Step B: Check pending approvals
curl http://localhost:8000/api/v1/approvals/pending

# Step C: Approve (use thread_id from Step A)
curl -X POST http://localhost:8000/api/v1/approvals/{thread_id}/decide \
  -H "Content-Type: application/json" \
  -d '{"decision": "approve", "decided_by": "SUPPORT_AGENT"}'
```

### 5. Stop the stack

```bash
docker compose down          # Stop (data preserved)
docker compose down -v       # Stop + delete volumes (fresh start)
```


---

## Environment Variables Reference

All variables are set in `docker-compose.yml`. Override via `.env` file or exports.

### LLM Configuration

| Variable | Default | Description |
|---|---|---|
| `LLM_PROVIDER` | `ollama` | LLM provider: `ollama` or `openai` |
| `OLLAMA_BASE_URL` | `http://host.docker.internal:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `llama3.2` | Ollama chat model name |
| `OLLAMA_EMBEDDING_MODEL` | `nomic-embed-text` | Ollama embedding model |
| `MODEL_NAME` | `gpt-4o-mini` | OpenAI model (only when LLM_PROVIDER=openai) |
| `MODEL_TEMPERATURE` | `0.1` | LLM temperature |
| `OPENAI_API_KEY` | *(empty)* | OpenAI API key (only when LLM_PROVIDER=openai) |

### Embedding Configuration

| Variable | Default | Description |
|---|---|---|
| `EMBEDDING_PROVIDER` | `ollama` | Provider: `ollama`, `openai`, or `chroma` |
| `EMBEDDING_MODEL` | `nomic-embed-text` | Embedding model name |

### Database, Server, and Tracing

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite+aiosqlite:///./techkart.db` | Async SQLite URL |
| `CHROMA_PERSIST_DIR` | `./chroma_db` | ChromaDB storage directory |
| `HOST` | `0.0.0.0` | Backend bind address |
| `PORT` | `8000` | Backend port |
| `ENVIRONMENT` | `development` | Environment name |
| `CORS_ORIGINS` | `http://localhost:3000, http://localhost:5173` | CORS origins |
| `LANGSMITH_TRACING` | `true` | Enable LangSmith tracing |
| `LANGSMITH_API_KEY` | *(empty)* | LangSmith API key (optional) |
| `LANGSMITH_PROJECT` | `techkart-support-agent` | LangSmith project name |

---

## Changing the LLM (Chat) Model

The LLM is used in two places: the **agent node** (tool-calling) and the
**RAG node** (policy Q&A). Both use `get_llm()` in `backend/app/graph/nodes.py`.

### Where the LLM is configured

| Layer | File | Setting |
|---|---|---|
| **Settings (typed)** | `backend/app/config/settings.py` | `ollama_model` (alias OLLAMA_MODEL) |
| **LLM instantiation** | `backend/app/graph/nodes.py` -> `get_llm()` | Reads llm_provider to pick ChatOllama or ChatOpenAI |
| **Docker env** | `docker-compose.yml` | OLLAMA_MODEL, MODEL_NAME env vars |
| **System prompt** | `backend/app/agents/prompts.py` | SYSTEM_PROMPT (works with any chat model) |

### To change the Ollama chat model

**Step 1:** Pull the new model on your host:
```bash
ollama pull llama3.1:8b       # or any other model
ollama pull mistral            # or Mistral
ollama pull qwen2.5:14b       # or Qwen
```

**Step 2:** Set the environment variable (pick ONE method):

Method A -- .env file (recommended):
```bash
echo 'OLLAMA_MODEL=llama3.1:8b' > .env
```

Method B -- Docker Compose: edit docker-compose.yml, change OLLAMA_MODEL value.

Method C -- Inline:
```bash
OLLAMA_MODEL=llama3.1:8b docker compose up -d
```

**Step 3:** Restart (no rebuild needed):
```bash
docker compose restart backend
```

> **IMPORTANT:** The model must support **function/tool calling** to work as the
> agent. Models like llama3.2, llama3.1, mistral, qwen2.5, and gemma2 support
> tool calling via Ollama. Models without tool support will fail.

### To switch to OpenAI

```bash
echo 'LLM_PROVIDER=openai' >> .env
echo 'OPENAI_API_KEY=sk-your-key-here' >> .env
echo 'MODEL_NAME=gpt-4o-mini' >> .env
docker compose up -d --build    # langchain-openai already in requirements.txt
```

### To use a remote Ollama server (GPU machine)

```bash
echo 'OLLAMA_BASE_URL=http://192.168.1.100:11434' >> .env
docker compose restart backend
```

---

## Changing the Embedding Model

Embeddings are used by the RAG pipeline to vectorize policy documents and
retrieve relevant chunks for customer questions.

### Where embeddings are configured

| Layer | File | Setting |
|---|---|---|
| **Settings** | `backend/app/config/settings.py` | `embedding_provider`, `embedding_model` |
| **Embedding factory** | `backend/app/rag/embeddings.py` -> `get_embeddings()` | Returns LangChain Embeddings object |
| **Vector store** | `backend/app/rag/vectorstore.py` -> `get_vectorstore()` | Calls get_embeddings(), seeds on first run |
| **Docker env** | `docker-compose.yml` | EMBEDDING_PROVIDER, EMBEDDING_MODEL |

### Changing the Ollama embedding model

**Step 1:** Pull the new model:
```bash
ollama pull mxbai-embed-large      # 670M params, 1024 dims
ollama pull all-minilm             # 33M params, 384 dims
ollama pull snowflake-arctic-embed # Good quality
```

**Step 2:** Set environment variables:
```bash
echo 'EMBEDDING_MODEL=mxbai-embed-large' >> .env
echo 'OLLAMA_EMBEDDING_MODEL=mxbai-embed-large' >> .env
```

**Step 3:** Delete ChromaDB (embeddings must be regenerated with new model):
```bash
docker compose down
rm -rf backend/chroma_db
docker compose up -d
```

> **CRITICAL:** You MUST delete `backend/chroma_db` when changing embedding
> models. Different models produce incompatible vector dimensions.

### Switching to OpenAI embeddings

```bash
echo 'EMBEDDING_PROVIDER=openai' >> .env
echo 'EMBEDDING_MODEL=text-embedding-3-small' >> .env
echo 'OPENAI_API_KEY=sk-your-key-here' >> .env
rm -rf backend/chroma_db
docker compose up -d --build
```

### Switching to ChromaDB built-in ONNX embeddings

```bash
echo 'EMBEDDING_PROVIDER=chroma' >> .env
rm -rf backend/chroma_db
docker compose up -d
```


---

## Switching Between Providers

| Current State | Desired State | What to Change | Rebuild? |
|---|---|---|---|
| Ollama LLM | OpenAI LLM | `LLM_PROVIDER=openai` + `OPENAI_API_KEY` + `MODEL_NAME` | first time only |
| OpenAI LLM | Ollama LLM | `LLM_PROVIDER=ollama` + `OLLAMA_MODEL` | no |
| Ollama embeddings | OpenAI embeddings | `EMBEDDING_PROVIDER=openai` + `EMBEDDING_MODEL` | yes |
| Ollama embeddings | Chroma ONNX | `EMBEDDING_PROVIDER=chroma` | yes |
| Chroma ONNX | Ollama embeddings | `EMBEDDING_PROVIDER=ollama` + `OLLAMA_EMBEDDING_MODEL` | no |
| Local Ollama | Remote Ollama | `OLLAMA_BASE_URL=http://<ip>:11434` | no |

> The **LLM provider** and **embedding provider** are independent switches.
> You can mix-and-match: Ollama chat + OpenAI embeddings works.

### Supported Combinations

| LLM Provider | Embedding Provider | Works? | Notes |
|---|---|---|---|
| ollama | ollama | Yes | Default fully-local setup |
| ollama | chroma | Yes | Chroma ONNX local embeddings |
| ollama | openai | Yes | Needs API key for embeddings only |
| openai | ollama | Yes | Needs API key for chat only |
| openai | openai | Yes | Fully cloud |
| openai | chroma | Yes | OpenAI chat + local embeddings |

---

## LangGraph Workflow Deep-Dive

### Graph shape

```
 START
   |
   v
[guardrails]  -> validates input, checks PII, classifies intent
   |
   v
[agent]       -> LLM with tools; loops while tool_calls pending
   |
   +--(category: policy/info)--> [rag]  ----------------------> back to [agent]
   |
   +--(refund requested)------> [refund_tools] --> [risk eval] --> [create_approval]
   |                                                                   |
   |                                                                   v
   |                                                            [human_approval]  <-- awaits DB decision
   |                                                                   |
   |                                                                   v
   |                                                            [apply_approval] --> [agent]
   |
   +--(support request)--------> [create_ticket] --> back to [agent]
   |
   v
  END
```

### Node reference

| Node | File | Purpose |
|---|---|---|
| `guardrails` | `app/graph/nodes.py` | Validate input, detect PII, classify intent category |
| `agent` | `app/graph/nodes.py` | Main LLM loop with 11 tools; stops at MAX_ITERATIONS |
| `rag` | `app/graph/nodes.py` | Retrieve policy chunks, synthesize answer from policies |
| `refund_tools` | `app/tools/refund_tools.py` | Initiate refund, evaluate eligibility & risk |
| `create_approval` | `app/graph/nodes.py` | Insert approval record into SQLite |
| `create_ticket` | `app/graph/nodes.py` | Insert support ticket into SQLite |
| `human_approval` | `app/graph/nodes.py` | Poll approval decision (approve/reject/edit) |
| `apply_approval` | `app/graph/nodes.py` | Apply approved refund to the order |

### Edge routing

| From | To | Condition |
|---|---|---|
| START | guardrails | always |
| guardrails | agent / rag / refund / ticket | determined by intent category |
| agent | END | no tool calls remain |
| agent | agent | tool calls remain (loop, capped) |
| rag | agent | always return to agent after RAG |
| refund path | human_approval | refund is risky (flagged) |
| human_approval | apply_approval | decision == approve |
| apply_approval | agent | continue conversation with result |
| human_approval | agent | decision == reject/edit |

The graph is compiled in `app/graph/workflow.py` using `StateGraph(AgentState)`.
State is defined in `app/agents/state.py` as a TypedDict:
messages, customer_id, thread_id, category, approval_pending, etc.


---

## Tools Reference

The agent has **11 tools** across 5 files.

### `backend/app/tools/order_tools.py`

| Tool | Description | Key Arguments |
|---|---|---|
| `lookup_orders` | List orders for a customer | `customer_id` |
| `lookup_order_details` | Full details of one order | `order_id` |
| `track_order` | Status + status timeline | `order_id` |

### `backend/app/tools/shipping_tools.py`

| Tool | Description | Key Arguments |
|---|---|---|
| `get_shipping_status` | Shipping status | `order_id` |
| `get_shipping_address` | Fulfilment address | `order_id` |
| `change_shipping_address` | Update address (used by approvals) | `order_id`, `new_address` |

### `backend/app/tools/refund_tools.py`

| Tool | Description | Key Arguments |
|---|---|---|
| `initiate_refund` | Start a refund request | `order_id`, `reason`, `amount` |
| `evaluate_refund_eligibility` | Check refund policy eligibility | `order_id` |
| `check_refund_status` | Refund status for an order | `order_id` |
| `get_refund_defaulted` | Default refund amount per policy | `order_id`, `reason` |

### `backend/app/tools/customer_tools.py`

| Tool | Description | Key Arguments |
|---|---|---|
| `lookup_customer_by_phone` | Find customer by phone | `phone` |

### `backend/app/tools/support_tools.py`

| Tool | Description | Key Arguments |
|---|---|---|
| `create_support_ticket` | Create ticket | `customer_id`, `order_id`, `issue`, `priority` |

> All tools are registered via `@tool` decorators and bound to the LLM using
> `llm.bind_tools(tools)` in `app/graph/nodes.py` -> `get_agent()`.

---

## RAG Pipeline

### Flow

```
data/policies/*.md  data/faq/faq.md
        |
        v
[DocumentLoader + SplitMarkdown]  (rag/documents.py)
        |
        v
[get_embeddings()]  (rag/embeddings.py)
   ollama | openai | chroma
        |
        v
[get_vectorstore()]  (rag/vectorstore.py)
   ChromaDB, persists to ./chroma_db
   Seeds only when collection is empty
        |
        v
[MessagesRetriever]  (rag/retriever.py)
   Used by RAG node to fetch top-k chunks
```

### Files

| File | Responsibility |
|---|---|
| `backend/app/rag/documents.py` | `get_documents()` -- loads policy + FAQ markdown files |
| `backend/app/rag/embeddings.py` | `get_embeddings()` -- returns embeddings object for provider |
| `backend/app/rag/vectorstore.py` | `get_vectorstore()` -- persistent Chroma, auto-seed, top-k |
| `backend/app/rag/retriever.py` | `create_retriever()` -- wraps store as messages retriever |

### Documents indexed

| Document | Source |
|---|---|
| Refund policy | `data/policies/refund_policy.md` |
| Return policy | `data/policies/return_policy.md` |
| Cancellation policy | `data/policies/cancellation_policy.md` |
| Shipping policy | `data/policies/shipping_policy.md` |
| Warranty policy | `data/policies/warranty_policy.md` |
| FAQ | `data/faq/faq.md` |

### RAG prompt

Defined in `backend/app/agents/prompts.py` (RAG_PROMPT). Instructs the model to
answer **only** from retrieved chunks, cite the source document, and say
"I don't know" when nothing relevant is found.

---

## Human-in-the-Loop (HITL) Approval Flow

```
 Customer asks for a refund
        |
        v
[agent] calls initiate_refund
        |
        v
[evaluate_refund_eligibility] -> eligible? amount computed
        |
        v
[risk evaluation]  -> risky if amount > threshold or flagged pattern
        |
        +-- NOT risky ---> refund applied immediately, message returned
        |
        v
     [risky]
        |
        v
[create_approval_request]
  INSERT INTO approvals (status='pending', thread_id, ...)
        |
        v
[human_approval node]  -- waits; workflow checks approval record
        |
        +-- approve --> [apply_approval] updates order refund status
        |
        +-- reject  --> message "Your refund was declined"
        |
        +-- edit    --> amounts adjusted, then applied
```

### Approval lifecycle

| Status | Meaning | Next action |
|---|---|---|
| `pending` | Awaiting human review | approve / reject / edit via UI |
| `approved` | Approved, under processing | order refund status updated |
| `rejected` | Declined | customer informed by agent |
| `cancelled` | Cancelled by requester | no effect |

### Database schema (simplified)

```sql
-- ApprovalRequest
id, thread_id, customer_id, order_id,
refund_amount, status, reason,
available_balance, warranty, insurance,
created_at, decided_at, decided_by
```


---

## API Reference

Base URL: `http://localhost:8000`. All routes are prefixed with `/api/v1`.

### Chat

| Method | Endpoint | Body | Returns |
|---|---|---|---|
| `POST` | `/chat` | `{message, customer_id, thread_id?}` | `{response, thread_id, category?, approval_pending?}` |
| `POST` | `/chat/history` | `{thread_id}` | `{messages: [...]}` |
| `GET` | `/chat/health` | -- | `{status: "ok"}` |

### Orders

| Method | Endpoint | Params | Returns |
|---|---|---|---|
| `GET` | `/orders/customers/{customer_id}/orders` | path | Order list |
| `GET` | `/orders/{order_id}` | path | Order detail |

### Approvals

| Method | Endpoint | Params / Body | Returns |
|---|---|---|---|
| `GET` | `/approvals` | `status` query (`pending`/`all`) | Approval records |
| `GET` | `/approvals/pending` | -- | Pending approvals |
| `POST` | `/approvals/{thread_id}/decide` | `{decision, decided_by, edit_amount?}` | Updated approval |

### Customers

| Method | Endpoint | Body | Returns |
|---|---|---|---|
| `GET` | `/customers/{customer_id}` | path | Customer record |
| `GET` | `/customers/phone/{phone}` | path | Customer by phone |

### Misc

| Method | Endpoint | Returns |
|---|---|---|
| `GET` | `/health` | `{status, service}` |
| `GET` | `/api-tools` | Docs / tool list |

> Swagger UI available at `http://localhost:8000/docs`.

---

## Frontend Pages

| Route | File | Purpose |
|---|---|---|
| `/` | `frontend/app/page.tsx` | Home: pick a demo customer to continue as |
| `/chat` | `frontend/app/chat/page.tsx` | Chat window with streaming UX, thread management |
| `/orders` | `frontend/app/orders/page.tsx` | Order lookup + details for selected customer |
| `/approvals` | `frontend/app/approvals/page.tsx` | Approve/reject/edit pending refunds |

### Chat page features

- Customer selectable from dropdown (list fetched from `/customers`)
- Message list from `ChatWindow.tsx`
- Thread id stored per customer, new thread starts a new conversation
- Shows approval-creating responses with a notice when action is pending

### Approvals page features

- Table of pending approvals with: customer, order, amount, reason, timestamp
- **Approve** button -> POST decide `{decision: "approve"}`
- **Reject** button -> POST decide `{decision: "reject"}`
- **Edit amount + approve** -> POST decide `{decision: "approve", edit_amount: X}`
- UI auto-refreshes the list after each action

---

## Seeded Demo Data

Data is seeded on container startup (`app/database/seed.py`) and can be
re-seeded manually with:

```bash
python backend/scripts/seed_database.py
```

| Entity | Sample Values | Notes |
|---|---|---|
| **Customers** | CUS1001 (Rahul Sharma), CUS1002, CUS1003 | Phone, status, credit balance |
| **Orders** | TK10001..TK10006 | Various statuses: shipped, delivered, processing |
| **Order Items** | iPhone 15 Pro Max, Samsung Galaxy S24, etc. | Price, quantity, eligible_for_refund |
| **Approvals** | pending | Created via the refund flow |

### Example customer

| Field | Value |
|---|---|
| customer_id | CUS1001 |
| name | Rahul Sharma |
| phone | 9876543210 |
| status | active |
| available_balance | 75000.0 |

### Example order

| Field | Value |
|---|---|
| order_id | TK10001 |
| customer_id | CUS1001 |
| total_amount | 134900.0 |
| status | delivered |
| warranty | no |

> Every order ships with 2 items, item-level warranty flags, and a status
> timeline used by `track_order`.


---

## Guardrails

Two layers protect the agent. Both live in `backend/app/guardrails/`.

### Input guardrails (`input_guardrails.py`)

| Check | What it blocks / flags |
|---|---|
| **Empty input** | Rejects blank messages |
| **PII detection** | Flags emails, phone numbers, Aadhaar-like 12-digit numbers, IPs |
| **Prompt injection** | Detects "ignore previous instructions", system prompt override attempts |
| **Sensitive categories** | Flags violence, self-harm, hate speech requests |
| **Rag-only questions** | Routes company-external questions to RAG, not the agent |
| **Confidence handling** | Low-confidence inputs get a guardrail fallback response |

Failed validation returns a fixed message and **does not** invoke the LLM.

### Output guardrails (`output_guardrails.py`)

| Check | What it does |
|---|---|
| **Content safety** | Flags harmful content in the model response |
| **Sensitive data** | Detects PII leakage in generated text |
| **Fallback** | Replaces flagged output with a safe canned message |

### How it ties into the graph

The guardrail node runs first and decides where to route:

```python
# app/graph/nodes.py  (simplified)
def guardrail_node(state):
    validation = validate_input(state["messages"][-1].content, state.get("customer_id"))
    if not validation["passed"]:
        return {"messages": [fallback_message], "category": "guardrail"}
    return {"category": validation["category"], "is_pii_detected": validation["is_pii_detected"]}
```

---

## Troubleshooting

### Ollama connection refused (backend can't reach Ollama)

**Symptom:** `ConnectionRefusedError: [Errno 111] ... host.docker.internal:11434`

**Fix:**
```bash
# Confirm Ollama is running on the host
curl http://localhost:11434   # -> "Ollama is running"

# Confirm the model is pulled
ollama list                   # llama3.2 + nomic-embed-text present?

# On Linux, host.docker.internal needs extra_ hosts in docker-compose.yml:
#   extra_hosts:
#     - "host.docker.internal:host-gateway"
```

### Ollama model not found

**Symptom:** `model 'llama3.2' not found`

**Fix:** `ollama pull llama3.2` and `ollama pull nomic-embed-text`.

### Model does not support tool calls

**Symptom:** Agent repeats "I cannot use tools" or returns malformed tool JSON.

**Fix:** Use a tool-calling-capable model (llama3.2, llama3.1, mistral, qwen2.5, gemma2).
The default `llama3.2` supports tools via Ollama.

### Changed embedding model but retrievals are wrong

**Symptom:** RAG returns garbage or errors about mismatched dimension.

**Fix:** Delete the persisted Chroma store and re-seed:
```bash
docker compose down
rm -rf backend/chroma_db
docker compose up -d
```

### Port 8000 or 3000 already in use

**Fix:**
```bash
docker compose down
# or change HOST_PORT in docker-compose.yml
```

### Slow first message

The first chat message warms up the Ollama models and seeds ChromaDB.
Subsequent messages are fast. Consider pre-pulling and pre-warming:

```bash
curl -X POST http://localhost:11434/api/generate -d '{"model": "llama3.2", "prompt": "hi", "stream": false}'
```

### Container starts but frontend blank

Check that `NEXT_PUBLIC_API_URL` (or the API base in `frontend/lib/api.ts`)
points at `http://localhost:8000`.

---

## Development Guide

### Run backend outside Docker

```bash
cd backend
python -m venv .venv
.venv/Scripts/activate          # Windows
source .venv/bin/activate       # macOS/Linux
pip install -r requirements.txt
python scripts/seed_database.py
uvicorn app.main:app --reload --port 8000
```

### Run frontend outside Docker

```bash
cd frontend
npm install
npm run dev                     # -> http://localhost:3000
```

### Run tests

```bash
cd backend
pytest tests/ -v                # uses fixtures, no external calls
```

### Project conventions

| Rule | Detail |
|---|---|
| Python | `app/` packages; async everywhere (fastapi + SQLAlchemy async) |
| Settings | All env vars typed in `app/config/settings.py`; never read `os.environ` elsewhere |
| State | Agent state lives in `app/agents/state.py`; pass data via state, not globals |
| Tools | One file per domain (`tools/order_tools.py`, etc.), decorated with `@tool` |
| Logging | Use `app/utils/logging.py` `logger = get_logger(__name__)` in every module |
| DB access | Via `app/database/session.py` async session factory |
| Frontend | TypeScript + Tailwind; API client centralized in `lib/api.ts` |
| Config | Never hardcode model names in code -- always through settings |

### Adding a new tool

1. Add the function in the right `tools/*.py` file with `@tool` decorator
2. Include it in the tool list passed to `get_agent()` in `app/graph/nodes.py`
3. The agent picks it up automatically -- no prompt changes needed (tool docs injected by LangChain)

### Adding a new policy document

1. Add a `.md` file under `data/policies/`
2. On next startup (or after `docker compose restart backend`), the RAG
   pipeline auto-embeds it into ChromaDB

---

## License

MIT License -- free to use, modify, and distribute for any purpose.
