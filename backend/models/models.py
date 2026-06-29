from pydantic import BaseModel, Field
from typing import List, Optional

class TripRequest(BaseModel):
    destination: str = Field(..., description="Target city ID (e.g. 'tokyo')")
    budget: float = Field(..., gt=0, description="Total budget in USD")
    days: int = Field(..., gt=0, le=30, description="Duration in days")
    interests: List[str] = Field(default_factory=list, description="Travel interests list")
    hotel_pref: str = Field("Boutique", description="Hotel category preference")
    food_pref: str = Field("Local", description="Food preference")
    transport_pref: str = Field("Public", description="Transportation preference")
    nationality: str = Field("US", description="Passport nationality for visa check")

class ExportRequest(BaseModel):
    itinerary: dict = Field(..., description="Full generated itinerary payload")
    format_type: str = Field("markdown", description="Output format ('markdown' or 'html')")
