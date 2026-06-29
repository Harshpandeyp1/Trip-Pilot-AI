import asyncio
import logging
from typing import Dict, Any, List
from backend.tools.base import load_json_dataset
from backend.tools.hotel_tool import search_hotels
from backend.tools.restaurant_tool import search_restaurants
from backend.tools.attraction_tool import search_attractions
from backend.tools.budget_tool import calculate_budget

from backend.skills.skills import (
    budget_analysis_skill,
    trip_summary_skill,
    hotel_recommendation_skill,
    packing_checklist_skill,
    daily_planner_skill,
    travel_safety_skill,
    expense_breakdown_skill
)

logger = logging.getLogger("TripPilot-PlannerService")

def get_season_by_destination(city_id: str) -> str:
    """Helper to determine the current season for a destination in June (current local time month)."""
    # Northern Hemisphere cities: Tokyo, Paris, Rome, London, New York -> Summer in June
    # Southern Hemisphere: Sydney -> Winter in June
    # Tropical: Bali -> Summer / Dry Season in June
    if city_id == "sydney":
        return "winter"
    elif city_id == "bali":
        return "summer" # Dry season
    else:
        return "summer"

def generate_offline_trip_plan(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Synchronous planner execution that orchestrates the offline skills.
    Runs completely offline using local databases.
    """
    destination = params.get("destination", "tokyo").strip().lower()
    days = int(params.get("days", 3))
    budget = float(params.get("budget", 1000))
    interests = params.get("interests", ["Culture", "Food"])
    hotel_pref = params.get("hotel_pref", "Boutique")
    food_pref = params.get("food_pref", "Local")
    transport_pref = params.get("transport_pref", "Public")
    nationality = params.get("nationality", "US")

    logger.info(f"Generating travel plan for {destination} - Budget: {budget}, Days: {days}")
    
    # 1. Load city details
    cities = load_json_dataset("cities.json")
    city_obj = next((c for c in cities if c["id"] == destination), None)
    if not city_obj:
        raise ValueError(f"Destination '{destination}' is not supported in the offline database.")

    # Determine season
    season = get_season_by_destination(destination)
    
    # 2. Run budget allocation skill
    # We run the async functions synchronously here or wrap them in asyncio
    loop = asyncio.new_event_loop()
    try:
        budget_info = loop.run_until_complete(budget_analysis_skill(budget, days))
    except Exception as e:
        logger.error(f"Error in budget skill: {str(e)}")
        budget_info = {
            "daily_limit_usd": budget / days,
            "status": "healthy",
            "warning": "",
            "breakdown": {"accommodation_usd": budget * 0.4, "food_usd": budget * 0.25, "attractions_usd": budget * 0.15, "transportation_usd": budget * 0.1, "contingency_usd": budget * 0.1}
        }
    
    # 3. Find and rank hotels matching budget limit
    accommodation_cap = budget_info["breakdown"]["accommodation_usd"]
    max_night_cost = accommodation_cap / days
    
    try:
        candidate_hotels = loop.run_until_complete(search_hotels(destination, max_price=max_night_cost, style=hotel_pref))
        if not candidate_hotels:
            # Try searching without style filter if none found
            candidate_hotels = loop.run_until_complete(search_hotels(destination, max_price=max_night_cost))
        selected_hotel = loop.run_until_complete(hotel_recommendation_skill(candidate_hotels, hotel_pref, max_night_cost))
    except Exception as e:
        logger.error(f"Error in hotel selection: {str(e)}")
        selected_hotel = {
            "name": "Local Cozy Guesthouse",
            "category": "Budget",
            "price_per_night": round(max_night_cost * 0.8, 2),
            "rating": 4.2,
            "amenities": ["Wi-Fi", "AC"],
            "description": "A comfortable fallback accommodation near the center."
        }

    # 4. Search attractions matching interests
    selected_attractions = []
    seen_attractions = set()
    
    try:
        for interest in interests:
            found_attrs = loop.run_until_complete(search_attractions(destination, category=interest))
            for attr in found_attrs:
                if attr["id"] not in seen_attractions:
                    selected_attractions.append(attr)
                    seen_attractions.add(attr["id"])
                    
        # If no attractions match interests, load all attractions for the city
        if not selected_attractions:
            found_attrs = loop.run_until_complete(search_attractions(destination))
            selected_attractions = found_attrs[:5]
    except Exception as e:
        logger.error(f"Error loading attractions: {str(e)}")
        selected_attractions = []

    # 5. Search restaurants
    try:
        # Match restaurant price level to overall budget status
        price_lvl_map = {"critical": "Budget", "budget": "Budget", "healthy": "Mid-Range", "luxury": "Luxury"}
        pref_price_lvl = price_lvl_map.get(budget_info["status"], "Mid-Range")
        
        selected_restaurants = loop.run_until_complete(search_restaurants(destination, cuisine=food_pref, price_level=pref_price_lvl))
        if not selected_restaurants:
            selected_restaurants = loop.run_until_complete(search_restaurants(destination))
    except Exception as e:
        logger.error(f"Error loading restaurants: {str(e)}")
        selected_restaurants = []

    # 6. Optimize Daily Schedule
    try:
        itinerary = loop.run_until_complete(daily_planner_skill(destination, selected_attractions, days))
    except Exception as e:
        logger.error(f"Error in schedule optimizer: {str(e)}")
        itinerary = [{"day": d, "cost_usd": 40, "timeline": []} for d in range(1, days + 1)]

    # 7. Generate packing checklist
    try:
        packing_list = loop.run_until_complete(packing_checklist_skill(destination, season, days, interests))
    except Exception as e:
        logger.error(f"Error in packing skill: {str(e)}")
        packing_list = {"essentials": ["Passport", "Tickets"], "clothing": ["Jeans", "T-shirts"], "activity_gear": []}

    # 8. Generate safety advice
    try:
        safety_advice = travel_safety_skill(destination, nationality)
    except Exception as e:
        logger.error(f"Error in safety skill: {str(e)}")
        safety_advice = {
            "emergency_contacts": {"police": "112", "fire_ambulance": "112", "medical_helpline": "112"},
            "local_customs": [],
            "useful_phrases": [],
            "visa_guidelines": "Verify entry rules before departure."
        }

    # 9. Expense breakdown calculation
    try:
        expenses = expense_breakdown_skill(budget_info, selected_hotel, itinerary, days)
    except Exception as e:
        logger.error(f"Error in expense skill: {str(e)}")
        expenses = {
            "hotel_total_usd": selected_hotel["price_per_night"] * days,
            "dining_total_usd": 30.0 * days,
            "attractions_total_usd": 15.0 * days,
            "transportation_total_usd": 10.0 * days,
            "total_estimated_usd": (selected_hotel["price_per_night"] + 55) * days,
            "budget_limit_usd": budget,
            "contingency_usd": budget * 0.1
        }

    # 10. Generate summary
    summary = trip_summary_skill(destination, days, selected_hotel, budget, expenses["total_estimated_usd"])

    # Close loop
    loop.close()

    # Build final result JSON
    return {
        "destination": destination.title(),
        "country": city_obj["country"],
        "currency": city_obj["currency"],
        "timezone": city_obj["timezone"],
        "description": city_obj["description"],
        "days": days,
        "budget": budget,
        "season": season.title(),
        "summary": summary,
        "hotel": selected_hotel,
        "itinerary": itinerary,
        "packing_list": packing_list,
        "safety_advice": safety_advice,
        "expenses": expenses
    }
