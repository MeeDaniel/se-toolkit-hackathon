import httpx
from app.config import settings


class BackendService:
    """Service to communicate with the TourStats backend API"""
    
    def __init__(self):
        self.backend_url = settings.BACKEND_URL.rstrip('/')
    
    async def get_or_create_user(self, telegram_id: int, telegram_username: str) -> dict:
        """Get or create a user based on Telegram username (via Telegram bot endpoint)
        
        This registers the user with requires_password=True, meaning they MUST set a password.
        """
        telegram_alias = telegram_username if telegram_username else f"tg_{telegram_id}"
        telegram_alias = telegram_alias.lstrip('@')

        async with httpx.AsyncClient(timeout=10.0) as client:
            # Try to get existing user first
            try:
                response = await client.get(
                    f"{self.backend_url}/api/users/{telegram_alias}"
                )
                if response.status_code == 200:
                    return response.json()
            except Exception:
                pass

            # Register user via Telegram endpoint (requires_password=True)
            response = await client.post(
                f"{self.backend_url}/api/users/register-telegram",
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
