"""
Find a Card — Agentic Card Discovery Web App
A beautiful demo illustrating how AI agents find the perfect payment card.
"""

from flask import Flask, render_template, jsonify, request
import json
import random
import time
from datetime import datetime

app = Flask(__name__)

# ─── Simulated Data ───────────────────────────────────────────────────────────

COUNTRIES = {
    "UK": {
        "name": "United Kingdom",
        "flag": "🇬🇧",
        "currency": "GBP",
        "banks": [
            {"id": "barclays", "name": "Barclays", "logo": "B"},
            {"id": "hsbc", "name": "HSBC", "logo": "H"},
            {"id": "lloyds", "name": "Lloyds Banking Group", "logo": "L"},
            {"id": "natwest", "name": "NatWest", "logo": "N"},
            {"id": "monzo", "name": "Monzo", "logo": "M"},
            {"id": "revolut", "name": "Revolut", "logo": "R"},
        ]
    },
    "US": {
        "name": "United States",
        "flag": "🇺🇸",
        "currency": "USD",
        "banks": [
            {"id": "chase", "name": "JPMorgan Chase", "logo": "J"},
            {"id": "citi", "name": "Citibank", "logo": "C"},
            {"id": "bofa", "name": "Bank of America", "logo": "B"},
            {"id": "wells", "name": "Wells Fargo", "logo": "W"},
            {"id": "capital_one", "name": "Capital One", "logo": "C"},
            {"id": "amex_bank", "name": "Goldman Sachs", "logo": "G"},
        ]
    },
    "IE": {
        "name": "Ireland",
        "flag": "🇮🇪",
        "currency": "EUR",
        "banks": [
            {"id": "aib", "name": "AIB", "logo": "A"},
            {"id": "boi", "name": "Bank of Ireland", "logo": "B"},
            {"id": "ptsb", "name": "Permanent TSB", "logo": "P"},
            {"id": "revolut_ie", "name": "Revolut", "logo": "R"},
            {"id": "n26_ie", "name": "N26", "logo": "N"},
        ]
    },
    "DE": {
        "name": "Germany",
        "flag": "🇩🇪",
        "currency": "EUR",
        "banks": [
            {"id": "deutsche", "name": "Deutsche Bank", "logo": "D"},
            {"id": "commerzbank", "name": "Commerzbank", "logo": "C"},
            {"id": "ing_de", "name": "ING", "logo": "I"},
            {"id": "n26", "name": "N26", "logo": "N"},
            {"id": "dkb", "name": "DKB", "logo": "D"},
        ]
    },
    "SG": {
        "name": "Singapore",
        "flag": "🇸🇬",
        "currency": "SGD",
        "banks": [
            {"id": "dbs", "name": "DBS", "logo": "D"},
            {"id": "ocbc", "name": "OCBC", "logo": "O"},
            {"id": "uob", "name": "UOB", "logo": "U"},
            {"id": "sc_sg", "name": "Standard Chartered", "logo": "S"},
            {"id": "citi_sg", "name": "Citibank", "logo": "C"},
        ]
    },
    "AU": {
        "name": "Australia",
        "flag": "🇦🇺",
        "currency": "AUD",
        "banks": [
            {"id": "cba", "name": "Commonwealth Bank", "logo": "C"},
            {"id": "anz", "name": "ANZ", "logo": "A"},
            {"id": "westpac", "name": "Westpac", "logo": "W"},
            {"id": "nab", "name": "NAB", "logo": "N"},
            {"id": "macquarie", "name": "Macquarie", "logo": "M"},
        ]
    }
}

SPENDING_CATEGORIES = [
    {"name": "Groceries", "icon": "🛒", "monthly_avg": 0},
    {"name": "Dining", "icon": "🍽️", "monthly_avg": 0},
    {"name": "Travel", "icon": "✈️", "monthly_avg": 0},
    {"name": "Shopping", "icon": "🛍️", "monthly_avg": 0},
    {"name": "Entertainment", "icon": "🎬", "monthly_avg": 0},
    {"name": "Transport", "icon": "🚗", "monthly_avg": 0},
    {"name": "Subscriptions", "icon": "📱", "monthly_avg": 0},
    {"name": "Utilities", "icon": "💡", "monthly_avg": 0},
]

SOCIAL_INTERESTS = [
    "Travel", "Food & Wine", "Fitness", "Technology", "Fashion",
    "Sustainability", "Sports", "Music", "Photography", "Art",
    "Gaming", "Outdoor Adventures", "Luxury", "Family", "Pets"
]

MASTERCARD_BENEFITS = {
    "standard": [
        {"name": "Zero Liability Protection", "icon": "🛡️", "desc": "You won't be held responsible for unauthorized transactions"},
        {"name": "ID Theft Protection", "icon": "🔐", "desc": "Free identity theft resolution services"},
        {"name": "Mastercard Global Service", "icon": "🌍", "desc": "24/7 emergency assistance worldwide"},
    ],
    "world": [
        {"name": "Travel Rewards", "icon": "✈️", "desc": "Earn points on every purchase, bonus on travel"},
        {"name": "Price Protection", "icon": "💰", "desc": "Get refunded the difference if price drops"},
        {"name": "Extended Warranty", "icon": "🔧", "desc": "Double manufacturer's warranty up to 1 year"},
        {"name": "Purchase Assurance", "icon": "📦", "desc": "Covers new purchases against damage or theft for 120 days"},
        {"name": "Airport Lounge Access", "icon": "🛋️", "desc": "Complimentary access to 1,000+ airport lounges"},
    ],
    "world_elite": [
        {"name": "Luxury Hotel Collection", "icon": "🏨", "desc": "Complimentary nights, upgrades & VIP perks at 3,000+ hotels"},
        {"name": "Priceless Experiences", "icon": "⭐", "desc": "Exclusive access to culinary, sports, entertainment events"},
        {"name": "Concierge Service", "icon": "🎩", "desc": "24/7 dedicated concierge for travel, dining & more"},
        {"name": "Travel Insurance Suite", "icon": "🧳", "desc": "Comprehensive travel, medical & baggage insurance"},
        {"name": "Cell Phone Protection", "icon": "📱", "desc": "Coverage for damage/theft of your cell phone"},
        {"name": "Mastercard Travel Pass", "icon": "🎫", "desc": "Discounted airport experiences worldwide"},
        {"name": "Sustainability Badge", "icon": "🌱", "desc": "Carbon footprint tracker on every transaction"},
    ]
}

CARD_TEMPLATES = [
    {
        "name": "World Elite Travel Rewards",
        "tier": "world_elite",
        "annual_fee": 195,
        "apr_range": "15.9% - 22.9%",
        "cashback": "3% travel, 2% dining, 1% all else",
        "welcome_bonus": "60,000 points",
        "fx_fee": "0%",
        "colors": ["#1a1a2e", "#e94560"],
        "accent": "#e94560",
        "tags": ["travel", "premium", "rewards"],
        "approval_base": 75,
    },
    {
        "name": "World Cashback Plus",
        "tier": "world",
        "annual_fee": 95,
        "apr_range": "17.9% - 24.9%",
        "cashback": "2% on everything, 5% rotating categories",
        "welcome_bonus": "£200 cashback",
        "fx_fee": "0%",
        "colors": ["#0f3460", "#e94560"],
        "accent": "#16213e",
        "tags": ["cashback", "everyday", "rewards"],
        "approval_base": 70,
    },
    {
        "name": "World Elite Black",
        "tier": "world_elite",
        "annual_fee": 495,
        "apr_range": "14.9% - 19.9%",
        "cashback": "5% travel & dining, 2% all else",
        "welcome_bonus": "100,000 points + companion flight",
        "fx_fee": "0%",
        "colors": ["#0d0d0d", "#c9a84c"],
        "accent": "#c9a84c",
        "tags": ["luxury", "travel", "premium"],
        "approval_base": 60,
    },
    {
        "name": "Standard Everyday",
        "tier": "standard",
        "annual_fee": 0,
        "apr_range": "19.9% - 29.9%",
        "cashback": "0.5% on all purchases",
        "welcome_bonus": "0% APR for 15 months",
        "fx_fee": "2.99%",
        "colors": ["#2d3436", "#636e72"],
        "accent": "#636e72",
        "tags": ["no-fee", "basic", "starter"],
        "approval_base": 90,
    },
    {
        "name": "World Sustainability",
        "tier": "world",
        "annual_fee": 0,
        "apr_range": "18.9% - 25.9%",
        "cashback": "2% on sustainable brands, 1% all else",
        "welcome_bonus": "Plant 100 trees on approval",
        "fx_fee": "0%",
        "colors": ["#1b4332", "#52b788"],
        "accent": "#52b788",
        "tags": ["sustainability", "eco", "rewards"],
        "approval_base": 80,
    },
    {
        "name": "World Elite Platinum Rewards",
        "tier": "world_elite",
        "annual_fee": 295,
        "apr_range": "16.9% - 21.9%",
        "cashback": "4x points on travel, 3x dining, 1x all",
        "welcome_bonus": "80,000 points after £3,000 spend",
        "fx_fee": "0%",
        "colors": ["#283048", "#859398"],
        "accent": "#859398",
        "tags": ["travel", "points", "premium"],
        "approval_base": 65,
    },
    {
        "name": "World Digital First",
        "tier": "world",
        "annual_fee": 0,
        "apr_range": "18.9% - 26.9%",
        "cashback": "3% online shopping, 1% all else",
        "welcome_bonus": "£100 statement credit",
        "fx_fee": "1%",
        "colors": ["#4a00e0", "#8e2de2"],
        "accent": "#8e2de2",
        "tags": ["digital", "online", "tech"],
        "approval_base": 85,
    },
    {
        "name": "World Elite Dining & Lifestyle",
        "tier": "world_elite",
        "annual_fee": 250,
        "apr_range": "16.9% - 23.9%",
        "cashback": "5% dining, 3% entertainment, 1% all",
        "welcome_bonus": "£300 dining credit + 50,000 pts",
        "fx_fee": "0%",
        "colors": ["#3d0c11", "#d4455a"],
        "accent": "#d4455a",
        "tags": ["dining", "lifestyle", "premium"],
        "approval_base": 68,
    },
]


def generate_spending_profile():
    """Generate realistic spending data as if from Open Banking."""
    categories = []
    total = 0
    for cat in SPENDING_CATEGORIES:
        ranges = {
            "Groceries": (200, 600),
            "Dining": (50, 400),
            "Travel": (0, 800),
            "Shopping": (100, 500),
            "Entertainment": (30, 200),
            "Transport": (50, 300),
            "Subscriptions": (20, 100),
            "Utilities": (80, 250),
        }
        lo, hi = ranges.get(cat["name"], (50, 300))
        avg = random.randint(lo, hi)
        total += avg
        categories.append({**cat, "monthly_avg": avg})
    return categories, total


def generate_social_profile():
    """Generate interests as if from social media analysis."""
    num_interests = random.randint(4, 8)
    chosen = random.sample(SOCIAL_INTERESTS, num_interests)
    return chosen


def score_card(card, profile_data):
    """Score a card based on the user's profile."""
    score = random.randint(55, 98)
    annual_value = random.randint(80, 900)
    approval_prob = min(98, card["approval_base"] + random.randint(-10, 15))
    breakeven_months = 0 if card["annual_fee"] == 0 else random.randint(2, 10)

    fit_reasons = []
    if "travel" in card["tags"] and profile_data.get("travel_frequency", 0) > 3:
        score = min(99, score + 8)
        fit_reasons.append("High travel frequency matches travel rewards")
    if "cashback" in card["tags"]:
        fit_reasons.append("Cashback on everyday spending categories")
    if "sustainability" in card["tags"] and "Sustainability" in profile_data.get("interests", []):
        score = min(99, score + 10)
        fit_reasons.append("Aligns with your sustainability values")
    if "dining" in card["tags"] and profile_data.get("dining_spend", 0) > 200:
        score = min(99, score + 7)
        fit_reasons.append("High dining spend maximizes dining rewards")
    if card["annual_fee"] == 0:
        fit_reasons.append("No annual fee — pure value from day one")
    if card["fx_fee"] == "0%":
        fit_reasons.append("Zero FX fees for international purchases")
    if "premium" in card["tags"]:
        fit_reasons.append("Premium tier unlocks exclusive Mastercard benefits")

    if not fit_reasons:
        fit_reasons = ["Solid all-round card for your profile", "Good rewards structure"]

    return {
        "score": score,
        "annual_value": annual_value,
        "approval_probability": approval_prob,
        "breakeven_months": breakeven_months,
        "fit_reasons": fit_reasons[:4],
    }


AGENT_LOG_TEMPLATES = [
    {"phase": "init", "messages": [
        "🤖 Agent initialized — Find a Card v3.2 (Agentic Mode)",
        "📡 Establishing secure connection to Mastercard Decision API...",
        "✅ Connection established. Session encrypted with TLS 1.3",
    ]},
    {"phase": "profile", "messages": [
        "👤 Loading consumer profile from identity provider...",
        "🔑 OAuth 2.0 token exchange with Open Banking gateway",
        "📊 Retrieving 12-month transaction history...",
        "💳 Found {num_transactions} transactions across {num_accounts} accounts",
        "📈 Analyzing spending patterns with ML categorization engine...",
        "🏷️ Top categories: {top_categories}",
        "💰 Monthly average spend: {currency}{monthly_spend}",
    ]},
    {"phase": "social", "messages": [
        "🌐 Connecting to social profile aggregator...",
        "🔍 Analyzing interests and lifestyle signals...",
        "❤️ Identified passions: {interests}",
        "🧠 Building psychographic profile vector...",
        "✅ Consumer profile complete — 47 feature dimensions extracted",
    ]},
    {"phase": "search", "messages": [
        "🔎 Querying Mastercard Card Catalog API...",
        "📋 GET /v3/cards?country={country}&profile_vector=encoded&tier=all",
        "📦 Received {num_cards} eligible card products from {num_issuers} issuers",
        "⚡ Running optimization engine on card portfolio...",
        "📊 Computing expected annual value for each card...",
        "🏦 Requesting pre-qualification from issuer agents...",
        "🤝 Agent-to-agent negotiation: requesting personalized offers...",
        "💎 {num_premium} premium offers received with enhanced welcome bonuses",
    ]},
    {"phase": "rank", "messages": [
        "🏆 Ranking cards by composite fit score...",
        "📐 Factoring: rewards value, approval probability, fee efficiency",
        "🎯 Applying preference weights from consumer profile",
        "✨ Top match: {top_card} — Score: {top_score}/100",
        "📊 Expected annual value: +{currency}{annual_value}",
        "✅ Results ready. {num_results} personalized recommendations generated.",
    ]},
]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/countries")
def get_countries():
    result = []
    for code, data in COUNTRIES.items():
        result.append({
            "code": code,
            "name": data["name"],
            "flag": data["flag"],
            "currency": data["currency"],
        })
    return jsonify(result)


@app.route("/api/banks/<country_code>")
def get_banks(country_code):
    country = COUNTRIES.get(country_code.upper())
    if not country:
        return jsonify({"error": "Country not found"}), 404
    return jsonify(country["banks"])


@app.route("/api/connect-bank", methods=["POST"])
def connect_bank():
    """Simulate Open Banking connection and spending analysis."""
    data = request.json or {}
    bank_id = data.get("bank_id", "unknown")
    categories, total = generate_spending_profile()
    travel_spend = next((c["monthly_avg"] for c in categories if c["name"] == "Travel"), 0)
    dining_spend = next((c["monthly_avg"] for c in categories if c["name"] == "Dining"), 0)

    interests = generate_social_profile()
    lifestyle_tags = random.sample(
        ["Urban Professional", "Frequent Traveler", "Foodie", "Eco-Conscious",
         "Tech Enthusiast", "Luxury Seeker", "Family Focused", "Adventure Lover"],
        k=random.randint(2, 4)
    )

    return jsonify({
        "bank_id": bank_id,
        "connected": True,
        "accounts": random.randint(1, 3),
        "transactions_analyzed": random.randint(180, 420),
        "spending_categories": categories,
        "monthly_total": total,
        "credit_score_band": random.choice(["Good", "Very Good", "Excellent"]),
        "travel_frequency": random.randint(1, 12),
        "cross_border_percentage": random.randint(5, 45),
        "travel_spend": travel_spend,
        "dining_spend": dining_spend,
        "existing_cards": random.randint(1, 4),
        "interests": interests,
        "lifestyle_tags": lifestyle_tags,
    })


@app.route("/api/connect-social", methods=["POST"])
def connect_social():
    """Simulate social media connection for interest analysis."""
    interests = generate_social_profile()
    return jsonify({
        "connected": True,
        "interests": interests,
        "lifestyle_tags": random.sample(
            ["Urban Professional", "Frequent Traveler", "Foodie", "Eco-Conscious",
             "Tech Enthusiast", "Luxury Seeker", "Family Focused", "Adventure Lover"],
            k=random.randint(2, 4)
        ),
    })


@app.route("/api/search-cards", methods=["POST"])
def search_cards():
    """Run the agentic card search and return scored results."""
    data = request.json or {}
    country_code = data.get("country", "UK")
    currency_symbol = {"GBP": "£", "USD": "$", "EUR": "€", "SGD": "S$", "AUD": "A$"}.get(
        COUNTRIES.get(country_code, {}).get("currency", "GBP"), "£"
    )

    profile_data = {
        "travel_frequency": data.get("travel_frequency", 3),
        "dining_spend": data.get("dining_spend", 150),
        "interests": data.get("interests", []),
        "credit_score": data.get("credit_score_band", "Good"),
        "monthly_spend": data.get("monthly_total", 2000),
    }

    results = []
    for card in CARD_TEMPLATES:
        scoring = score_card(card, profile_data)
        results.append({
            **card,
            **scoring,
            "currency": currency_symbol,
            "annual_value_display": f"+{currency_symbol}{scoring['annual_value']}",
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return jsonify(results)


@app.route("/api/agent-log", methods=["POST"])
def agent_log():
    """Return phased agent log messages for the workflow feed."""
    data = request.json or {}
    phase = data.get("phase", "init")
    country = data.get("country", "UK")
    currency_symbol = {"GBP": "£", "USD": "$", "EUR": "€", "SGD": "S$", "AUD": "A$"}.get(
        COUNTRIES.get(country, {}).get("currency", "GBP"), "£"
    )

    template = next((t for t in AGENT_LOG_TEMPLATES if t["phase"] == phase), None)
    if not template:
        return jsonify([])

    messages = []
    for msg in template["messages"]:
        formatted = msg.format(
            num_transactions=random.randint(180, 420),
            num_accounts=random.randint(1, 3),
            top_categories="Travel, Dining, Shopping",
            monthly_spend=random.randint(1500, 4500),
            currency=currency_symbol,
            interests="Travel, Food & Wine, Technology",
            country=country,
            num_cards=len(CARD_TEMPLATES),
            num_issuers=random.randint(4, 8),
            num_premium=random.randint(2, 4),
            top_card="World Elite Travel Rewards",
            top_score=random.randint(90, 98),
            annual_value=random.randint(300, 700),
            num_results=len(CARD_TEMPLATES),
        )
        messages.append(formatted)
    return jsonify(messages)


if __name__ == "__main__":
    app.run(debug=True, port=5432)
