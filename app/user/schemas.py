from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreateDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    email: EmailStr
    password: str
    code: Optional[str] = None


class UserDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: Optional[int] = None
    name: Optional[str] = None


# Токен

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    user_id: Optional[int] = None
