from pydantic import BaseModel, EmailStr

class RegistrationRequestForm(BaseModel):
    email: EmailStr
    password: str