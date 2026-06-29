from google.adk.agents.llm_agent import Agent
from google.adk.agents.workflow_agents import SequentialAgent

# Import tool references for definition tracing
from backend.tools.hotel_tool import search_hotels
from backend.tools.restaurant_tool import search_restaurants
from backend.tools.attraction_tool import search_attractions
from backend.tools.budget_tool import calculate_budget
from backend.tools.distance_tool import calculate_distance
from backend.tools.packing_tool import generate_packing_checklist
from backend.tools.schedule_tool import optimize_schedule
from backend.tools.weather_tool import lookup_weather
from backend.tools.currency_tool import lookup_currency

# 1. Define sub-agents with specific duties and allowed tools
budget_agent = Agent(
    name="BudgetAgent",
    model="gemini-2.5-flash",
    instruction="""You are a financial advisor agent. 
    Your job is to analyze the total travel budget, check offline currency conversion rates, 
    allocate funds across hotels/food/sights/transit, and flag low-budget warnings.
    Always prioritize keeping the trip within the user's financial limit.""",
    tools=[calculate_budget, lookup_currency]
)

hotel_agent = Agent(
    name="HotelAgent",
    model="gemini-2.5-flash",
    instruction="""You are an accommodation specialist. 
    Search the local hotel dataset, rank candidate hotels based on ratings and pricing limits, 
    and recommend the single best hotel matching the user's travel style (Luxury, Boutique, Budget).""",
    tools=[search_hotels]
)

attraction_agent = Agent(
    name="AttractionAgent",
    model="gemini-2.5-flash",
    instruction="""You are a tour guide agent. 
    Select the best points of interest in the target city matching the user's travel interests. 
    Filter out duplicate sights and optimize for popular locations from the offline database.""",
    tools=[search_attractions]
)

restaurant_agent = Agent(
    name="RestaurantAgent",
    model="gemini-2.5-flash",
    instruction="""You are a food critic agent. 
    Select dining spots matching the user's food preferences (Local, Vegetarian, Halal, etc.) 
    and budget level, curating morning/afternoon meal plans from the local dining set.""",
    tools=[search_restaurants]
)

transportation_agent = Agent(
    name="TransportationAgent",
    model="gemini-2.5-flash",
    instruction="""You are a transit logistics planner. 
    Identify the most appropriate transportation modes based on preferences (Public, Taxi, Rental, walking), 
    and calculate distance legs to minimize daily transit fatigue.""",
    tools=[calculate_distance]
)

schedule_agent = Agent(
    name="ScheduleAgent",
    model="gemini-2.5-flash",
    instruction="""You are a time-management coordinator. 
    Organize chosen activities, lunches, and dinners into linear daily timelines. 
    Verify that opening hours are respected and travel routes are logically sequenced.""",
    tools=[optimize_schedule]
)

packing_agent = Agent(
    name="PackingAgent",
    model="gemini-2.5-flash",
    instruction="""You are a travel preparation assistant. 
    Retrieve local average weather statistics and generate custom packing checklists 
    based on duration, climate season, and activities.""",
    tools=[lookup_weather, generate_packing_checklist]
)

safety_agent = Agent(
    name="SafetyAgent",
    model="gemini-2.5-flash",
    instruction="""You are a traveler safety advisor. 
    Provide local emergency contact phone numbers, visa requirements, 
    cultural customs, and critical travel tips for the destination.""",
    tools=[]
)

# 2. Define the main PlannerAgent who coordinates the workflow
planner_agent = Agent(
    name="PlannerAgent",
    model="gemini-2.5-flash",
    instruction="""You are the main coordinator of the TripPilot AI travel planner. 
    You receive the user planning request and delegate sub-tasks to the Budget, Hotel, 
    Attraction, Restaurant, Transportation, Schedule, Packing, and Safety agents. 
    You synthesize their outputs into a final consolidated travel itinerary.""",
    tools=[]
)

# 3. Create the sequential ADK workflow orchestrator
# This lists sub-agents in order of execution/dependency
trippilot_workflow = SequentialAgent(
    name="TripPilotWorkflow",
    sub_agents=[
        budget_agent,
        hotel_agent,
        attraction_agent,
        restaurant_agent,
        transportation_agent,
        schedule_agent,
        packing_agent,
        safety_agent
    ]
)
