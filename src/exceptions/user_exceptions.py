class AuthorizationException(Exception):
    """Base class for authorization-related exceptions."""
    pass

class UserNotFoundException(AuthorizationException):
    """Exception raised when a user is not found."""
    def __init__(self, username: str):
        super().__init__(f"User '{username}' not found.")
        self.username = username
