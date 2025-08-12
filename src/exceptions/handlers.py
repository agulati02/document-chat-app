from fastapi import Request
from fastapi.responses import JSONResponse
from exceptions.user_exceptions import AuthorizationException, UserNotFoundException


class UserExceptionHandler:
    """Handles user-related exceptions."""
    
    @staticmethod
    def handle_user_not_found_exception(request: Request, exception: UserNotFoundException):
        """Handle UserNotFoundException."""
        return JSONResponse(
            status_code=401,
            content={"error": "Bad credentials", "username": exception.username},
        )
