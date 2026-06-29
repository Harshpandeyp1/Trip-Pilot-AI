import logging
from typing import List, Dict, Any, Optional
from backend.tools.base import load_json_dataset
from backend.tools.security import validate_city, simulate_rate_limit

logger = logging.getLogger("SearchRestaurants")

async def search_restaurants(city: str, cuisine: Optional[str] = None, price_level: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    SearchRestaurants: Searches local dining database matching criteria.
    
    Args:
        city: Target city
        cuisine: Cuisine preference ('Local', 'Vegetarian', 'Fine Dining', 'Casual')
        price_level: Price level ('Budget', 'Mid-Range', 'Luxury')
    """
    await simulate_rate_limit()
    city_id = validate_city(city)
    
    logger.info(f"Executing SearchRestaurants tool for city={city_id}, cuisine={cuisine}, price_level={price_level}")
    
    restaurants = load_json_dataset("restaurants.json")
    results = []
    
    for rest in restaurants:
        if rest["city_id"] == city_id:
            # Cuisine check
            if cuisine and rest["cuisine"].lower() != cuisine.lower():
                continue
            # Price level check
            if price_level and rest["price_level"].lower() != price_level.lower():
                continue
            results.append(rest)
            
    results.sort(key=lambda x: x["rating"], reverse=True)
    return results
