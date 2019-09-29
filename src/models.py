from typing import Any
from gino import Gino  # type: ignore


db = Gino()
Model: Any = db.Model


class Users(Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    age = db.Column(db.Integer)


class Addresses(Model):
    __tablename__ = "addresses"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(None, db.ForeignKey("users.id"))
    email_address = db.Column(db.String, nullable=False)
