# Glow Goals AI Shopping Assistant

An AI-powered shopping assistant for **Glow Goals**, a UK-based Korean skincare Shopify store.
It helps customers find suitable products, get personalised recommendations, learn about
Korean skincare and ingredients, build routines, and get store/order support — grounded in the
store's real product catalog, not invented answers.

This is a portfolio project built step by step, with each milestone working and tested before
the next one starts. See [`PROJECT_LOG.md`](./PROJECT_LOG.md) for the full build log and the
current status of every milestone.

## Status

🚧 **Milestone 3 of 8 — Product recommendations grounded in the real Shopify catalog.** No
knowledge base, intent routing, or frontend yet.

## Architecture (target, built incrementally)

```
Customer
   │
React Chat Widget (standalone, embeddable)
   │
Backend API (a plain Lambda-style handler function, run locally and later deployed behind
AWS API Gateway + Lambda directly — no web framework in between)
   │
AI Orchestration Layer
   │
   ├── Gemini (LLM, behind a swappable provider interface)
   ├── Tools: search_products, search_knowledge, ... (Shopify Admin API + local knowledge base)
   └── Simple RAG over a small skincare knowledge base (ingredients, routines, FAQ)
```

Design principles carried over from the original architecture spec:

- **Product grounding** — recommendations only ever come from the real Glow Goals catalog via
  Shopify's Admin API, never invented.
- **Knowledge separation** — commerce data (Shopify), business/store policy info, and general
  skincare education are treated as distinct sources the assistant chooses between.
- **Provider flexibility** — the LLM is called through an interface, so the underlying model
  (Gemini first, others later) can change without touching application logic.
- **Serverless backend** — designed to run on AWS Lambda + API Gateway, no always-on server.

Scope for this build is intentionally trimmed from the original full spec (single LLM provider
to start, no hosted vector DB, no conversation database, manual AWS deploy before IaC). The
deferred pieces are listed at the bottom of `PROJECT_LOG.md` as future work.

## Repo layout (grows as milestones are built)

```
glow_goals_ai/
├── README.md        — this file
├── PROJECT_LOG.md    — build log, milestone tracker, and working rules for this project
├── .gitignore
└── backend/
    ├── handler.py             — Lambda-shaped entry point (chat request in, chat reply out)
    ├── providers/
    │   ├── base.py            — the AIProvider interface every LLM provider implements
    │   └── gemini_provider.py — Gemini implementation, including the tool-calling loop
    ├── shopify_client.py      — OAuth token exchange + real Shopify product search
    ├── tools.py               — the search_products tool definition + dispatcher
    ├── requirements.txt
    └── .env.example           — template for local secrets (Gemini + Shopify credentials)
```
