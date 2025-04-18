from typing import Dict, List, Any, Optional, Union
from enum import Enum
from pydantic import BaseModel, Field


class OperationType(str, Enum):
    """Enum for webhook operation types."""
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    BULK_CREATE = "BULK_CREATE"
    BULK_UPDATE = "BULK_UPDATE"
    BULK_DELETE = "BULK_DELETE"


class WebhookPayload(BaseModel):
    """Schema for incoming webhook payloads from Zoho CRM."""
    operation: OperationType
    resource: str = Field(..., description="Resource type (Leads, Contacts, etc.)")
    triggered_at: str = Field(..., description="ISO formatted timestamp")
    source: Optional[str] = None
    data: List[Dict[str, Any]] = Field(..., description="The actual data payload")
    token: Optional[str] = None
    
    class Config:
        use_enum_values = True


class WebhookResponse(BaseModel):
    """Schema for webhook response."""
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None


class ZohoToken(BaseModel):
    """Schema for Zoho OAuth tokens."""
    access_token: str
    refresh_token: Optional[str] = None
    expires_in: int
    token_type: str = "Bearer"
    api_domain: Optional[str] = None
    created_at: Optional[int] = None


class SupabaseResponse(BaseModel):
    """Schema for Supabase responses."""
    success: bool
    data: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None
    error: Optional[str] = None 