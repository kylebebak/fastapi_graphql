from typing import Any
from uuid import UUID
from datetime import datetime

from gino import Gino  # type: ignore
from sqlalchemy import func  # type: ignore
from sqlalchemy.dialects.postgresql import UUID as Uuid  # type: ignore


db = Gino()
Model: Any = db.Model


class ModelMixin:
    # depends on `create extension "uuid-ossp";`
    id: UUID = db.Column(Uuid, primary_key=True, server_default=func.uuid_generate_v4())
    created_at: datetime = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: datetime = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class Group(Model, ModelMixin):
    __tablename__ = "groups"

    name: str = db.Column(db.String, nullable=False)


class User(Model, ModelMixin):
    __tablename__ = "users"

    group_id: UUID = db.Column(None, db.ForeignKey("groups.id"))
    name: str = db.Column(db.String)
    age: int = db.Column(db.Integer)


class Address(Model, ModelMixin):
    __tablename__ = "addresses"

    user_id: UUID = db.Column(None, db.ForeignKey("users.id"))
    email_address: str = db.Column(db.String, nullable=False)


class Details(Model, ModelMixin):
    __tablename__ = "details"

    address_id: UUID = db.Column(None, db.ForeignKey("addresses.id"))
    details: str = db.Column(db.String, nullable=False)
