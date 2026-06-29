import logging
import math
from typing import List, Dict, Any
from backend.tools.security import simulate_rate_limit

logger = logging.getLogger("DistanceCalculator")

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great-circle distance between two points in kilometers."""
    R = 6371.0  # Earth radius in km
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

async def calculate_distance(points: List[Dict[str, float]]) -> Dict[str, Any]:
    """
    DistanceCalculator: Calculates distance between consecutive points (lat, lng).
    
    Args:
        points: A list of dicts with keys 'lat' and 'lng'
    """
    await simulate_rate_limit()
    
    if not points or len(points) < 2:
        return {
            "total_distance_km": 0.0,
            "legs": []
        }
        
    logger.info(f"Executing DistanceCalculator tool for points count={len(points)}")
    
    total = 0.0
    legs = []
    
    for i in range(len(points) - 1):
        p1 = points[i]
        p2 = points[i+1]
        
        # Validate keys
        if "lat" not in p1 or "lng" not in p1 or "lat" not in p2 or "lng" not in p2:
            raise ValueError("All points must contain 'lat' and 'lng' coordinate keys.")
            
        dist = haversine_distance(p1["lat"], p1["lng"], p2["lat"], p2["lng"])
        total += dist
        legs.append({
            "from_index": i,
            "to_index": i+1,
            "distance_km": round(dist, 2)
        })
        
    return {
        "total_distance_km": round(total, 2),
        "legs": legs
    }
