import logging
from typing import List, Dict, Any, Optional
from backend.tools.base import load_json_dataset
from backend.tools.security import validate_city, simulate_rate_limit

logger = logging.getLogger("SearchAttractions")

async def search_attractions(city: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    SearchAttractions: Searches local attractions database.
    
    Args:
        city: Target city
        category: Sights category ('Culture', 'Nature', 'Adventure', 'Shopping', 'Relaxation')
    """
    await simulate_rate_limit()
    city_id = validate_city(city)
    
    logger.info(f"Executing SearchAttractions tool for city={city_id}, category={category}")
    
    attractions = load_json_dataset("tourist_attractions.json")
    results = []
    
    for attr in attractions:
        if attr["city_id"] == city_id:
            if category and attr["category"].lower() != category.lower():
                continue
            results.append(attr)
            
    return results
