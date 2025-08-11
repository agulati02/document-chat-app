from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    hashed_password: str

class RegisterRequest(BaseModel):
    username: str
    email: str
    password_hash: str
