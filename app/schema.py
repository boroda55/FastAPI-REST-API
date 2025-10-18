import uuid
from datetime import datetime

from pydantic import BaseModel


class BaseUserRequest(BaseModel):
    name: str
    password: str


class IdResponse(BaseModel):
    id: int



class CreateAdvertisementRequest(BaseModel):
    title: str
    description: str
    price: int


class GetAdvertisementResponse(BaseModel):
    id: int
    title: str
    description: str
    price: int
    author_id: str
    date_of_creation: datetime


class SearchAdvertisementResponse(BaseModel):
    results: list[GetAdvertisementResponse]


class UpdateAdvertisementRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    price: int | None = None
    author_id: str | None = None


class LoginRequest(BaseUserRequest):
    name: str
    password: str


class LoginResponse(BaseModel):
    token: uuid.UUID

class CreateUserRequest(BaseUserRequest):
    name: str
    password: str

class CreateUserResponse(IdResponse):
    pass

class GetUserResponse(BaseUserRequest):
    id: int
    name: str
    role: str

class UpdateUserRequest(BaseModel):
    name: str | None = None
    password: str | None = None
    role: str | None = None
