from typing import List, Dict, Any, Optional
from backend.tools.budget_tool import calculate_budget
from backend.tools.packing_tool import generate_packing_checklist
from backend.tools.schedule_tool import optimize_schedule
from backend.tools.base import load_json_dataset

async def budget_analysis_skill(budget: float, days: int) -> Dict[str, Any]:
    """Analyzes budget limits and flags warnings."""
    return await calculate_budget(budget, days)

def trip_summary_skill(destination: str, days: int, hotel: Dict[str, Any], budget: float, estimated_cost: float) -> Dict[str, Any]:
    """Compiles high-level summary of the planned travel adventure."""
    savings = budget - estimated_cost
    status = "under_budget" if savings >= 0 else "over_budget"
    
    return {
        "title": f"Ultimate {days}-Day Adventure in {destination.title()}",
        "subtitle": f"Experience local culture and sightseeing staying at {hotel['name']}",
        "savings_usd": round(savings, 2),
        "status": status,
        "efficiency_index": round((estimated_cost / budget) * 100, 1) if budget > 0 else 0
    }

async def hotel_recommendation_skill(hotels: List[Dict[str, Any]], preference: str, max_price: float) -> Dict[str, Any]:
    """Selects and recommends the best matching hotel from list."""
    if not hotels:
        # Fallback hotel
        return {
            "name": "Standard Guest House",
            "category": "Budget",
            "price_per_night": 60,
            "rating": 4.0,
            "amenities": ["Wi-Fi", "AC"],
            "description": "A reliable, basic local guest house."
        }
        
    # Find exact matching preference under price limit, or fallback to first
    for hotel in hotels:
        if hotel["category"].lower() == preference.lower() and hotel["price_per_night"] <= max_price:
            return hotel
            
    # Sub-optimal search: find any under price limit
    for hotel in hotels:
        if hotel["price_per_night"] <= max_price:
            return hotel
            
    # Default to cheapest hotel if all exceed limit
    hotels.sort(key=lambda x: x["price_per_night"])
    return hotels[0]

async def packing_checklist_skill(city: str, season: str, duration: int, interests: List[str]) -> Dict[str, Any]:
    """Compiles clothing and gear requirements."""
    return await generate_packing_checklist(city, season, duration, interests)

async def daily_planner_skill(city: str, attractions: List[Dict[str, Any]], days: int) -> List[Dict[str, Any]]:
    """Builds optimized linear daytime flow."""
    return await optimize_schedule(city, attractions, days)

def travel_safety_skill(city: str, nationality: str) -> Dict[str, Any]:
    """Collects emergency protocols and immigration requirements."""
    # Load travel tips
    tips_db = load_json_dataset("travel_tips.json")
    visa_db = load_json_dataset("visa.json")
    
    city_tips = tips_db.get(city, {
        "emergency_contacts": {"police": "112", "fire_ambulance": "112", "medical_helpline": "112"},
        "local_customs": ["Respect local laws and residents."],
        "useful_phrases": []
    })
    
    # Check visa
    visa_guidelines = "Check local entry requirements before traveling."
    # Find matching country
    for country, requirements in visa_db.items():
        # Match cities to countries
        # Tokyo -> Japan, Paris -> France, Rome -> Italy, London -> United Kingdom, New York -> United States, Bali -> Indonesia, Sydney -> Australia
        city_country_map = {
            "tokyo": "Japan",
            "paris": "France",
            "rome": "Italy",
            "london": "United Kingdom",
            "new_york": "United States",
            "bali": "Indonesia",
            "sydney": "Australia"
        }
        
        target_country = city_country_map.get(city, "")
        if country.lower() == target_country.lower():
            visa_guidelines = requirements.get(nationality, requirements.get("other", visa_guidelines))
            break
            
    return {
        "emergency_contacts": city_tips["emergency_contacts"],
        "local_customs": city_tips["local_customs"],
        "useful_phrases": city_tips["useful_phrases"],
        "visa_guidelines": f"Visa rules for {nationality} citizens traveling to {country}: {visa_guidelines}"
    }

def expense_breakdown_skill(budget_info: Dict[str, Any], hotel: Dict[str, Any], itinerary: List[Dict[str, Any]], days: int) -> Dict[str, Any]:
    """Aggregates all daily costs, hotel bookings, dining estimates to form final ledger."""
    hotel_cost = hotel["price_per_night"] * days
    
    # Calculate attractions and dining costs from itinerary
    attractions_cost = 0.0
    dining_cost = 0.0
    transport_cost = 0.0
    
    for day in itinerary:
        for slot in day["timeline"]:
            cost = slot.get("cost_usd", 0)
            if slot["type"] == "Attraction":
                attractions_cost += cost
            elif slot["type"] == "Meal":
                dining_cost += cost
            elif slot["type"] == "Transport":
                transport_cost += cost
                
    # If transport wasn't detailed, estimate from budget allocation
    if transport_cost == 0:
        transport_cost = budget_info["breakdown"]["transportation_usd"]
        
    actual_total = hotel_cost + attractions_cost + dining_cost + transport_cost
    
    return {
        "hotel_total_usd": round(hotel_cost, 2),
        "dining_total_usd": round(dining_cost, 2),
        "attractions_total_usd": round(attractions_cost, 2),
        "transportation_total_usd": round(transport_cost, 2),
        "total_estimated_usd": round(actual_total, 2),
        "budget_limit_usd": budget_info["daily_limit_usd"] * days,
        "contingency_usd": round(budget_info["breakdown"]["contingency_usd"], 2)
    }
