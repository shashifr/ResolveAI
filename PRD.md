# Product Requirements Document (PRD)
## ResolveAI: Enterprise Multi-Tier Customer Support Agent

This document outlines the product requirements, architectural specifications, prompt engineering frameworks, security protocols, and compliance standards for **ResolveAI**—an enterprise-grade, autonomous customer support agent and human-in-the-loop escalation system.

---

## 1. Requirements Traceability Matrix

| Requirement ID | Component | Description | Measurable Acceptance Criteria | Priority |
| :--- | :--- | :--- | :--- | :--- |
| **REQ-SEC-001** | Security | Next.js Console & API Gateway Auth | All Next.js calls must route through the FastAPI Gateway. Requests must include a valid OAuth2/JWT token in the `Authorization` header. Unauthorized calls must return HTTP 401. | High |
| **REQ-SEC-002** | Security | Customer PII Encryption | Enforce AES-256-GCM encryption for all sensitive customer data (`Customer.email`, `Customer.phone`) at rest, and TLS 1.3 transit security. | High |
| **REQ-SEC-003** | Security | API Rate Limiting | The FastAPI Gateway must enforce a Token Bucket rate limit of 60 requests per minute per IP address / authenticated session. | High |
| **REQ-ARC-001** | Architecture | Production Database Migration | Replace the local SQLite database with PostgreSQL configured for connection pooling (`SQLAlchemy` with `pgbouncer`), supporting up to 500 concurrent connections. | High |
| **REQ-ARC-002** | Architecture | Microservices Decoupling | Decouple the monolithic LangGraph state machine into independent, stateless worker services communicating asynchronously via a message broker (RabbitMQ/Kafka). | High |
| **REQ-PRM-001** | Prompts | CRISPE Classifier Node | Define the Classifier Node system prompt using the CRISPE framework to extract intents and entities into a validated JSON structure with a strict schema. | Medium |
| **REQ-PRM-002** | Prompts | CRISPE MoE Router Node | Define the MoE Router system prompt using the CRISPE framework to select model tiers (0, 1, or 2) and output structured JSON. | Medium |
| **REQ-OBS-001** | Observability | OpenTelemetry Logging & Tracing | Integrate OpenTelemetry SDK to export trace spans (OTLP format) across FastAPI, LangGraph, and worker boundaries, including correlation IDs. | Medium |
| **REQ-OBS-002** | Observability | Token Tracking & Financial Audit | Log exact prompt/completion token usage and cost per ticket in the cryptographic ledger to enable real-time financial audit. | Medium |

---

## 2. API Security & Access Control

### 2.1 OAuth2 / JWT Authentication Flow
The FastAPI Gateway acts as the central security sentinel. The Next.js dashboard never directly queries the database. It authenticates users against an identity provider, receives a JWT, and sends the token with every request.

```
+------------------+             +-----------------+             +-------------------+
| Next.js Console  |             | FastAPI Gateway |             | Identity Provider |
+------------------+             +-----------------+             +-------------------+
        |                                 |                                 |
        |---- 1. POST /api/v1/login ----->|                                 |
        |                                 |---- 2. Authenticate User ------>|
        |                                 |<--- 3. Return ID & Roles -------|
        |<--- 4. Return JWT Access Token -|                                 |
        |                                 |                                 |
        |---- 5. GET /api/v1/tickets ---->| (Validate JWT Signature &       |
        |        Authorization: Bearer <K>|  verify 'support_agent' role)   |
        |                                 |                                 |
```

*   **JWT Payload Schema:**
    ```json
    {
      "sub": "agent_12345",
      "name": "Jane Doe",
      "role": "support_agent",
      "permissions": ["tickets:read", "tickets:write", "refund:approve"],
      "exp": 1782240000
    }
    ```

### 2.2 Rate Limiting (Token Bucket Algorithm)
The FastAPI Gateway leverages Redis to implement a distributed Token Bucket rate limiter.
*   **Capacity:** 100 tokens per user key.
*   **Refill Rate:** 1 token per second.
*   **Redis Keys:** `rate_limit:{user_id}:tokens` (float) and `rate_limit:{user_id}:last_updated` (timestamp).

### 2.3 Cryptographic PII Protection (GDPR Compliance)
*   **Data at Rest:** Customer emails and phone numbers are encrypted before database insertion using **AES-256-GCM** with a master key stored in Google Cloud Secret Manager.
*   **Data in Transit:** Enforced TLS 1.3 for all HTTP/WebSocket traffic. Older ciphers (TLS 1.0, 1.1, 1.2) are rejected at the gateway.

---

## 3. Decoupled Microservices Architecture

To prevent architectural coupling, ResolveAI is partitioned into stateless, event-driven workers. 

### 3.1 Asynchronous Event Topology
Instead of a single blocking thread executing all LangGraph nodes, ticket progress is driven by message queues.

```
       +------------------+
       | FastAPI Gateway  |
       +------------------+
                | (Publish "ticket.ingested")
                v
       +------------------+
       |   RabbitMQ /     |
       |  Kafka Broker    |
       +------------------+
         /      |       \
        /       |        \
       v        v         v
+----------+ +----------+ +----------+
|Classifier| |Retriever | |Resolver  |
| Worker   | | Worker   | | Worker   |
+----------+ +----------+ +----------+
```

1.  **FastAPI Gateway** writes raw tickets to Postgres, publishes a `ticket.ingested` event, and returns HTTP 202 to the customer channel.
2.  **Classifier Worker** consumes `ticket.ingested`, runs the classification LLM, writes flags to the database, and publishes `ticket.classified`.
3.  **Retriever Worker** consumes `ticket.classified`, queries embeddings and customer profile history, enriches the ticket state, and publishes `ticket.enriched`.
4.  **Resolver Worker** consumes `ticket.enriched`, invokes the MoE router, drafts response, evaluates the confidence gate, and either auto-resolves or flags for human approval.

### 3.2 SQLite to PostgreSQL Migration
To support production-level write concurrency and connection pooling, the system migrates to PostgreSQL:
*   **Connection Pooler:** `pgbouncer` running in transaction mode.
*   **Max Connections:** 500 active pool connections.
*   **ORM Integration:** SQLAlchemy configuration updated to use `postgresql+psycopg2` driver.

---

## 4. Prompt Engineering (CRISPE Framework)

All system prompts are designed using the **CRISPE** (Capacity, Role, Instruction, Schema, Power, Executive) framework to ensure output consistency.

### 4.1 Classifier Node Prompts

*   **Capacity & Role:** Act as an elite Customer Support Data Classifier with deep expertise in retail and software subscription operations.
*   **Instruction:** Analyze the incoming user query. Determine the primary intent, extract key identifiers (order numbers, subscription models), and flag potential operational risks (extreme anger, legal warnings, or high monetary refund claims).
*   **Schema (Output Format):** Strict JSON matching the schema below. No conversational wrappers or markdown backticks in the response.
*   **Power / Context:**
    *   Valid Intents: `order_status`, `refund_request`, `shipping_delay`, `subscription_cancel`, `account_access`, `general_faq`.
    *   Valid Risk Flags: `angry_language`, `legal_threat`, `high_refund_value` (if refund value is > $100).
*   **Executive Constraint:** Output ONLY valid JSON.

#### System Prompt Template
```
Capacity: Elite Classification Agent
Role: Customer Ticket Intent & Risk Evaluator
Instruction:
  You must parse the customer message and return a JSON object with:
  1. "intent": One of ["order_status", "refund_request", "shipping_delay", "subscription_cancel", "account_access", "general_faq"].
  2. "confidence": A float between 0.0 and 1.0 representing classification confidence.
  3. "extracted_entities": JSON object containing keys like "order_id" (format ORD-XXXX) or "refund_amount" (float).
  4. "risk_flags": List of strings containing any of ["angry_language", "legal_threat", "high_refund_value"].

Constraint: Do NOT include any intro or outro text. Do NOT wrap in code blocks.

Few-Shot Example:
Input: "I want a refund for order ORD-1234, this product is completely broken!"
Output: {
  "intent": "refund_request",
  "confidence": 0.98,
  "extracted_entities": {
    "order_id": "ORD-1234"
  },
  "risk_flags": ["angry_language"]
}
```

---

## 5. LLM Observability & Tracing

ResolveAI utilizes **OpenTelemetry** to trace requests end-to-end across API boundaries, worker processes, and LLM providers.

### 5.1 Observability Architecture

```
+-----------------+       +-------------------+       +-----------------------+
| FastAPI Gateway | ----> |  OTel Collector   | ----> | LangSmith / Phoenix   |
| & Worker Spans  |       | (OLTP receiver)   |       | (Telemetry Visualizer)|
+-----------------+       +-------------------+       +-----------------------+
```

1.  **Correlation ID Injection:** A unique UUID `X-Correlation-ID` is generated at the API Gateway intake and injected into the request header. It propagates down to RabbitMQ messages, database queries, and LLM logs.
2.  **OTel Collector:** The FastAPI app and workers send OTLP trace telemetry to an OpenTelemetry collector.
3.  **Visualizers:** Spans are aggregated in LangSmith or Arize Phoenix to track latency distributions, token sizes, and financial costs per ticket.

### 5.2 Financial Logging Schema
Every LLM call appends metrics to the cryptographic audit chain:
*   `model_name`: e.g., `gemini-1.5-flash`
*   `prompt_tokens`: Count of input tokens.
*   `completion_tokens`: Count of output tokens.
*   `cost_usd`: Calculated in real-time based on `MODEL_PRICING` tables.
