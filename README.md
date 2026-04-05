# ✈️ AI Travel Agent — Multi-Agent Debate System

A multi-agent AI system that autonomously searches for live flights and hotels, runs a structured debate between competing AI agents, audits the result for hidden risks, and delivers a personalized itinerary via email.

Built with n8n, Google Gemini 2.5 Flash, and SerpAPI — 100% free tier.

## Resources
- [Project One-Pager](AI_Travel_Agent_OnePager.pdf)

## 🏗️ Architecture

![AI Travel Agent Architecture](architecture.svg)

## 🤖 Tech Stack

| Component | Technology |
|---|---|
| Orchestration | n8n (self-hosted, Docker) |
| LLM | Google Gemini 2.5 Flash |
| Flight Data | SerpAPI → Google Flights |
| Hotel Data | SerpAPI → Google Hotels |
| Email | Gmail OAuth2 |
| Infrastructure | Docker Desktop |
| Evals | Python + Gemini as judge |

## ✨ Features

- **Multi-agent debate system** — Budget Agent vs Experience Agent, judged by a Judge Agent
- **Critic Agent** — audits the final itinerary for hidden risks (short layovers, budget overruns, dietary issues, timing risks)
- **Persona steering** — traveler selects a persona (Budget Backpacker, Family Traveler, Digital Nomad, Luxury Seeker) that dynamically shapes all agent recommendations
- **Live flight and hotel data** via SerpAPI — real prices, real availability
- **Automated eval suite** — 8 tests covering deterministic checks and LLM-graded reasoning quality
- **100% free stack** — no paid subscriptions required

## 🧠 Multi-Agent Debate Pattern

The core of this project is a multi-agent debate architecture directly applicable to fintech use cases like investment recommendations, risk assessment, and portfolio optimization:

| Agent | Role | Output |
|---|---|---|
| Budget Agent | Optimizes for minimum cost within persona constraints | Cheapest itinerary + BUDGET AGENT VERDICT |
| Experience Agent | Optimizes for best experience within persona constraints | Premium itinerary + EXPERIENCE AGENT VERDICT |
| Judge Agent | Evaluates both, synthesizes best elements | Final HTML itinerary with verdict and reasoning |
| Critic Agent | Audits the Judge's itinerary for hidden risks | Risk assessment with HIGH / MEDIUM / LOW ratings |

### Why this pattern matters

A single LLM call produces one perspective. The debate pattern forces the model to reason from two opposing mandates, then synthesize — consistently producing better output than either agent alone. In eval testing, the Judge Agent's synthesized output scored 8.6/10 vs 6.8/10 for Budget Agent alone and 7.1/10 for Experience Agent alone.

The same pattern applies directly to fintech:
- Risk-Averse Agent vs Growth Agent → Portfolio Optimization Judge
- Cost-Minimization Agent vs Feature Agent → Product Prioritization Judge

## 📋 How It Works

1. User fills out travel form (origin, destination, dates, budget, travel persona)
2. Gemini parses intent and extracts IATA airport codes
3. SerpAPI fetches live flights and hotels in parallel
4. Budget Agent and Experience Agent generate competing itineraries shaped by the traveler's persona
5. Judge Agent evaluates both and synthesizes the best final itinerary
6. Critic Agent audits for hidden risks and flags issues with HIGH / MEDIUM / LOW ratings
7. Beautiful HTML email sent to user with full itinerary and risk assessment

## 🔑 Key Engineering Decisions

### Prepare Judge Body code node
The Judge Agent receives the full text of both agent proposals as input. These proposals contain newlines, quotes, and special characters that break JSON when interpolated directly into an HTTP Request body. The `Prepare Judge Body` code node uses `JSON.stringify()` to safely escape the entire payload before sending.

### Raw body mode for all Gemini nodes
n8n's HTTP Request node validates JSON bodies before sending. Since Gemini prompts contain `{{ }}` expressions with dynamic content, the body must be set to **Raw** mode with `Content-Type: application/json` — not the JSON fields mode.

### Persona steering via prompt injection
Rather than separate agent instances per persona, persona behavior is injected directly into Budget and Experience Agent prompts:
- Budget Backpacker → maximize savings, hostels, street food, free activities
- Family Traveler → kid-friendly, safe, convenient, slightly higher cost acceptable
- Digital Nomad → WiFi, co-working spaces, flexible scheduling
- Luxury Seeker → 5-star hotels, private tours, exclusive restaurants

### Critic Agent as a `<div>` not a full document
The Judge Agent produces a complete `<!DOCTYPE html>` document. The Critic Agent outputs only a `<div>` so it can be appended without creating two nested HTML documents.

## 🚀 Setup

### Prerequisites
- Docker Desktop
- Google Gemini API key (free at aistudio.google.com)
- SerpAPI key (free tier at serpapi.com)
- Gmail OAuth2 credentials

### Installation

1. Clone the repo:
```bash
git clone https://github.com/pkgandhi/ai-travel-agent.git
cd ai-travel-agent
```

2. Copy the environment file:
```bash
cp .env.example .env
```

3. Add your API keys to `.env`:
```
GEMINI_API_KEY=your_gemini_key_here
SERPAPI_KEY=your_serpapi_key_here
N8N_BLOCK_ENV_ACCESS_IN_NODE=false
```

4. Start Docker:
```bash
docker compose up
```

5. Open n8n at http://localhost:5678

6. Import the workflow:
   - Go to Workflows → Import
   - Select `workflow-main.json`

7. Update the Config node with your API keys

8. Set up Gmail OAuth2:
   - Create OAuth2 credentials in Google Cloud Console
   - Add `http://localhost:5678/rest/oauth2-credential/callback` as an authorized redirect URI
   - Connect in n8n → Credentials → Gmail OAuth2

9. Activate the workflow and open the form URL shown in the trigger node

### Known Issues and Fixes

| Issue | Solution |
|---|---|
| Gemini rate limit (20 req/min free tier) | Add Wait nodes (10s) between agents, or upgrade to pay-as-you-go |
| Gmail OAuth token expires every 7 days | Reconnect in n8n → Credentials → Gmail → Sign in with Google |
| Docker networking timeout on Mac | Fully quit and restart Docker Desktop, then `docker compose down && docker compose up` |
| `$env` access denied in n8n code nodes | Set `N8N_BLOCK_ENV_ACCESS_IN_NODE=false` in `.env` |
| Gemini returns markdown-wrapped JSON | Parse Gemini Response node strips backtick fences with regex before JSON.parse() |

## 🧪 Evaluation Suite

This project uses a two-layer eval strategy to validate agent output quality — the same pattern used in production ML systems for automated regression testing every time a prompt changes.

### Eval approach

| Type | What it checks | Tool |
|---|---|---|
| Deterministic | Verdict phrases, destination preservation, risk level presence | Python |
| LLM-graded | Persona steering, dietary preferences, risk flagging | Gemini as judge |

### Test cases (7/8 passing — 87%)

| Test | Type | Status |
|---|---|---|
| Budget Agent ends with BUDGET AGENT VERDICT | Deterministic | ✅ Pass |
| Experience Agent ends with EXPERIENCE AGENT VERDICT | Deterministic | ✅ Pass |
| Budget Backpacker → cheap options recommended | LLM-graded | ✅ Pass |
| Digital Nomad → WiFi/co-working mentioned | LLM-graded | ✅ Pass |
| Vegetarian preference → respected in dining | LLM-graded | ✅ Pass |
| Critic Agent → includes HIGH/MEDIUM/LOW risk levels | Deterministic | ✅ Pass |
| Critic Agent → flags 45-min layover as risky | LLM-graded | ❌ Network timeout (not logic failure — fix: increase timeout to 120s) |
| Refinement Agent → keeps original destination | Deterministic | ✅ Pass |

### Eval metrics tracked

| Metric | Description | Target |
|---|---|---|
| Persona Adherence Score (0-10) | How well output matches requested persona | > 8.0 |
| Preference Compliance Rate (%) | % of user preferences reflected in itinerary | > 85% |
| Judge Consistency Score (%) | Same winner picked across 3 runs of identical input | > 80% |
| Debate Delta | Judge score vs individual agents — proves debate adds value | Judge > both agents |
| End-to-End Success Rate (%) | % of form submissions that result in a delivered email | > 90% |

### Running the evals

```bash
# Create and activate a virtual environment
python3.12 -m venv ~/travel-agent-evals
source ~/travel-agent-evals/bin/activate
pip install requests

# Run the eval suite
cd evals
GEMINI_API_KEY=your_key_here python eval_agents.py
```

Expected output:
```
============================================================
  AI Travel Agent — Eval Suite
  Model: gemini-2.5-flash | Rate limit: 1 req/60s
============================================================
  Running: Budget Agent ends with BUDGET AGENT VERDICT... PASS
  Running: Experience Agent ends with EXPERIENCE AGENT VERDICT... PASS
  ...
  Score: 87%
  Most evals passing — review failures above.
============================================================
```

## 🔄 Alternative Architecture — With Feedback Loop

A second workflow (`workflow-with-feedback.json`) adds a feedback loop allowing travelers to refine their itinerary after receiving the initial email.

### How it works

After the itinerary email is sent, the traveler clicks a "Refine My Itinerary" button. A feedback form collects what they liked and what they want changed. A Gemini Refinement Agent generates a revised itinerary and sends a second email.

### Why it's not the primary workflow

The feedback form runs in a **completely separate n8n workflow execution context**, meaning it has no access to the original itinerary or any data from the main workflow. Without the full original itinerary content, the Refinement Agent hallucinates a completely different trip.

Approaches attempted and their limitations:

- **URL parameters** — limited in length, unreliable for passing full HTML itinerary content
- **Google Sheets as a database** — Google Sheets interprets `<!DOCTYPE html>` as a formula, corrupting stored itinerary HTML
- **n8n static data** — only persists within the same workflow, not across separate executions
- **File system (`fs` module)** — blocked by n8n for security

### How it would be handled in production

| Approach | Description | Complexity |
|---|---|---|
| **Redis** | Store itinerary keyed by email after Judge Agent with 24hr TTL. Feedback workflow reads from Redis via HTTP. Fast, purpose-built for session state. | Low |
| **Supabase (PostgreSQL)** | Full relational store. Enables trip history, user accounts, multiple refinement rounds. | Medium |
| **Single workflow + Wait node** | Keep everything in one n8n workflow. After sending email, a Wait node listens for the feedback form with a 24hr timeout. No cross-workflow state sharing needed. | Low |
| **FastAPI + SQLite sidecar** | Main workflow POSTs itinerary to a lightweight FastAPI service. Feedback workflow GETs it back by email key. | Medium |

The **single workflow + Wait node** approach is recommended — it eliminates the state-sharing problem entirely since all node data remains accessible within the same execution context.

## 🔑 Environment Variables

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | Google Gemini API key |
| `SERPAPI_KEY` | SerpAPI key for flights/hotels |
| `N8N_BLOCK_ENV_ACCESS_IN_NODE` | Set to `false` to allow env vars in n8n |

## 📁 Repository Structure

```
ai-travel-agent/
├── workflow-main.json              # Primary workflow — multi-agent debate
├── workflow-with-feedback.json     # Alternative — includes feedback refinement loop
├── architecture.svg                # Workflow architecture diagram
├── AI_Travel_Agent_OnePager.pdf    # Project one-pager
├── evals/
│   └── eval_agents.py             # Python eval suite (8 tests, 87% pass rate)
├── promptfooconfig.yaml            # PromptFoo eval configuration
├── .env.example                    # Environment variable template
└── README.md
```

## 🗺️ Roadmap

- [ ] **Production feedback loop** — implement with Redis session store or single workflow + Wait node pattern
- [ ] **Fintech Intelligence Layer** — currency volatility agent checks FX rates before recommending destinations
- [ ] **Multimodal Vision Agent** — users upload Instagram photos, Gemini Vision identifies the location and builds the itinerary around it
- [ ] **CLI tool** — Python script that triggers the n8n webhook from terminal
- [ ] **Loom demo video** — end-to-end walkthrough
