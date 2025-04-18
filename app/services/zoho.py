import time
import logging
import requests
from typing import Dict, List, Any, Optional
from app.config import settings
from app.models.schemas import WebhookPayload, ZohoToken

# Configure logging
logger = logging.getLogger(__name__)

class ZohoService:
    """Service for interacting with Zoho CRM API."""
    
    def __init__(self):
        self.client_id = settings.ZOHO_CLIENT_ID
        self.client_secret = settings.ZOHO_CLIENT_SECRET
        self.refresh_token = settings.ZOHO_REFRESH_TOKEN
        self.accounts_url = settings.ZOHO_ACCOUNTS_URL
        self.api_url = settings.ZOHO_API_URL
        self.access_token = None
        self.token_expiry = 0
    
    async def get_access_token(self) -> str:
        """
        Get a valid access token for Zoho CRM API.
        
        If the current token is still valid, return it.
        Otherwise, refresh the token.
        """
        # Check if token is still valid
        current_time = int(time.time())
        if self.access_token and current_time < self.token_expiry:
            return self.access_token
        
        # Token is expired or doesn't exist, refresh it
        try:
            logger.info("Refreshing Zoho access token")
            response = requests.post(
                f"{self.accounts_url}/oauth/v2/token",
                params={
                    "refresh_token": self.refresh_token,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "grant_type": "refresh_token"
                }
            )
            response.raise_for_status()
            token_data = response.json()
            
            # Parse token data
            token = ZohoToken(**token_data)
            
            # Update token information
            self.access_token = token.access_token
            self.token_expiry = current_time + token.expires_in - 60  # Buffer of 60 seconds
            
            logger.info("Zoho access token refreshed successfully")
            return self.access_token
            
        except Exception as e:
            logger.error(f"Error refreshing Zoho access token: {str(e)}")
            raise
    
    async def make_api_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make a request to the Zoho CRM API."""
        # Get a valid access token
        access_token = await self.get_access_token()
        
        # Prepare headers
        headers = {
            "Authorization": f"Zoho-oauthtoken {access_token}",
            "Content-Type": "application/json"
        }
        
        # Make the request
        try:
            response = requests.request(
                method=method.upper(),
                url=f"{self.api_url}/crm/v2/{endpoint}",
                headers=headers,
                params=params,
                json=data
            )
            response.raise_for_status()
            return response.json()
            
        except requests.HTTPError as e:
            logger.error(f"HTTP error in Zoho API request: {str(e)}")
            # Handle specific error codes
            if response.status_code == 401:
                # Token might be invalid, try to refresh and retry once
                self.access_token = None
                access_token = await self.get_access_token()
                headers["Authorization"] = f"Zoho-oauthtoken {access_token}"
                
                # Retry the request
                response = requests.request(
                    method=method.upper(),
                    url=f"{self.api_url}/crm/v2/{endpoint}",
                    headers=headers,
                    params=params,
                    json=data
                )
                response.raise_for_status()
                return response.json()
            else:
                # Re-raise the exception for other HTTP errors
                raise
        except Exception as e:
            logger.error(f"Error in Zoho API request: {str(e)}")
            raise
    
    async def get_leads(self, fields: Optional[List[str]] = None, criteria: Optional[str] = None, 
                        page: int = 1, per_page: int = 200) -> List[Dict[str, Any]]:
        """
        Get leads from Zoho CRM.
        
        Args:
            fields: List of field names to fetch (None for all fields)
            criteria: Search criteria
            page: Page number
            per_page: Records per page
            
        Returns:
            List of lead records
        """
        params = {
            "page": page,
            "per_page": per_page
        }
        
        # Add fields parameter if specified
        if fields:
            params["fields"] = ",".join(fields)
            
        # Add search criteria if specified
        if criteria:
            params["criteria"] = criteria
            
        # Make the API request
        response = await self.make_api_request(
            method="GET",
            endpoint="Leads",
            params=params
        )
        
        return response.get("data", [])
    
    async def process_webhook(self, payload: WebhookPayload) -> List[Dict[str, Any]]:
        """
        Process webhook payload from Zoho CRM.
        
        This method processes the webhook data and enriches it with additional
        data if needed before storing it in Supabase.
        """
        try:
            processed_data = []
            
            for item in payload.data:
                # Get the ID from the webhook data
                record_id = item.get("id")
                
                if not record_id:
                    logger.warning(f"Record ID not found in webhook data: {item}")
                    continue
                
                # For delete operations, we just need the ID
                if payload.operation in [
                    "DELETE", "BULK_DELETE"
                ]:
                    processed_data.append({"id": record_id, "deleted": True})
                    continue
                
                # For create and update operations, get full record details from Zoho
                try:
                    # Get detailed record from Zoho CRM
                    record_data = await self.make_api_request(
                        method="GET",
                        endpoint=f"{payload.resource}/{record_id}"
                    )
                    
                    # Extract the record from the response
                    if "data" in record_data and len(record_data["data"]) > 0:
                        full_record = record_data["data"][0]
                        processed_data.append(full_record)
                    else:
                        logger.warning(
                            f"Record not found in Zoho CRM: {payload.resource}/{record_id}"
                        )
                        # Use the data from the webhook as fallback
                        processed_data.append(item)
                        
                except Exception as e:
                    logger.error(
                        f"Error fetching record details from Zoho: {str(e)}"
                    )
                    # Use the data from the webhook as fallback
                    processed_data.append(item)
            
            return processed_data
            
        except Exception as e:
            logger.error(f"Error processing webhook data: {str(e)}")
            raise 