import httpx
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class MCPToolRegistry:
    """MCP Tools for querying excursion statistics"""
    
    def __init__(self):
        self.backend_url = settings.BACKEND_URL
        self.tools = {
            "get_statistics": self.get_statistics,
            "get_excursions": self.get_excursions,
            "get_correlations": self.get_correlations,
        }

    async def execute_query(self, message: str) -> dict:
        """Execute a statistics query using MCP tools"""
        # For now, use a simple tool selection based on keywords
        if "correlation" in message.lower():
            return await self.get_correlations()
        elif "excursion" in message.lower() or "list" in message.lower():
            return await self.get_excursions()
        else:
            return await self.get_statistics()

    async def get_statistics(self) -> dict:
        """Get overall statistics"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.backend_url}/api/statistics/",
                    timeout=10.0,
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {"error": str(e)}

    async def get_excursions(self, limit: int = 10) -> dict:
        """Get recent excursions"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.backend_url}/api/excursions/?limit={limit}",
                    timeout=10.0,
                )
                response.raise_for_status()
                return {"excursions": response.json()}
        except Exception as e:
            logger.error(f"Error getting excursions: {e}")
            return {"error": str(e)}

    async def get_correlations(self) -> dict:
        """Get correlation analysis"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.backend_url}/api/statistics/correlations",
                    timeout=10.0,
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error getting correlations: {e}")
            return {"error": str(e)}
