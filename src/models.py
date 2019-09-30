from pydantic import BaseModel


class User(BaseModel):
    id: int
    name: str
    age: int
    group_id: int


class UserIn(BaseModel):
    name: str
    age: int
    group_id: int


class AddressIn(BaseModel):
    user_id: int
    email_address: str


class AddressDetailsIn(BaseModel):
    address_id: int
    details: str


class GroupIn(BaseModel):
    name: str
