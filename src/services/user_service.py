import logging
from typing import Optional
from repositories.user_repository import UserRepository
from models.orm import User
from models.requests import RegisterRequest

class UserManagementService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    async def register_user(self, user_data: RegisterRequest) -> User:
        """Create a new user."""
        logging.info(f"Creating user with username: {user_data.username}")
        return await self.user_repository.create_user(user_data)
    
    async def verify_user(self, username: str, password_hash: str) -> Optional[User]:
        """Verify if the user exists with correct credentials."""
        logging.info(f"Verifying user: {username}")
        user = await self.user_repository.get_user({
            "username": username, 
            "password_hash": password_hash
        })
        return user