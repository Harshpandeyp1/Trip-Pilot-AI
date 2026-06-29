import sys
import os
import pytest

# Add project root to python path for testing imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.tools.base import load_json_dataset
from backend.tools.security import validate_city
from backend.services.planner import generate_offline_trip_plan

def test_datasets_loading():
    """Verify that all offline JSON datasets load without raising errors."""
    cities = load_json_dataset("cities.json")
    hotels = load_json_dataset("hotels.json")
    restaurants = load_json_dataset("restaurants.json")
    attractions = load_json_dataset("tourist_attractions.json")
    
    assert len(cities) > 0
    assert len(hotels) > 0
    assert len(restaurants) > 0
    assert len(attractions) > 0

def test_city_validation():
    """Verify that security checks protect against illegal city inputs and traversal."""
    assert validate_city("Tokyo") == "tokyo"
    assert validate_city("New York") == "new_york"
    
    with pytest.raises(ValueError):
        validate_city("invalid_city_name_not_in_db")
        
    with pytest.raises(ValueError):
        validate_city("tokyo../path/traversal")

def test_planner_generation():
    """Verify that the multi-agent system execution yields a structured itinerary."""
    params = {
        "destination": "tokyo",
        "days": 2,
        "budget": 500.0,
        "interests": ["Culture"],
        "hotel_pref": "Budget",
        "food_pref": "Local",
        "transport_pref": "Public",
        "nationality": "US"
    }
    
    plan = generate_offline_trip_plan(params)
    
    assert plan["destination"] == "Tokyo"
    assert plan["days"] == 2
    assert plan["budget"] == 500.0
    assert "hotel" in plan
    assert "itinerary" in plan
    assert len(plan["itinerary"]) == 2
    assert "packing_list" in plan
    assert "safety_advice" in plan
    assert "expenses" in plan
