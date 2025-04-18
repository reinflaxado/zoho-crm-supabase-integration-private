import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

# Configure logging
logger = logging.getLogger(__name__)

def parse_iso_datetime(date_string: str) -> Optional[datetime]:
    """
    Parse an ISO formatted date string into a datetime object.
    
    Args:
        date_string: ISO formatted date string
    
    Returns:
        datetime object or None if parsing fails
    """
    try:
        return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        try:
            # Fallback to standard ISO format
            return datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%fZ")
        except (ValueError, AttributeError):
            logger.warning(f"Failed to parse date string: {date_string}")
            return None

def transform_zoho_to_supabase(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform Zoho CRM data format to Supabase format.
    
    This function normalizes the data structure and field names
    to match the Supabase schema.
    
    Args:
        data: Zoho CRM data
    
    Returns:
        Transformed data for Supabase
    """
    # Create a new dict for transformed data
    transformed = {}
    
    # Copy the ID field
    if "id" in data:
        transformed["id"] = data["id"]
    
    # Transform fields based on data type
    for key, value in data.items():
        # Skip the ID field since we already copied it
        if key == "id":
            continue
        
        # Handle nested objects
        if isinstance(value, dict):
            # Check if it's a lookup field (has 'id' and 'name')
            if "id" in value and "name" in value:
                # Store both ID and name for lookup fields
                transformed[f"{key}_id"] = value["id"]
                transformed[f"{key}_name"] = value["name"]
            else:
                # Store nested object as JSON
                transformed[key] = json.dumps(value)
        
        # Handle lists
        elif isinstance(value, list):
            # Store lists as JSON
            transformed[key] = json.dumps(value)
        
        # Handle date fields
        elif key.lower().endswith(("date", "time", "at")) and isinstance(value, str):
            # Convert to datetime if possible
            dt = parse_iso_datetime(value)
            if dt:
                transformed[key] = dt.isoformat()
            else:
                transformed[key] = value
        
        # Handle other fields
        else:
            transformed[key] = value
    
    return transformed

def transform_batch_data(
    data: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Transform a batch of Zoho CRM data for Supabase.
    
    Args:
        data: List of Zoho CRM data records
    
    Returns:
        List of transformed records for Supabase
    """
    return [transform_zoho_to_supabase(record) for record in data] 