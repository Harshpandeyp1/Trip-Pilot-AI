import logging
from typing import Dict, Any
from backend.tools.base import load_json_dataset
from backend.tools.security import simulate_rate_limit

logger = logging.getLogger("CurrencyLookup")

async def lookup_currency() -> Dict[str, Any]:
    """
    CurrencyLookup: Retrieves exchange rates from local database.
    """
    await simulate_rate_limit()
    
    logger.info("Executing CurrencyLookup tool")
    
    return load_json_dataset("currency.json")
