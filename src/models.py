from uuid import UUID
from datetime import datetime

from pydantic import BaseModel


class Model(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime


class User(Model):
    name: str
    age: int
    group_id: UUID


class Address(Model):
    user_id: UUID
    email_address: str


class Details(Model):
    address_id: UUID
    details: str


class Group(Model):
    name: str


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


class DetailsIn(BaseModel):
    address_id: UUID
    details: str


class GroupIn(BaseModel):
    name: str
