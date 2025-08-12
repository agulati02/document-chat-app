import logging
from typing import Optional

from repositories.user_repository import UserRepository
from models.orm import User
from models.requests import LoginRequest, RegisterRequest
from exceptions.user_exceptions import UserNotFoundException
from utils.security import JWTHandler, PasswordManager
from config.settings import JWT_SECRET_KEY, JWT_ALGORITHM


class UserManagementService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        self.jwt_handler = JWTHandler(JWT_SECRET_KEY, JWT_ALGORITHM)
    
    async def register_user(self, user_data: RegisterRequest) -> User:
        """Create a new user."""
        logging.info(f"Creating user with username: {user_data.username}")
        user_data.password = PasswordManager.hash_password(user_data.password)
        return await self.user_repository.create_user(user_data)
    
    async def verify_user(self, login_data: LoginRequest) -> Optional[User]:
        """Verify if the user exists with correct credentials."""
        logging.info(f"Verifying user: {login_data.username}")
        user = await self.user_repository.get_user({
            "username": login_data.username
        })
        if user and PasswordManager.verify_password(user.password, login_data.password):
            logging.info(f"User {login_data.username} verified successfully.")
            return self.jwt_handler.encode({
                "username": user.username,
            })
        raise UserNotFoundException(login_data.username)