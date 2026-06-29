import logging
from typing import Dict, Any
from backend.tools.security import simulate_rate_limit

logger = logging.getLogger("BudgetCalculator")

async def calculate_budget(total_budget: float, days: int) -> Dict[str, Any]:
    """
    BudgetCalculator: Analyzes travel budget, splits it into categories, and flags issues.
    
    Args:
        total_budget: Total trip budget in USD
        days: Trip duration in days
    """
    await simulate_rate_limit()
    
    if total_budget <= 0:
        raise ValueError("Budget must be a positive number.")
    if days <= 0:
        raise ValueError("Days must be a positive integer.")
        
    logger.info(f"Executing BudgetCalculator tool for total_budget={total_budget}, days={days}")
    
    daily_budget = total_budget / days
    
    # Standard allocations (in percentages)
    hotel_pct = 0.40
    food_pct = 0.25
    attractions_pct = 0.15
    transport_pct = 0.10
    contingency_pct = 0.10
    
    # Calculate amounts
    hotel_total = total_budget * hotel_pct
    food_total = total_budget * food_pct
    attractions_total = total_budget * attractions_pct
    transport_total = total_budget * transport_pct
    contingency_total = total_budget * contingency_pct
    
    # Check if budget is low
    status = "healthy"
    warning = ""
    if daily_budget < 50:
        status = "critical"
        warning = "Extremely low budget! You may need to look for hostel dorms, eat street food, and visit only free attractions."
    elif daily_budget < 120:
        status = "budget"
        warning = "Economical budget. Restrict fine dining and paid attractions to stay within bounds."
    elif daily_budget > 350:
        status = "luxury"
        warning = "Comfortable luxury budget. Access top-tier hotels and premium dining."
        
    return {
        "daily_limit_usd": round(daily_budget, 2),
        "status": status,
        "warning": warning,
        "breakdown": {
            "accommodation_usd": round(hotel_total, 2),
            "food_usd": round(food_total, 2),
            "attractions_usd": round(attractions_total, 2),
            "transportation_usd": round(transport_total, 2),
            "contingency_usd": round(contingency_total, 2)
        }
    }
