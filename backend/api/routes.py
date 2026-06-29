import asyncio
import json
import logging
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from backend.models.models import TripRequest, ExportRequest
from backend.tools.base import load_json_dataset
from backend.tools.export_tool import export_trip

# Import Google ADK classes and our agents definition
from google.adk.runners import Runner, agent_logs
from google.adk.sessions import InMemorySessionService
from backend.agents import trippilot_workflow

router = APIRouter()
logger = logging.getLogger("TripPilot-APIRoutes")

session_service = InMemorySessionService()
# Instantiate the runner with our sequential multi-agent workflow
runner = Runner(
    agent=trippilot_workflow,
    app_name="TripPilot AI",
    session_service=session_service
)

@router.get("/cities")
def get_cities():
    """Retrieve list of supported destinations."""
    try:
        cities = load_json_dataset("cities.json")
        return [{"id": c["id"], "name": c["name"], "country": c["country"], "description": c["description"]} for c in cities]
    except Exception as e:
        logger.error(f"Error fetching cities: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching city datasets")

@router.post("/plan")
async def plan_trip(request: TripRequest):
    """
    Receives request, launches Google ADK orchestrator, and returns final plan.
    """
    try:
        # Construct raw query JSON for ADK runner
        query_str = json.dumps(request.dict())
        
        # Run Google ADK runner programmatically (will trigger sub-agent delegation)
        result_str = await runner.run(query=query_str)
        
        # Parse result back to JSON
        return json.loads(result_str)
    except ValueError as val_err:
        logger.warning(f"Validation Error: {str(val_err)}")
        raise HTTPException(status_code=400, detail=str(val_err))
    except Exception as e:
        logger.error(f"Error executing trip planner runner: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Agent workflow failed: {str(e)}")

@router.get("/logs")
async def stream_logs():
    """
    Server-Sent Events (SSE) endpoint to stream real-time agent collaboration logs.
    This lets the frontend display a scrolling live-terminal of agent thinking!
    """
    async def event_generator():
        # Keep track of which logs we have sent
        sent_count = 0
        
        while True:
            # Check if there are new logs in the ADK runner buffer
            current_logs = list(agent_logs)
            if len(current_logs) > sent_count:
                for log in current_logs[sent_count:]:
                    yield f"data: {json.dumps(log)}\n\n"
                sent_count = len(current_logs)
            
            # Wait a short moment
            await asyncio.sleep(0.1)
            
            # If the last log is system completion, we can stop the stream (but keep SSE open briefly)
            if sent_count > 0 and current_logs[-1]["agent"] == "System" and "complete" in current_logs[-1]["message"].lower():
                # Yield final pulse and exit
                yield f"data: {json.dumps({'agent': 'System', 'message': 'Log stream ended.', 'type': 'system'})}\n\n"
                break
                
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.post("/export")
async def export_itinerary(request: ExportRequest):
    """
    Export itinerary JSON to Markdown.
    """
    try:
        formatted = await export_trip(request.itinerary, request.format_type)
        return {"content": formatted}
    except Exception as e:
        logger.error(f"Error exporting trip: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")
