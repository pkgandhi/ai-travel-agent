"""
AI Travel Agent — Eval Suite
Tests Budget Agent, Experience Agent, Judge Agent, and Critic Agent
using direct Gemini API calls with controlled rate limiting.

Usage:
    export GEMINI_API_KEY=your_key_here
    python eval_agents.py
"""

import os
import time
import json
import requests

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_KEY_HERE")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
DELAY_BETWEEN_CALLS = 60  # seconds — stays under free tier 20 req/min

# ── Helpers ──────────────────────────────────────────────────────────────────

def call_gemini(prompt: str) -> str:
    """Call Gemini API and return the text response."""
    body = {"contents": [{"parts": [{"text": prompt}]}]}
    response = requests.post(GEMINI_URL, json=body, timeout=60)
    data = response.json()
    if "candidates" not in data:
        raise Exception(f"Gemini error: {json.dumps(data)}")
    return data["candidates"][0]["content"]["parts"][0]["text"]


def llm_grade(output: str, rubric: str) -> tuple[bool, str]:
    """Use Gemini to grade an output against a rubric. Returns (pass, reason)."""
    prompt = f"""You are an eval judge. Assess whether the following OUTPUT passes the RUBRIC.

RUBRIC: {rubric}

OUTPUT:
{output[:2000]}

Respond with ONLY a JSON object like this:
{{"pass": true, "reason": "brief explanation"}}"""
    
    result = call_gemini(prompt)
    # Strip markdown fences if present
    cleaned = result.replace("```json", "").replace("```", "").strip()
    try:
        parsed = json.loads(cleaned)
        return parsed.get("pass", False), parsed.get("reason", "")
    except Exception:
        return False, f"Could not parse grader response: {result[:100]}"


def run_test(name: str, fn) -> dict:
    """Run a single test and return result."""
    print(f"\n  Running: {name}...", end="", flush=True)
    try:
        result = fn()
        status = "PASS" if result["passed"] else "FAIL"
        print(f" {status}")
        return {"name": name, "passed": result["passed"], "reason": result.get("reason", "")}
    except Exception as e:
        print(f" ERROR")
        return {"name": name, "passed": False, "reason": str(e)}


# ── Test cases ────────────────────────────────────────────────────────────────

def test_budget_agent_verdict():
    """Budget Agent must end with BUDGET AGENT VERDICT."""
    prompt = """You are a Budget Travel Agent. Create the cheapest possible itinerary.

TRAVELER INFO:
- Name: John
- Destination: Miami
- Dates: 2026-04-10 to 2026-04-14
- Budget: $2000
- Preferences: beach, vegetarian restaurants
- Travel Persona: Family Traveler

Create a brief day-by-day itinerary prioritizing lowest cost. End your response with: BUDGET AGENT VERDICT"""

    output = call_gemini(prompt)
    passed = "BUDGET AGENT VERDICT" in output
    return {"passed": passed, "reason": "Verdict phrase found" if passed else "Missing BUDGET AGENT VERDICT"}


def test_experience_agent_verdict():
    """Experience Agent must end with EXPERIENCE AGENT VERDICT."""
    time.sleep(DELAY_BETWEEN_CALLS)
    prompt = """You are an Experience Travel Agent. Create the best possible travel experience.

TRAVELER INFO:
- Name: John
- Destination: Paris
- Dates: 2026-04-10 to 2026-04-14
- Budget: $5000
- Preferences: fine dining, art
- Travel Persona: Luxury Seeker

Create a brief day-by-day itinerary prioritizing best experiences. End your response with: EXPERIENCE AGENT VERDICT"""

    output = call_gemini(prompt)
    passed = "EXPERIENCE AGENT VERDICT" in output
    return {"passed": passed, "reason": "Verdict phrase found" if passed else "Missing EXPERIENCE AGENT VERDICT"}


def test_budget_backpacker_persona():
    """Budget Backpacker persona should produce cheap recommendations."""
    time.sleep(DELAY_BETWEEN_CALLS)
    prompt = """You are a Budget Travel Agent. Create the cheapest possible itinerary.

TRAVELER INFO:
- Name: Sam
- Destination: Bangkok
- Dates: 2026-05-01 to 2026-05-07
- Budget: $800
- Preferences: street food, culture
- Travel Persona: Budget Backpacker

Prioritize lowest cost options. End your response with: BUDGET AGENT VERDICT"""

    output = call_gemini(prompt)
    time.sleep(DELAY_BETWEEN_CALLS)
    passed, reason = llm_grade(
        output,
        "The itinerary prioritizes low-cost options such as hostels, street food, or budget guesthouses. "
        "It does NOT recommend 5-star hotels or fine dining restaurants."
    )
    return {"passed": passed, "reason": reason}


def test_digital_nomad_persona():
    """Digital Nomad persona should mention WiFi or co-working."""
    time.sleep(DELAY_BETWEEN_CALLS)
    prompt = """You are an Experience Travel Agent. Create the best possible travel experience.

TRAVELER INFO:
- Name: Sarah
- Destination: Lisbon
- Dates: 2026-04-10 to 2026-04-17
- Budget: $3000
- Preferences: remote work, coffee shops
- Travel Persona: Digital Nomad

Prioritize experiences suited for a remote worker. End your response with: EXPERIENCE AGENT VERDICT"""

    output = call_gemini(prompt)
    time.sleep(DELAY_BETWEEN_CALLS)
    passed, reason = llm_grade(
        output,
        "The itinerary mentions at least one of: co-working spaces, WiFi availability, "
        "remote-work friendly cafes, or digital nomad hubs."
    )
    return {"passed": passed, "reason": reason}


def test_vegetarian_preference():
    """Vegetarian preference must be reflected in dining recommendations."""
    time.sleep(DELAY_BETWEEN_CALLS)
    prompt = """You are a Budget Travel Agent. Create the cheapest possible itinerary.

TRAVELER INFO:
- Name: Pratik
- Destination: Tokyo
- Dates: 2026-04-10 to 2026-04-17
- Budget: $2500
- Preferences: vegetarian food only, no meat or fish
- Travel Persona: Family Traveler

Create a day-by-day itinerary. End your response with: BUDGET AGENT VERDICT"""

    output = call_gemini(prompt)
    time.sleep(DELAY_BETWEEN_CALLS)
    passed, reason = llm_grade(
        output,
        "The itinerary specifically mentions vegetarian-friendly restaurants, "
        "vegetarian options, or plant-based dining. It does not recommend meat or fish dishes."
    )
    return {"passed": passed, "reason": reason}


def test_critic_has_risk_levels():
    """Critic Agent must include HIGH/MEDIUM/LOW risk ratings."""
    time.sleep(DELAY_BETWEEN_CALLS)
    sample_itinerary = """Day 1: Fly JFK to MIA (45-min layover in CLT). Check into budget hotel near airport.
Day 2: South Beach, lunch at random beachside cafe, evening walk.
Day 3: Everglades day trip, return late evening.
Day 4: Fly home."""

    prompt = f"""You are a Devil's Advocate Travel Critic. Audit this itinerary for risks.

ITINERARY:
{sample_itinerary}

Identify risks and rate each as HIGH, MEDIUM, or LOW. Keep response under 300 words."""

    output = call_gemini(prompt)
    passed = any(level in output.upper() for level in ["HIGH", "MEDIUM", "LOW"])
    return {
        "passed": passed,
        "reason": "Risk levels found" if passed else "No HIGH/MEDIUM/LOW ratings in Critic output"
    }


def test_critic_flags_short_layover():
    """Critic Agent should flag a 45-minute layover as a risk."""
    time.sleep(DELAY_BETWEEN_CALLS)
    sample_itinerary = "Flight: JFK → CLT (45 min layover) → MIA. Hotel: downtown budget hotel."

    prompt = f"""You are a Devil's Advocate Travel Critic. Audit this itinerary for hidden risks.

ITINERARY:
{sample_itinerary}

Flag any logistical, budget, or experience risks. Rate each HIGH/MEDIUM/LOW."""

    output = call_gemini(prompt)
    time.sleep(DELAY_BETWEEN_CALLS)
    passed, reason = llm_grade(
        output,
        "The response identifies the 45-minute layover as a risk — flagging it as too short, "
        "risky for a connection, or likely to be missed."
    )
    return {"passed": passed, "reason": reason}


def test_refinement_keeps_destination():
    """Refinement Agent must keep the original destination."""
    time.sleep(DELAY_BETWEEN_CALLS)
    prompt = """You are an expert travel agent refining an existing itinerary based on user feedback.

ORIGINAL TRIP CONTEXT:
- Destination: Miami
- Traveler: John

USER FEEDBACK:
- What they want to change: More vegetarian restaurant options
- Additional preferences: Keep the beach activities

IMPORTANT: The destination is Miami. Do NOT change the destination.

Generate a REVISED itinerary for Miami only. Format as plain text."""

    output = call_gemini(prompt)
    passed = "miami" in output.lower()
    return {
        "passed": passed,
        "reason": "Miami preserved in refined itinerary" if passed else "Destination changed — Miami not found in output"
    }


# ── Main runner ───────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  AI Travel Agent — Eval Suite")
    print("  Model: gemini-2.5-flash | Rate limit: 1 req/10s")
    print("=" * 60)

    tests = [
        ("Budget Agent ends with BUDGET AGENT VERDICT",   test_budget_agent_verdict),
        ("Experience Agent ends with EXPERIENCE AGENT VERDICT", test_experience_agent_verdict),
        ("Budget Backpacker → cheap options (LLM graded)", test_budget_backpacker_persona),
        ("Digital Nomad → WiFi/co-working mentioned (LLM graded)", test_digital_nomad_persona),
        ("Vegetarian preference → dining respected (LLM graded)", test_vegetarian_preference),
        ("Critic Agent → includes risk levels",            test_critic_has_risk_levels),
        ("Critic Agent → flags 45min layover (LLM graded)", test_critic_flags_short_layover),
        ("Refinement Agent → keeps destination",           test_refinement_keeps_destination),
    ]

    results = []
    for name, fn in tests:
        result = run_test(name, fn)
        results.append(result)

    # Summary
    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    print("\n" + "=" * 60)
    print(f"  Results: {passed}/{total} passed")
    print("=" * 60)

    for r in results:
        icon = "✅" if r["passed"] else "❌"
        print(f"  {icon}  {r['name']}")
        if not r["passed"]:
            print(f"       → {r['reason']}")

    print("\n" + "=" * 60)
    score = int((passed / total) * 100)
    print(f"  Score: {score}%")
    if score == 100:
        print("  All evals passed!")
    elif score >= 75:
        print("  Most evals passing — review failures above.")
    else:
        print("  Several evals failing — review agent prompts.")
    print("=" * 60)


if __name__ == "__main__":
    main()