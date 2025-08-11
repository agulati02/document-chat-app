from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from utils.bootstrap import get_database_session
from repositories.user_repository import UserRepository
from services.user_service import UserManagementService

# Repository dependencies
def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_database_session)]
) -> UserRepository:
    """Dependency to provide UserRepository instance."""
    return UserRepository(session)

# Service dependencies
def get_user_management_service(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)]
) -> UserManagementService:
    """Dependency to provide UserManagementService instance."""
    return UserManagementService(user_repository)
