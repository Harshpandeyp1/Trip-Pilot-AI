import asyncio
import json
import logging
import sys
from typing import List, Dict, Any, Optional

try:
    from mcp.server import Server
    import mcp.types as types
except ImportError:
    # Fallback to satisfy static analyzer if package isn't loaded yet
    class Server:
        def __init__(self, name: str): self.name = name
        def list_tools(self): return lambda f: f
        def call_tool(self): return lambda f: f

from backend.tools.hotel_tool import search_hotels
from backend.tools.restaurant_tool import search_restaurants
from backend.tools.attraction_tool import search_attractions
from backend.tools.budget_tool import calculate_budget
from backend.tools.distance_tool import calculate_distance
from backend.tools.packing_tool import generate_packing_checklist
from backend.tools.schedule_tool import optimize_schedule
from backend.tools.weather_tool import lookup_weather
from backend.tools.currency_tool import lookup_currency

logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger("TripPilot-MCPServer")

server = Server("trippilot-mcp-server")

@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """Expose available local datasets and helpers to LLM/agents."""
    return [
        types.Tool(
            name="SearchHotels",
            description="Searches local JSON database for hotels by city, max price, and hotel style.",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "e.g. 'tokyo', 'paris'"},
                    "max_price": {"type": "number", "description": "Max cost per night"},
                    "style": {"type": "string", "description": "Budget, Boutique, or Luxury"}
                },
                "required": ["city"]
            }
        ),
        types.Tool(
            name="SearchRestaurants",
            description="Finds local restaurants by city, cuisine type, and price level.",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {"type": "string"},
                    "cuisine": {"type": "string"},
                    "price_level": {"type": "string"}
                },
                "required": ["city"]
            }
        ),
        types.Tool(
            name="SearchAttractions",
            description="Retrieves top sights by city and interest category.",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {"type": "string"},
                    "category": {"type": "string"}
                },
                "required": ["city"]
            }
        ),
        types.Tool(
            name="BudgetCalculator",
            description="Calculates suggested budget splits (Hotels, Food, Sights, Transport) for duration.",
            inputSchema={
                "type": "object",
                "properties": {
                    "total_budget": {"type": "number"},
                    "days": {"type": "integer"}
                },
                "required": ["total_budget", "days"]
            }
        ),
        types.Tool(
            name="DistanceCalculator",
            description="Estimates travel distance (km) between list of coordinate points.",
            inputSchema={
                "type": "object",
                "properties": {
                    "points": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "lat": {"type": "number"},
                                "lng": {"type": "number"}
                            },
                            "required": ["lat", "lng"]
                        }
                    }
                },
                "required": ["points"]
            }
        ),
        types.Tool(
            name="PackingChecklist",
            description="Builds packing checklist matching destination, climate season, and duration.",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {"type": "string"},
                    "season": {"type": "string"},
                    "duration": {"type": "integer"},
                    "interests": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["city", "season", "duration", "interests"]
            }
        ),
        types.Tool(
            name="ScheduleOptimizer",
            description="Generates daily hour-by-hour timeline for activities, preventing impossible routing.",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {"type": "string"},
                    "activities": {"type": "array", "items": {"type": "object"}},
                    "days": {"type": "integer"}
                },
                "required": ["city", "activities", "days"]
            }
        ),
        types.Tool(
            name="WeatherLookup",
            description="Gets average local weather ranges and conditions by month.",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {"type": "string"}
                },
                "required": ["city"]
            }
        ),
        types.Tool(
            name="CurrencyLookup",
            description="Looks up current offline JPY/EUR/GBP rates relative to USD.",
            inputSchema={"type": "object", "properties": {}}
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Execute local MCP tool logic and return text response."""
    logger.info(f"MCP Call received: Tool '{name}' with arguments: {arguments}")
    
    try:
        if name == "SearchHotels":
            res = await search_hotels(
                city=arguments["city"],
                max_price=arguments.get("max_price"),
                style=arguments.get("style")
            )
        elif name == "SearchRestaurants":
            res = await search_restaurants(
                city=arguments["city"],
                cuisine=arguments.get("cuisine"),
                price_level=arguments.get("price_level")
            )
        elif name == "SearchAttractions":
            res = await search_attractions(
                city=arguments["city"],
                category=arguments.get("category")
            )
        elif name == "BudgetCalculator":
            res = await calculate_budget(
                total_budget=arguments["total_budget"],
                days=arguments["days"]
            )
        elif name == "DistanceCalculator":
            res = await calculate_distance(points=arguments["points"])
        elif name == "PackingChecklist":
            res = await generate_packing_checklist(
                city=arguments["city"],
                season=arguments["season"],
                duration=arguments["duration"],
                interests=arguments["interests"]
            )
        elif name == "ScheduleOptimizer":
            res = await optimize_schedule(
                city=arguments["city"],
                activities=arguments["activities"],
                days=arguments["days"]
            )
        elif name == "WeatherLookup":
            res = await lookup_weather(city=arguments["city"])
        elif name == "CurrencyLookup":
            res = await lookup_currency()
        else:
            raise ValueError(f"Unknown MCP tool: {name}")
            
        return [types.TextContent(type="text", text=json.dumps(res, indent=2))]
        
    except Exception as e:
        logger.error(f"Error executing MCP tool {name}: {str(e)}")
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    """Stdio entrypoint for MCP clients like Claude Desktop."""
    from mcp.server.stdio import stdio_server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        asyncio.run(main())
    else:
        print("MCP Server configured. Run with 'python -m backend.mcp.server run' to start stdio listener.")
