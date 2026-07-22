# ResolveAI — Autonomous Customer Support Console

**ResolveAI** is a multi-tier, Mixture-of-Experts (MoE) customer support automation system. It features a **LangGraph-powered agentic backend** and a **Next.js frontend dashboard** to manage autonomous resolutions, confidence gating, and human-in-the-loop escalations.

> [!IMPORTANT]
> **Product Requirements & Production Design:** For the complete, formal engineering requirements, CRISPE prompt engineering templates, security protocols (OAuth2/JWT, rate limiting, AES-256), and enterprise microservices decoupling specifications, please refer to the official **[Product Requirements Document (PRD.md)](file:///c:/Users/SHASHI/Desktop/ResolveAI/PRD.md)**.
> 
> **Hackathon Submission Report & Working Process PDF**: Please see the **`submission_report.md`** and **`working_process.pdf`** documents in the repository root for our detailed evaluation criteria, latency analysis, and architectural walkthroughs.

---

## 🗺️ System Overview & Architecture

ResolveAI handles incoming customer queries through multiple communication channels (Email, Live Chat, Voice), automatically resolving low-risk, high-confidence requests while escalating complex or high-risk cases to a human support agent dashboard.

### High-Level Execution Pipeline

```mermaid
graph TD
    %% Define Channels and Intake
    Inbound["Incoming Query (Email, Chat, Voice)"] --> IntakeNode["[1] Intake Node (Normalize & Log)"]
    IntakeNode --> ClassifierNode["[2] Classifier Node (Intent & Risk)"]
    
    %% Context and Resolution
    ClassifierNode --> ContextNode["[3] Context Retriever (CRM & KB)"]
    ContextNode --> ResolutionNode["[4] Resolution Agent (MoE Routing)"]
    
    %% Gating
    ResolutionNode --> GatingNode{"[5] Confidence Gate"}
    
    %% Routing Decisions
    GatingNode -- "Confidence >= Threshold" --> AutoResolve["[6a] Auto-Execute Tools"]
    GatingNode -- "Confidence < Threshold (or Risk Flags)" --> EscalateQueue["[6b] Escalate to Human Console"]
    
    %% Human Action
    EscalateQueue --> HumanReview{"Human Console Review"}
    HumanReview -- "Approve / Edit" --> HumanExecute["Execute Tools & Reply"]
    HumanReview -- "Reject" --> Rejection["Send Rejection Message"]
    
    %% Outputs
    AutoResolve --> CustomerReply["Send Agent Reply to Customer"]
    HumanExecute --> CustomerReply
    Rejection --> CustomerReply
```

---

## ⚙️ Core Technical Components

### 1. LangGraph State Machine Flow
The backend processing pipeline is modeled as a stateful graph using **LangGraph** (see `backend/app/graph.py`).

*   **`intake_node`**: Registers the ticket and incoming customer message into the database and initializes the audit trace.
*   **`classify_node`**: Leverages a low-cost LLM to identify the customer's intent, extract key entities (such as order IDs or subscription IDs), and check for risk flags (angry language, legal threats, high refund amount).
*   **`context_retriever_node`**: Looks up the customer's CRM profile, including order history and subscriptions, and queries the local SQLite knowledge base for relevant FAQ articles.
*   **`resolve_node`**: Routes the request to the appropriate LLM tier based on intent and risk. The chosen LLM formulates a draft response and proposes system actions (like issuing refunds or canceling subscriptions).
*   **`gate_node`**: Decides whether the resolution meets the confidence threshold. The threshold is intent-specific:
    *   `order_status`: `0.80`
    *   `refund_request`: `0.85`
    *   `shipping_delay`: `0.80`
    *   `subscription_cancel`: `0.90` (Strict escalation policy for user retention)
    *   `account_access`: `0.80`
    *   `general_faq`: `0.80`
*   **`execute_node`**:
    *   **Auto-Resolved**: Executes database actions (refunding orders or canceling subscriptions) automatically and replies directly.
    *   **Escalated**: Suspends automatic executions, sets the ticket status to `Escalated`, and packages the draft response and proposed actions to the Human Console.

---

### 2. Mixture-of-Experts (MoE) Model Routing
To optimize API costs and response latency, ResolveAI uses a three-tier model routing hierarchy (see `backend/app/llm.py`):

| Tier | Model Class | Cost (Input/Output per 1K) | Primary Use Cases |
| :--- | :--- | :--- | :--- |
| **Tier 0** | **Haiku-class (Cheap)** | $0.00025 / $0.00125 | Classification, General FAQs, simple queries |
| **Tier 1** | **Sonnet-class (Standard)** | $0.00300 / $0.01500 | Standard transactions (Order Status, low-value refunds, shipping delay) |
| **Tier 2** | **Opus-class (Frontier)** | $0.01500 / $0.07500 | High-risk scenarios (Legal threats, angry customers, high-value refunds, low classification confidence) |

---

### 3. Cryptographic Audit Ledger
For compliance, traceability, and safety, ResolveAI implements a **cryptographic hash chain** to log agent decisions. Every state transition in the LangGraph writes an immutable block to the `audit_logs` database table.

The hash of each log entry is mathematically chained to the previous log entry's hash using SHA-256:

$$\text{Current Hash} = \text{SHA-256}(\text{prev\_hash} \mid \text{ticket\_id} \mid \text{node} \mid \text{input\_summary} \mid \text{model\_used} \mid \text{tokens} \mid \text{cost} \mid \text{confidence} \mid \text{action\_taken})$$

This creates a verifiable **audit trail** that ensures execution traces cannot be retroactively tampered with. If any record is modified, the hash verification chain breaks. The Next.js dashboard validates this chain in real-time, showing a green checkmark next to verified cryptographic logs.

---

### 4. Enterprise DevOps & Security Hardening
ResolveAI employs enterprise-grade infrastructure configurations:

*   **CI/CD Quality Gates**: Fully automated GitHub Actions pipelines (`.github/workflows/ci.yml` and `cd.yml`) running `pytest` coverage matrices and automated Docker deployments on release tags.
*   **Database Reliability**: The backend seamlessly supports local development using `sqlite` while connecting to scalable `Supabase PostgreSQL` in production environments through dynamic configuration injection via `pydantic-settings`.
*   **API Security**: Implements strict `SecurityHeadersMiddleware`, Proxy IP-aware `RateLimitMiddleware`, and locked-down CORS policies inside `backend/app/main.py`.
*   **Dependabot**: Automated weekly vulnerability scanning and dependency updates for both Node.js (npm) and Python (pip) ecosystems.

---

## 🖥️ Next.js Frontend Dashboard Features

The dashboard provides a simulator and console for testing and human verification:

1.  **Global Metrics Bar**: Displays real-time statistics including Trust Autonomy Rate, Total Cost Saved, and Average Response Time.
2.  **Channel Simulators**: Includes an Email, Voice, and Live Chat simulator for deep, real-time testing of LangGraph behaviors and AI responses.
3.  **Human Console Interventions**: Allows human agents to review escalated tickets, inspect customer transaction histories, and safely click to **Approve**, **Edit**, or **Reject** proposed agent actions.

---

## 🚀 Running the Project Locally

### 1. Backend Setup (FastAPI)
1.  Navigate to the backend folder:
    ```bash
    cd backend
    ```
2.  Activate the virtual environment:
    *   **Windows (PowerShell)**:
        ```powershell
        .\.venv\Scripts\Activate.ps1
        ```
    *   **macOS / Linux**:
        ```bash
        source .venv/bin/activate
        ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Seed the SQLite database with mock customers, orders, and knowledge articles:
    ```bash
    python seed.py
    ```
5.  Start the FastAPI Uvicorn server:
    ```bash
    python -m uvicorn app.main:app --reload --port 8000
    ```

### 2. Frontend Setup (Next.js)
1.  Navigate to the frontend folder:
    ```bash
    cd ../frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Start the dev server:
    ```bash
    npm run dev
    ```
4.  Open your browser and navigate to [http://localhost:3000](http://localhost:3000).

### 3. Automated Testing
Run the complete backend test suite (unit tests and LangGraph simulations):
```bash
cd backend
python -m pytest test_main.py test_agent.py -v
```
