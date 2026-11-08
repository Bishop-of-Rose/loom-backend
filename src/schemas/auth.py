from pydantic import BaseModel, EmailStr

class RegistrationRequestForm(BaseModel):
    email: EmailStr
    password: str

class ActivationRequestForm(BaseModel):
    email: EmailStr
    token: str

class LoginForm(BaseModel):
    email: EmailStr
    password: str