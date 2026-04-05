import httpx
from app.config import settings


class BackendService:
    """Service to communicate with the TourStats backend API"""
    
    def __init__(self):
        self.backend_url = settings.BACKEND_URL.rstrip('/')
    
    async def get_or_create_user(self, telegram_id: int, telegram_username: str) -> dict:
        """Get or create a user based on Telegram ID"""
        # Use telegram_id as a unique identifier - map to telegram_alias
        telegram_alias = f"tg_{telegram_id}"
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                # Try to get existing user
                response = await client.get(
                    f"{self.backend_url}/api/users/{telegram_alias}"
                )
                if response.status_code == 200:
                    return response.json()
            except Exception:
                pass
            
            # Create new user
            response = await client.post(
                f"{self.backend_url}/api/users/",
                json={"telegram_alias": telegram_alias}
            )
            if response.status_code == 200:
                return response.json()
            
            raise Exception(f"Failed to create user: {response.text}")
    
    async def send_message_to_backend(self, user_id: int, message: str) -> dict:
        """Send a message to the backend for AI processing"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.backend_url}/api/excursions/from-message",
                json={
                    "user_id": user_id,
                    "message": message
                }
            )
            if response.status_code == 200:
                return response.json()
            raise Exception(f"Backend error: {response.status_code} - {response.text}")
    
    async def get_statistics(self, user_id: int) -> dict:
        """Get user statistics"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{self.backend_url}/api/statistics/",
                params={"user_id": user_id}
            )
            if response.status_code == 200:
                return response.json()
            raise Exception(f"Backend error: {response.status_code} - {response.text}")
    
    async def get_correlations(self, user_id: int) -> dict:
        """Get user correlations"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{self.backend_url}/api/statistics/correlations",
                params={"user_id": user_id}
            )
            if response.status_code == 200:
                return response.json()
            raise Exception(f"Backend error: {response.status_code} - {response.text}")
    
    async def get_excursions(self, user_id: int, offset: int = 0, limit: int = 10) -> dict:
        """Get user excursions with pagination"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{self.backend_url}/api/excursions/",
                params={"user_id": user_id, "offset": offset, "limit": limit}
            )
            if response.status_code == 200:
                return response.json()
            raise Exception(f"Backend error: {response.status_code} - {response.text}")


# Singleton instance
backend_service = BackendService()
