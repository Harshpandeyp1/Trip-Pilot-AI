import asyncio
import logging
import json
import time
import os
from typing import Optional, Dict, Any, List

# A global list to capture logs that can be streamed to the frontend via SSE
agent_logs: List[Dict[str, Any]] = []

def log_agent_interaction(agent_name: str, message: str, event_type: str = "info", tool_call: Optional[str] = None, tool_result: Optional[str] = None):
    """Utility to log agent actions both to standard Python logging, a file, and the global UI buffer."""
    log_entry = {
        "timestamp": time.time(),
        "agent": agent_name,
        "message": message,
        "type": event_type,
        "tool_call": tool_call,
        "tool_result": tool_result
    }
    agent_logs.append(log_entry)
    
    # Write to a file if configured
    log_file = os.getenv("LOG_FILE_PATH", "backend/logs/agent_collaboration.log")
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")
        
    logging.info(f"[{agent_name}] {message} " + 
                 (f"(Tool: {tool_call} -> {tool_result})" if tool_call else ""))

class Runner:
    """Simulated Runner class matching Google ADK."""
    def __init__(self, agent: Any, app_name: str, session_service: Any):
        self.agent = agent
        self.app_name = app_name
        self.session_service = session_service

    async def run(self, query: str, session_id: Optional[str] = None) -> str:
        """Runs the multi-agent system workflow based on the query."""
        # Reset logs for new run
        global agent_logs
        agent_logs.clear()
        
        log_agent_interaction("System", f"Starting ADK app '{self.app_name}'", "system")
        
        # Parse query JSON if possible, otherwise assume standard string query
        params = {}
        try:
            params = json.loads(query)
        except json.JSONDecodeError:
            params = {
                "destination": "tokyo",
                "days": 3,
                "budget": 1000,
                "interests": ["Culture", "Food"],
                "hotel_pref": "Boutique",
                "food_pref": "Local",
                "transport_pref": "Public"
            }
            
        # The sequential sub-agents execution simulation
        sub_agents = []
        if hasattr(self.agent, "sub_agents"):
            sub_agents = self.agent.sub_agents
        else:
            sub_agents = [self.agent]
            
        log_agent_interaction("PlannerAgent", f"Planner received travel request for {params.get('destination', 'Unknown')}. Orchestrating sub-agents.", "info")
        
        # Simulate rate limit / thinking time
        delay = float(os.getenv("RATE_LIMIT_SIMULATION_MS", "100")) / 1000.0
        
        # Run sub-agents sequentially
        results = {}
        for agent in sub_agents:
            agent_name = agent.name
            log_agent_interaction(agent_name, f"Initializing and analyzing instruction: {agent.instruction[:60]}...", "info")
            await asyncio.sleep(delay)
            
            # Execute agent tools or logic
            if agent_name == "BudgetAgent":
                log_agent_interaction(agent_name, "Calculating exchange rates and budget safety margins...", "info")
                # Simulate tool call
                log_agent_interaction(
                    agent_name, 
                    "Invoking tool CurrencyLookup", 
                    "tool_call", 
                    tool_call="CurrencyLookup(destination_currency)", 
                    tool_result="Success: Rates retrieved"
                )
                await asyncio.sleep(delay)
                log_agent_interaction(
                    agent_name, 
                    "Invoking tool BudgetCalculator", 
                    "tool_call", 
                    tool_call=f"BudgetCalculator(budget={params.get('budget')}, days={params.get('days')})", 
                    tool_result=f"Success: Daily cap set to {params.get('budget') // params.get('days')} USD"
                )
                await asyncio.sleep(delay)
                
            elif agent_name == "HotelAgent":
                log_agent_interaction(agent_name, f"Searching hotels matching style: {params.get('hotel_pref')}", "info")
                log_agent_interaction(
                    agent_name, 
                    "Invoking tool SearchHotels", 
                    "tool_call", 
                    tool_call=f"SearchHotels(city={params.get('destination')}, style={params.get('hotel_pref')})", 
                    tool_result="Success: Found 3 candidate hotels"
                )
                await asyncio.sleep(delay)
                
            elif agent_name == "AttractionAgent":
                log_agent_interaction(agent_name, f"Finding attractions matching interests: {', '.join(params.get('interests', []))}", "info")
                log_agent_interaction(
                    agent_name, 
                    "Invoking tool SearchAttractions", 
                    "tool_call", 
                    tool_call=f"SearchAttractions(city={params.get('destination')}, interests={params.get('interests')})", 
                    tool_result="Success: Selected top attractions without duplicates"
                )
                await asyncio.sleep(delay)
                
            elif agent_name == "RestaurantAgent":
                log_agent_interaction(agent_name, f"Matching culinary spots for preferences: {params.get('food_pref')}", "info")
                log_agent_interaction(
                    agent_name, 
                    "Invoking tool SearchRestaurants", 
                    "tool_call", 
                    tool_call=f"SearchRestaurants(city={params.get('destination')}, preference={params.get('food_pref')})", 
                    tool_result="Success: Curated meal plan"
                )
                await asyncio.sleep(delay)
                
            elif agent_name == "TransportationAgent":
                log_agent_interaction(agent_name, f"Planning travel routes with mode: {params.get('transport_pref')}", "info")
                log_agent_interaction(
                    agent_name, 
                    "Invoking tool DistanceCalculator", 
                    "tool_call", 
                    tool_call=f"DistanceCalculator(points)", 
                    tool_result="Success: Computed 15.4 km total estimated travel"
                )
                await asyncio.sleep(delay)
                
            elif agent_name == "ScheduleAgent":
                log_agent_interaction(agent_name, "Optimizing daily timeline to prevent overlaps...", "info")
                log_agent_interaction(
                    agent_name, 
                    "Invoking tool ScheduleOptimizer", 
                    "tool_call", 
                    tool_call="ScheduleOptimizer(daily_activities)", 
                    tool_result="Success: Linear day schedules organized"
                )
                await asyncio.sleep(delay)
                
            elif agent_name == "PackingAgent":
                log_agent_interaction(agent_name, "Generating packing guidelines based on local weather...", "info")
                log_agent_interaction(
                    agent_name, 
                    "Invoking tool WeatherLookup", 
                    "tool_call", 
                    tool_call=f"WeatherLookup(city={params.get('destination')})", 
                    tool_result="Success: Climate conditions analyzed"
                )
                await asyncio.sleep(delay)
                log_agent_interaction(
                    agent_name, 
                    "Invoking tool PackingChecklist", 
                    "tool_call", 
                    tool_call=f"PackingChecklist(city={params.get('destination')}, season)", 
                    tool_result="Success: Checklist compiled"
                )
                await asyncio.sleep(delay)
                
            elif agent_name == "SafetyAgent":
                log_agent_interaction(agent_name, "Compiling visa guidelines and emergency numbers...", "info")
                log_agent_interaction(agent_name, "Checking regional travel advisories and customs...", "info")
                await asyncio.sleep(delay)
                
            log_agent_interaction(agent_name, f"Completed tasks and handed results back to PlannerAgent.", "success")
            await asyncio.sleep(delay)
            
        log_agent_interaction("PlannerAgent", "All sub-agents completed execution. Generating final travel plan document.", "success")
        
        # Invoke actual backend service to compile the travel plan JSON using the JSON data files
        from backend.services.planner import generate_offline_trip_plan
        trip_plan = generate_offline_trip_plan(params)
        
        log_agent_interaction("System", "Trip plan generation complete.", "system")
        return json.dumps(trip_plan)
