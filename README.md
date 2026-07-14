# Glow Goals AI Shopping Assistant

An AI-powered shopping assistant for **Glow Goals**, a UK-based Korean skincare Shopify store.
It helps customers find suitable products, get personalised recommendations, learn about
Korean skincare and ingredients, build routines, and get store/order support — grounded in the
store's real product catalog, not invented answers.

This is a portfolio project built step by step, with each milestone working and tested before
the next one starts. See [`PROJECT_LOG.md`](./PROJECT_LOG.md) for the full build log and the
current status of every milestone.

## Status

🚧 **Milestone 1 of 8 — Project scaffolding.** No backend or frontend code yet.

## Architecture (target, built incrementally)

```
Customer
   │
React Chat Widget (standalone, embeddable)
   │
Backend API (FastAPI locally → AWS Lambda + API Gateway later)
   │
AI Orchestration Layer
   │
   ├── Claude (LLM, behind a swappable provider interface)
   ├── Tools: search_products, search_knowledge, ... (Shopify Admin API + local knowledge base)
   └── Simple RAG over a small skincare knowledge base (ingredients, routines, FAQ)
```

Design principles carried over from the original architecture spec:

- **Product grounding** — recommendations only ever come from the real Glow Goals catalog via
  Shopify's Admin API, never invented.
- **Knowledge separation** — commerce data (Shopify), business/store policy info, and general
  skincare education are treated as distinct sources the assistant chooses between.
- **Provider flexibility** — the LLM is called through an interface, so the underlying model
  (Claude, and later others) can change without touching application logic.
- **Serverless backend** — designed to run on AWS Lambda + API Gateway, no always-on server.

Scope for this build is intentionally trimmed from the original full spec (single LLM provider
to start, no hosted vector DB, no conversation database, manual AWS deploy before IaC). The
deferred pieces are listed at the bottom of `PROJECT_LOG.md` as future work.

## Repo layout (grows as milestones are built)

```
glow_goals_ai/
├── README.md        — this file
├── PROJECT_LOG.md    — build log, milestone tracker, and working rules for this project
└── .gitignore
```
