from pydantic import BaseModel, EmailStr

class LoginForm(BaseModel):
    email: EmailStr
    password: str