from uuid import UUID

from pydantic import BaseModel


class User(BaseModel):
    id: UUID
    name: str
    age: int
    group_id: UUID


class UserIn(BaseModel):
    name: str
    age: int
    group_id: UUID


class UserUpdate(BaseModel):
    name: str
    age: int


class AddressIn(BaseModel):
    user_id: UUID
    email_address: str


class AddressDetailsIn(BaseModel):
    address_id: UUID
    details: str


class GroupIn(BaseModel):
    name: str
