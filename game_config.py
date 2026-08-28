"""Canonical calibration for the Economics Option Value classroom game.

This module deliberately has no oTree imports so the mechanism can be checked
with ordinary Python via validate_mechanism.py.
"""

from itertools import product

FALLBACK_CODE = "general_employment"
FALLBACK_LABEL = "General Employment"
FALLBACK_VALUE = 50
BOOM_MULTIPLIER = 1.50
WEAK_MULTIPLIER = 0.50
OFFER_CAP = 0.95

MAJORS = {
    "computer_science": {
        "label": "Computer Science",
        "icon": "💻",
        "cost": 18,
        "access": {
            "tech_data": 0.95,
            "finance": 0.10,
            "business_consulting": 0.20,
            "government_policy": 0.08,
            "people_human_services": 0.04,
        },
    },
    "finance": {
        "label": "Finance",
        "icon": "💰",
        "cost": 13,
        "access": {
            "tech_data": 0.12,
            "finance": 0.95,
            "business_consulting": 0.55,
            "government_policy": 0.12,
            "people_human_services": 0.06,
        },
    },
    "economics": {
        "label": "Economics",
        "icon": "📈",
        "cost": 14,
        "access": {
            "tech_data": 0.44,
            "finance": 0.52,
            "business_consulting": 0.65,
            "government_policy": 0.85,
            "people_human_services": 0.18,
        },
    },
    "general_business": {
        "label": "General Business",
        "icon": "💼",
        "cost": 10,
        "access": {
            "tech_data": 0.22,
            "finance": 0.40,
            "business_consulting": 0.86,
            "government_policy": 0.42,
            "people_human_services": 0.30,
        },
    },
    "psychology": {
        "label": "Psychology",
        "icon": "🧠",
        "cost": 8,
        "access": {
            "tech_data": 0.08,
            "finance": 0.06,
            "business_consulting": 0.25,
            "government_policy": 0.45,
            "people_human_services": 0.95,
        },
    },
}

CAREERS = {
    "tech_data": {"label": "Tech & Data", "icon": "💻", "value": 105},
    "finance": {"label": "Finance", "icon": "💰", "value": 100},
    "business_consulting": {
        "label": "Business & Consulting",
        "icon": "💼",
        "value": 90,
    },
    "government_policy": {
        "label": "Government & Policy",
        "icon": "🏛️",
        "value": 85,
    },
    "people_human_services": {
        "label": "People & Human Services",
        "icon": "🧠",
        "value": 82,
    },
}

STATES = {
    "tech_boom": {
        "label": "Tech & Data Boom",
        "icon": "💻",
        "boom_career": "tech_data",
        "probability": 0.20,
    },
    "finance_boom": {
        "label": "Finance Boom",
        "icon": "💰",
        "boom_career": "finance",
        "probability": 0.20,
    },
    "business_boom": {
        "label": "Business & Consulting Boom",
        "icon": "💼",
        "boom_career": "business_consulting",
        "probability": 0.20,
    },
    "policy_boom": {
        "label": "Government & Policy Boom",
        "icon": "🏛️",
        "boom_career": "government_policy",
        "probability": 0.20,
    },
    "people_boom": {
        "label": "People & Human Services Boom",
        "icon": "🧠",
        "boom_career": "people_human_services",
        "probability": 0.20,
    },
}

EMPIRICAL_FACTS = [
    {
        "metric": "Early-career earnings",
        "value": "~89th percentile",
        "detail": "among eligible majors in the exploratory ACS analysis",
    },
    {
        "metric": "Strong, above-median-paying occupational matches",
        "value": "~98th percentile",
        "detail": "on the project's structured-pathway measure",
    },
    {
        "metric": "Average occupational-demand shock resilience",
        "value": "~88th percentile",
        "detail": "on the project's model-based random-shock measure",
    },
]


def offer_probability(major_code, career_code, state_code):
    """State-dependent probability that career j is available to major m."""
    q = MAJORS[major_code]["access"][career_code]
    boom_career = STATES[state_code]["boom_career"]
    multiplier = BOOM_MULTIPLIER if career_code == boom_career else WEAK_MULTIPLIER
    return min(OFFER_CAP, q * multiplier)


def access_label(probability):
    """Student-facing qualitative label for an access probability-like number."""
    if probability >= 0.80:
        return "Excellent"
    if probability >= 0.60:
        return "Very Good"
    if probability >= 0.40:
        return "Good"
    if probability >= 0.20:
        return "Moderate"
    return "Limited"


def access_segments(probability):
    """Convert an access number to 1-5 filled visual segments."""
    if probability >= 0.80:
        return 5
    if probability >= 0.60:
        return 4
    if probability >= 0.40:
        return 3
    if probability >= 0.20:
        return 2
    return 1


def realize_offers(major_code, state_code, draws):
    """Apply stored U(0,1) draws to a major/state; no new randomness occurs here."""
    offers = {}
    probabilities = {}
    for career_code in CAREERS:
        p = offer_probability(major_code, career_code, state_code)
        probabilities[career_code] = p
        offers[career_code] = draws[career_code] <= p
    return probabilities, offers


def best_available(major_code, state_code, draws):
    """Best realized career and net payoff for a major under fixed luck."""
    probabilities, offers = realize_offers(major_code, state_code, draws)
    available = [
        career_code for career_code, is_available in offers.items() if is_available
    ]
    if available:
        career_code = max(available, key=lambda c: CAREERS[c]["value"])
        gross = CAREERS[career_code]["value"]
    else:
        career_code = FALLBACK_CODE
        gross = FALLBACK_VALUE
    cost = MAJORS[major_code]["cost"]
    return {
        "major_code": major_code,
        "career_code": career_code,
        "gross_value": gross,
        "net_payoff": gross - cost,
        "probabilities": probabilities,
        "offers": offers,
    }


def exact_major_state(major_code, state_code):
    """Exact expected outcome by enumerating all 2^5 offer bundles."""
    career_codes = list(CAREERS)
    probs = {
        c: offer_probability(major_code, c, state_code) for c in career_codes
    }
    degree_cost = MAJORS[major_code]["cost"]

    expected_net = 0.0
    expected_gross = 0.0
    p_fallback = 0.0
    expected_offers = 0.0

    for pattern in product([False, True], repeat=len(career_codes)):
        pattern_probability = 1.0
        offered = []
        for career_code, flag in zip(career_codes, pattern):
            p = probs[career_code]
            pattern_probability *= p if flag else (1 - p)
            if flag:
                offered.append(career_code)

        if offered:
            best_career = max(offered, key=lambda c: CAREERS[c]["value"])
            gross = CAREERS[best_career]["value"]
        else:
            gross = FALLBACK_VALUE
            p_fallback += pattern_probability

        expected_gross += pattern_probability * gross
        expected_net += pattern_probability * (gross - degree_cost)
        expected_offers += pattern_probability * len(offered)

    return {
        "major_code": major_code,
        "state_code": state_code,
        "expected_net_payoff": expected_net,
        "expected_gross_value": expected_gross,
        "probability_fallback": p_fallback,
        "probability_any_specialized_offer": 1 - p_fallback,
        "expected_number_specialized_offers": expected_offers,
    }


def ex_ante_summary():
    """Exact expected results when all five states are equally possible ex ante."""
    rows = []
    for major_code in MAJORS:
        by_state = [exact_major_state(major_code, state) for state in STATES]
        expected_net = sum(
            STATES[row["state_code"]]["probability"] * row["expected_net_payoff"]
            for row in by_state
        )
        fallback = sum(
            STATES[row["state_code"]]["probability"] * row["probability_fallback"]
            for row in by_state
        )
        expected_offers = sum(
            STATES[row["state_code"]]["probability"]
            * row["expected_number_specialized_offers"]
            for row in by_state
        )
        rows.append(
            {
                "major_code": major_code,
                "major_label": MAJORS[major_code]["label"],
                "degree_cost": MAJORS[major_code]["cost"],
                "expected_net_payoff": expected_net,
                "probability_fallback": fallback,
                "probability_any_specialized_offer": 1 - fallback,
                "expected_number_specialized_offers": expected_offers,
            }
        )
    return sorted(rows, key=lambda r: r["expected_net_payoff"], reverse=True)


def known_state_winners():
    rows = []
    for state_code in STATES:
        state_rows = [exact_major_state(m, state_code) for m in MAJORS]
        winner = max(state_rows, key=lambda r: r["expected_net_payoff"])
        rows.append(
            {
                "state_code": state_code,
                "state_label": STATES[state_code]["label"],
                "major_code": winner["major_code"],
                "major_label": MAJORS[winner["major_code"]]["label"],
                "expected_net_payoff": winner["expected_net_payoff"],
            }
        )
    return rows
