# ✈️ AI Travel Agent

A multi-agent AI system that autonomously searches for flights and hotels, generates 3 personalized itinerary options, and delivers them via email — with a built-in feedback loop for refinements.

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

## ✨ Features

- **Multi-step Gemini calls** for intent parsing and itinerary generation
- **Live flight and hotel data** via SerpAPI
- **3 tiered itineraries** — Budget, Comfort, Luxury
- **Email feedback loop** — users refine itineraries by filling a form
- **100% free stack** — no paid subscriptions required

## 🚀 Setup

### Prerequisites
- Docker Desktop
- Google Gemini API key (free at aistudio.google.com)
- SerpAPI key (free tier at serpapi.com)
- Gmail OAuth2 credentials

### Installation

1. Clone the repo:
```bash
git clone https://github.com/YOUR_USERNAME/ai-travel-agent.git
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
   - Select `AI Travel Agent - With Feedback.json`

7. Update the Config node with your API keys

8. Activate the workflow and you're ready!

## 📧 How It Works

1. User fills out travel form (origin, destination, dates, budget)
2. Gemini parses intent and extracts airport codes
3. SerpAPI fetches live flights and hotels
4. Gemini generates 3 itinerary options
5. Beautiful HTML email sent to user
6. User clicks "Refine My Itinerary" button
7. Feedback form captures change requests
8. Gemini Refinement Agent generates revised itinerary
9. Revised email sent automatically

## 🔑 Environment Variables

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | Google Gemini API key |
| `SERPAPI_KEY` | SerpAPI key for flights/hotels |
| `N8N_BLOCK_ENV_ACCESS_IN_NODE` | Set to false to allow env vars in n8n |

