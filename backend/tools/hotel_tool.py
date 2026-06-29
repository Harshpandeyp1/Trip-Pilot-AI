import logging
from typing import List, Dict, Any, Optional
from backend.tools.base import load_json_dataset
from backend.tools.security import validate_city, simulate_rate_limit

logger = logging.getLogger("SearchHotels")

async def search_hotels(city: str, max_price: Optional[float] = None, style: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    SearchHotels: Searches the local hotel database for hotels in a specific city.
    
    Args:
        city: Target city (e.g. 'tokyo')
        max_price: Maximum allowed price per night in USD
        style: Hotel category / travel style ('Budget', 'Boutique', 'Luxury')
    """
    await simulate_rate_limit()
    city_id = validate_city(city)
    
    logger.info(f"Executing SearchHotels tool for city={city_id}, max_price={max_price}, style={style}")
    
    hotels = load_json_dataset("hotels.json")
    results = []
    
    for hotel in hotels:
        if hotel["city_id"] == city_id:
            # Budget filtering
            if max_price is not None and hotel["price_per_night"] > max_price:
                continue
            # Style filtering
            if style and hotel["category"].lower() != style.lower():
                continue
            results.append(hotel)
            
    # Sort by rating descending
    results.sort(key=lambda x: x["rating"], reverse=True)
    return results
