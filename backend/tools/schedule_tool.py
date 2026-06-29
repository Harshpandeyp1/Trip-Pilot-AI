import logging
from typing import List, Dict, Any
from backend.tools.security import simulate_rate_limit

logger = logging.getLogger("ScheduleOptimizer")

async def optimize_schedule(city: str, activities: List[Dict[str, Any]], days: int) -> List[Dict[str, Any]]:
    """
    ScheduleOptimizer: Groups attractions into logical day schedules with time slots.
    
    Args:
        city: Target destination
        activities: Selected attraction dicts to distribute
        days: Trip duration in days
    """
    await simulate_rate_limit()
    
    logger.info(f"Executing ScheduleOptimizer tool for city={city}, activities count={len(activities)}, days={days}")
    
    # Simple algorithm to distribute activities across days
    itinerary_days = []
    
    # Initialize empty days
    for day_num in range(1, days + 1):
        itinerary_days.append({
            "day": day_num,
            "activities": []
        })
        
    if not activities:
        return itinerary_days
        
    # Group activities onto days
    for idx, act in enumerate(activities):
        day_idx = idx % days
        itinerary_days[day_idx]["activities"].append(act)
        
    # Standard day template times:
    # 09:30 - Morning Attraction
    # 12:30 - Lunch
    # 14:00 - Afternoon Attraction
    # 17:00 - Free time / Relax
    # 19:30 - Dinner
    
    formatted_days = []
    for day in itinerary_days:
        day_num = day["day"]
        day_acts = day["activities"]
        
        timeline = []
        
        # 1. Morning activity
        if len(day_acts) > 0:
            timeline.append({
                "time": "09:30 AM - 11:30 AM",
                "type": "Attraction",
                "name": day_acts[0]["name"],
                "description": day_acts[0].get("description", ""),
                "cost_usd": day_acts[0].get("ticket_cost", 0)
            })
        else:
            timeline.append({
                "time": "10:00 AM - 12:00 PM",
                "type": "Attraction",
                "name": "Local Neighborhood Exploration",
                "description": "Explore the local cafes and streets near your accommodation.",
                "cost_usd": 0
            })
            
        # 2. Lunch
        timeline.append({
            "time": "12:30 PM - 01:30 PM",
            "type": "Meal",
            "name": "Local Lunch",
            "description": "Stop by a nearby cafe or market to try regional specialties.",
            "cost_usd": 15
        })
        
        # 3. Afternoon activity
        if len(day_acts) > 1:
            timeline.append({
                "time": "02:00 PM - 04:30 PM",
                "type": "Attraction",
                "name": day_acts[1]["name"],
                "description": day_acts[1].get("description", ""),
                "cost_usd": day_acts[1].get("ticket_cost", 0)
            })
        elif len(day_acts) > 0:
            # If only 1 activity, put a scenic park or walk in the afternoon
            timeline.append({
                "time": "02:30 PM - 04:30 PM",
                "type": "Attraction",
                "name": "Scenic City Walk",
                "description": "Take a leisurely walk through local historic streets or gardens.",
                "cost_usd": 0
            })
            
        # 4. Free time
        timeline.append({
            "time": "05:00 PM - 07:00 PM",
            "type": "Relaxation",
            "name": "Return to Hotel / Leisure Time",
            "description": "Rest at your lodging, refresh, and prepare for the evening.",
            "cost_usd": 0
        })
        
        # 5. Dinner
        timeline.append({
            "time": "07:30 PM - 09:30 PM",
            "type": "Meal",
            "name": "Dinner & Evening Leisure",
            "description": "Savor a relaxing dinner and explore the city's evening atmosphere.",
            "cost_usd": 25
        })
        
        # Calculate daily cost
        daily_cost = sum(t["cost_usd"] for t in timeline)
        
        formatted_days.append({
            "day": day_num,
            "cost_usd": daily_cost,
            "timeline": timeline
        })
        
    return formatted_days
