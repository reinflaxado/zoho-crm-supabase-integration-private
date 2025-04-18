import logging
from typing import Dict, List, Any, Optional, Union
from supabase import create_client, Client
from app.config import settings
from app.models.schemas import SupabaseResponse

# Configure logging
logger = logging.getLogger(__name__)

class SupabaseService:
    """Service for interacting with Supabase."""
    
    def __init__(self):
        self.url = settings.SUPABASE_URL
        self.key = settings.SUPABASE_KEY
        self._client = None
    
    @property
    def client(self) -> Client:
        """
        Get Supabase client instance.
        
        Creates a new client if one doesn't exist.
        """
        if not self._client:
            self._client = create_client(self.url, self.key)
        return self._client
    
    async def store_data(
        self,
        table: str,
        data: Union[Dict[str, Any], List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """
        Store data in Supabase.
        
        For single records, it uses upsert.
        For multiple records, it uses bulk upsert.
        """
        try:
            # Convert single record to list
            if isinstance(data, dict):
                data = [data]
            
            if not data:
                logger.warning(f"No data to store in {table}")
                return {"success": True, "data": None}
            
            # Check if the data is for deletion
            if "deleted" in data[0] and data[0].get("deleted") is True:
                # This is a delete operation
                record_ids = [item["id"] for item in data if "id" in item]
                
                if not record_ids:
                    logger.warning("No IDs found for deletion")
                    return {"success": True, "data": None}
                
                # Delete the records
                response = self.client.table(table).delete().in_("id", record_ids).execute()
                
                return {
                    "success": True,
                    "data": {"deleted": len(record_ids)}
                }
            
            # This is an insert or update operation
            response = self.client.table(table).upsert(data).execute()
            
            # Parse response
            if hasattr(response, "data"):
                return {"success": True, "data": response.data}
            else:
                return {"success": True, "data": response}
                
        except Exception as e:
            logger.error(f"Error storing data in Supabase: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def query_data(
        self,
        table: str,
        query_params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Query data from Supabase.
        
        Args:
            table: Table name to query
            query_params: Dictionary of query parameters
                - limit: Maximum number of records to return
                - offset: Offset for pagination
                - select: Columns to select
                - order: Order by column
                - filter: Filter conditions
        """
        try:
            # Start the query
            query = self.client.table(table).select("*")
            
            # Apply query parameters if provided
            if query_params:
                # Apply select
                if "select" in query_params:
                    query = self.client.table(table).select(query_params["select"])
                
                # Apply filters
                if "filter" in query_params:
                    for filter_condition in query_params["filter"]:
                        column = filter_condition.get("column")
                        operator = filter_condition.get("operator", "eq")
                        value = filter_condition.get("value")
                        
                        if not all([column, operator, value is not None]):
                            continue
                        
                        # Apply filter based on operator
                        if operator == "eq":
                            query = query.eq(column, value)
                        elif operator == "neq":
                            query = query.neq(column, value)
                        elif operator == "gt":
                            query = query.gt(column, value)
                        elif operator == "lt":
                            query = query.lt(column, value)
                        elif operator == "gte":
                            query = query.gte(column, value)
                        elif operator == "lte":
                            query = query.lte(column, value)
                        elif operator == "in":
                            query = query.in_(column, value)
                        elif operator == "like":
                            query = query.like(column, value)
                
                # Apply order
                if "order" in query_params:
                    column = query_params["order"].get("column")
                    ascending = query_params["order"].get("ascending", True)
                    
                    if column:
                        if ascending:
                            query = query.order(column)
                        else:
                            query = query.order(column, desc=True)
                
                # Apply limit and offset
                if "limit" in query_params:
                    query = query.limit(query_params["limit"])
                
                if "offset" in query_params:
                    query = query.offset(query_params["offset"])
            
            # Execute the query
            response = query.execute()
            
            # Parse response
            if hasattr(response, "data"):
                return response.data
            else:
                return response or []
                
        except Exception as e:
            logger.error(f"Error querying data from Supabase: {str(e)}")
            raise 