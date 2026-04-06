import httpx
from app.config import settings


class BackendService:
    """Service to communicate with the TourStats backend API"""
    
    def __init__(self):
        self.backend_url = settings.BACKEND_URL.rstrip('/')
    
    async def get_or_create_user(self, telegram_id: int, telegram_username: str) -> dict:
        """Get or create a user based on Telegram username (matches web app)"""
        # Use the actual Telegram username to match web app registration
        # If username is None, fallback to tg_{id}
        telegram_alias = telegram_username if telegram_username else f"tg_{telegram_id}"
        # Remove @ prefix if present
        telegram_alias = telegram_alias.lstrip('@')
        
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


    async def set_password(self, telegram_alias: str, password: str) -> dict:
        """Set password for a user"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{self.backend_url}/api/users/set-password",
                json={"telegram_alias": telegram_alias, "password": password}
            )
            if response.status_code == 200:
                return response.json()
            raise Exception(f"Failed to set password: {response.text}")
    
    async def change_password(self, telegram_alias: str, new_password: str) -> dict:
        """Change password for a user"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{self.backend_url}/api/users/change-password",
                json={"telegram_alias": telegram_alias, "new_password": new_password}
            )
            if response.status_code == 200:
                return response.json()
            raise Exception(f"Failed to change password: {response.text}")
    
    async def remove_password(self, telegram_alias: str) -> dict:
        """Remove password protection"""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{self.backend_url}/api/users/remove-password",
                params={"telegram_alias": telegram_alias}
            )
            if response.status_code == 200:
                return response.json()
            raise Exception(f"Failed to remove password: {response.text}")


# Singleton instance
backend_service = BackendService()
