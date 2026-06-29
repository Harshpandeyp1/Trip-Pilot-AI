import os
import re
import logging
import asyncio
from typing import Any, Dict, List

# Setup simple logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("TripPilot-Security")

ALLOWED_CITIES = {"tokyo", "paris", "rome", "london", "new_york", "bali", "sydney"}

def validate_city(city: str) -> str:
    """Security Check: Prevents directory traversal & validates city exists in dataset."""
    if not city or not isinstance(city, str):
        raise ValueError("Invalid city parameter: must be a non-empty string.")
    
    # Lowercase & strip
    cleaned = city.strip().lower().replace(" ", "_")
    
    # Safe input regex (only alphabetic and underscores)
    if not re.match(r"^[a-z_]+$", cleaned):
        raise ValueError("Security Violation: City name contains illegal characters.")
        
    if cleaned not in ALLOWED_CITIES:
        raise ValueError(f"Destination '{city}' is not in the supported local database.")
        
    return cleaned

def secure_file_path(filename: str) -> str:
    """Security Check: Ensures file path stays within data/ directory."""
    base_data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
    target_path = os.path.abspath(os.path.join(base_data_dir, filename))
    
    # Check if target path lies under the base data directory (directory traversal protection)
    if not target_path.startswith(base_data_dir):
        logger.warning(f"Security Alert: Blocked directory traversal attempt to {target_path}")
        raise PermissionError("Access Denied: Path is outside the authorized data directory.")
        
    return target_path

def sanitize_input_text(text: str) -> str:
    """Security Check: Sanitizes text inputs to prevent prompt injection or script injection."""
    if not text:
        return ""
    # Strip HTML tags
    cleaned = re.sub(r"<[^>]*>", "", text)
    # Strip dangerous characters
    cleaned = re.sub(r"[;\"'$%^\&*]", "", cleaned)
    return cleaned.strip()

async def simulate_rate_limit():
    """Security/Resilience: Simulate API rate limiting for defensive coding verification."""
    rate_limit_delay = float(os.getenv("RATE_LIMIT_SIMULATION_MS", "50")) / 1000.0
    await asyncio.sleep(rate_limit_delay)
