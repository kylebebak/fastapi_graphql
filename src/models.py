from pydantic import BaseModel


class User(BaseModel):
    id: int
    name: str
    age: int


class UserIn(BaseModel):
    name: str
    age: int


class AddressIn(BaseModel):
    user_id: int
    email_address: str


class AddressDetailsIn(BaseModel):
    address_id: int
    details: str
