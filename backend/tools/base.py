import json
import logging
from backend.tools.security import secure_file_path

logger = logging.getLogger("TripPilot-Tools")

def load_json_dataset(filename: str) -> Any:
    """Helper to securely load a local JSON dataset."""
    try:
        safe_path = secure_file_path(filename)
        with open(safe_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Dataset not found: {filename}")
        raise FileNotFoundError(f"Database error: The dataset '{filename}' is missing.")
    except json.JSONDecodeError:
        logger.error(f"Malformed JSON: {filename}")
        raise ValueError(f"Database error: The dataset '{filename}' is corrupted.")
    except Exception as e:
        logger.error(f"Error loading dataset {filename}: {str(e)}")
        raise e
