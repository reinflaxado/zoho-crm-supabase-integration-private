import hmac
import hashlib
import logging
from fastapi import APIRouter, Request, Depends, HTTPException, Header, status
from app.config import settings
from app.models.schemas import WebhookPayload, WebhookResponse
from app.services.zoho import ZohoService
from app.services.supabase import SupabaseService

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Create service instances
zoho_service = ZohoService()
supabase_service = SupabaseService()

async def verify_webhook_signature(
    request: Request,
    x_zoho_signature: str = Header(..., description="Webhook signature from Zoho")
) -> bool:
    """Verify the webhook signature from Zoho CRM."""
    body = await request.body()
    
    # Create expected signature using the webhook secret
    secret = settings.ZOHO_WEBHOOK_SECRET.encode()
    expected_signature = hmac.new(
        secret,
        body,
        hashlib.sha256
    ).hexdigest()
    
    # Compare signatures
    if not hmac.compare_digest(expected_signature, x_zoho_signature):
        logger.warning("Invalid webhook signature")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature"
        )
    
    return True

@router.post("/zoho", response_model=WebhookResponse)
async def handle_zoho_webhook(
    payload: WebhookPayload,
    verified: bool = Depends(verify_webhook_signature)
):
    """
    Handle webhooks from Zoho CRM.
    
    This endpoint receives notifications from Zoho CRM when records are
    created, updated, or deleted. The data is then synchronized with Supabase.
    """
    try:
        # Log the webhook payload
        logger.info(f"Received webhook: {payload.operation} - {payload.resource}")
        
        # Process the webhook data
        processed_data = await zoho_service.process_webhook(payload)
        
        # Store the data in Supabase
        result = await supabase_service.store_data(
            table=payload.resource.lower(),
            data=processed_data
        )
        
        # Respond to Zoho CRM
        return WebhookResponse(
            status="success",
            message=f"Processed {payload.operation} for {payload.resource}",
            data={"id": result.get("id", None)}
        )
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing webhook: {str(e)}"
        ) 