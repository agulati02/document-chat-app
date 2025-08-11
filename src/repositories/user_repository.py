import logging
from typing import Any, Dict, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.orm import User
from models.requests import RegisterRequest

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_user(self, user_data: RegisterRequest) -> User:
        """Create a new user in the database."""
        try:
            # Create user object from dict
            user = User(**dict(user_data))
            
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            return user
        except Exception as e:
            logging.error(f"Error creating user: {e}")
            await self.session.rollback()
            raise e
    
    async def get_user(self, filter_criteria: Dict[str, Any]) -> Optional[User]:
        """Retrieve a user from the database based on filter criteria."""
        try:
            stmt = select(User).filter_by(**filter_criteria)
            result = await self.session.execute(stmt)
            user = result.scalars().first()
            return user
        except Exception as e:
            logging.error(f"Error retrieving user: {e}")
            raise e
