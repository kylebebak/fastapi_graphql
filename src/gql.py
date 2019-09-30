import graphene  # type: ignore

from src.db import User, Address, AddressDetails


class AddressDetailsType(graphene.ObjectType):
    id = graphene.Int()
    address_id = graphene.Int()
    details = graphene.String()


class AddressType(graphene.ObjectType):
    id = graphene.Int()
    user_id = graphene.Int()
    email_address = graphene.String()
    details = graphene.List(AddressDetailsType)

    async def resolve_details(self, info):
        objs = await AddressDetails.query.where(AddressDetails.address_id == self.id).gino.all()
        return objs


class UserType(graphene.ObjectType):
    id = graphene.Int()
    name = graphene.String()
    age = graphene.Int()
    addresses = graphene.List(AddressType)

    async def resolve_addresses(self, info):
        objs = await Address.query.where(Address.user_id == self.id).gino.all()
        return objs


class Query(graphene.ObjectType):
    hello = graphene.String(name=graphene.String(default_value="stranger"))
    users = graphene.List(UserType)

    async def resolve_hello(self, info, name):
        return "Hello " + name

    async def resolve_users(self, info):
        objs = await User.query.gino.all()
        return objs
