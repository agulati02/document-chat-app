import logging
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from utils.dependencies import get_user_management_service
from services.user_service import UserManagementService
from models.requests import LoginRequest, RegisterRequest

router = APIRouter(tags=["User Routers"])

@router.post("/login")
async def login(
    login_data: LoginRequest,
    user_service: Annotated[UserManagementService, Depends(get_user_management_service)]
):
    """
    Endpoint to log in a user.
    It verifies the user's credentials and returns a success message if valid.
    """    
    logging.info(f"Attempting to log in user: {login_data.username}")
    user = await user_service.verify_user(login_data.username, login_data.hashed_password)
    
    if user:
        return {"message": "Login successful", "user": user}
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")


@router.post("/register")
async def register(
    user_data: RegisterRequest,
    user_service: Annotated[UserManagementService, Depends(get_user_management_service)]
):
    """
    Endpoint to register a new user.
    """
    logging.info("Registering new user.")
    new_user = await user_service.register_user(user_data)
    return {"message": "User registered successfully", "username": user_data.username, "user_id": new_user.id}
