from pydantic import BaseModel, EmailStr

from app.schemas.users import UserOut

class ResponseLoggin(BaseModel):
    user: UserOut
    access_token: str 

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str