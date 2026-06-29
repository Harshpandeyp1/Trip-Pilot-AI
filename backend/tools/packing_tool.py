import logging
from typing import List, Dict, Any
from backend.tools.base import load_json_dataset
from backend.tools.security import validate_city, simulate_rate_limit

logger = logging.getLogger("PackingChecklist")

async def generate_packing_checklist(city: str, season: str, duration: int, interests: List[str]) -> Dict[str, Any]:
    """
    PackingChecklist: Compiles a custom packing list based on destination climate and activities.
    
    Args:
        city: Destination city
        season: Trip season ('spring', 'summer', 'autumn', 'winter', 'tropical')
        duration: Duration of trip in days
        interests: User travel interests list (e.g. ['Adventure', 'Culture'])
    """
    await simulate_rate_limit()
    city_id = validate_city(city)
    
    logger.info(f"Executing PackingChecklist tool for city={city_id}, season={season}, duration={duration}, interests={interests}")
    
    rules = load_json_dataset("packing_rules.json")
    
    checklist = {
        "essentials": list(rules["categories"]["essentials"]),
        "clothing": [],
        "activity_gear": []
    }
    
    # Season specific clothing
    cleaned_season = season.strip().lower()
    season_rules = rules["categories"]["season_specific"]
    
    if cleaned_season in season_rules:
        checklist["clothing"].extend(season_rules[cleaned_season])
    else:
        # Default to spring/mild if invalid
        checklist["clothing"].extend(season_rules["spring"])
        
    # Adjust clothing items based on duration (scale undergarments/socks)
    checklist["clothing"].append(f"{duration}x Sets of underwear & socks")
    
    # Activity specific items
    activity_rules = rules["categories"]["activity_specific"]
    for interest in interests:
        # Match interests to activity category
        for act_cat, items in activity_rules.items():
            if interest.lower() in act_cat.lower():
                checklist["activity_gear"].extend(items)
                
    # Remove duplicates
    checklist["clothing"] = list(set(checklist["clothing"]))
    checklist["activity_gear"] = list(set(checklist["activity_gear"]))
    
    return checklist
