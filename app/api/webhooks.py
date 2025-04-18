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

@router.get("/leads")
async def get_leads(
    page: int = 1, 
    per_page: int = 50,
    criteria: str = None
):
    """
    Get leads from Zoho CRM with specific fields.
    
    This endpoint fetches leads from Zoho CRM with only the specified fields.
    """
    try:
        # Define the fields to fetch
        fields = [
            "id", 
            "First_Name", 
            "Last_Name", 
            "Lead_Status",
            "Lead_Source",
            "Cold_lead_intro",
            "Brand",
            "Created_Time",
            "Creation_date",
            "Contact_type"
        ]
        
        # Get leads from Zoho CRM
        leads = await zoho_service.get_leads(
            fields=fields,
            criteria=criteria,
            page=page,
            per_page=per_page
        )
        
        # Transform the data to match the required format
        formatted_leads = []
        for lead in leads:
            formatted_lead = {
                "lead_id": lead.get("id"),
                "first_name": lead.get("First_Name"),
                "last_name": lead.get("Last_Name"),
                "lead_status": lead.get("Lead_Status"),
                "lead_source": lead.get("Lead_Source"),
                "cold_lead_intro": lead.get("Cold_lead_intro"),
                "brand": lead.get("Brand"),
                "created_time": lead.get("Created_Time"),
                "creation_date": lead.get("Creation_date"),
                "contact_type": lead.get("Contact_type")
            }
            formatted_leads.append(formatted_lead)
        
        return {
            "status": "success",
            "count": len(formatted_leads),
            "data": formatted_leads
        }
        
    except Exception as e:
        logger.error(f"Error fetching leads: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching leads: {str(e)}"
        ) 