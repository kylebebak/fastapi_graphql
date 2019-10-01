from uuid import UUID
from datetime import datetime

from pydantic import BaseModel

from src import db


class Model(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime


class User(Model):
    name: str
    age: int
    group_id: UUID


class UserDb(User, db.User):
    pass


class Address(Model):
    user_id: UUID
    email_address: str


class AddressDb(Address, db.Address):
    pass


class Details(Model):
    address_id: UUID
    details: str


class DetailsDb(Details, db.Details):
    pass


class Group(Model):
    name: str


class GroupDb(Group, db.Group):
    pass


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
