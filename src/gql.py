from typing import Dict, List
from collections import defaultdict

import graphene  # type: ignore
from aiodataloader import DataLoader  # type: ignore

from src.db import User, Address, AddressDetails


class AddressesByUserIdLoader(DataLoader):
    async def batch_load_fn(self, ids) -> List[List[Address]]:
        adresses_by_user_id: Dict[int, List[Address]] = defaultdict(list)

        for address in await Address.query.where(Address.user_id.in_(ids)).gino.all():
            adresses_by_user_id[address.user_id].append(address)

        return [adresses_by_user_id.get(uid, []) for uid in ids]


class DetailsByAddressIdLoader(DataLoader):
    async def batch_load_fn(self, ids) -> List[List[AddressDetails]]:
        details_by_address_id: Dict[int, List[AddressDetails]] = defaultdict(list)

        for details in await AddressDetails.query.where(AddressDetails.address_id.in_(ids)).gino.all():
            details_by_address_id[details.address_id].append(details)

        return [details_by_address_id.get(aid, []) for aid in ids]


a_loader = AddressesByUserIdLoader()
d_loader = DetailsByAddressIdLoader()


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
        return await d_loader.load(self.id)


class UserType(graphene.ObjectType):
    id = graphene.Int()
    name = graphene.String()
    age = graphene.Int()
    addresses = graphene.List(AddressType)

    async def resolve_addresses(self, info):
        return await a_loader.load(self.id)


class Query(graphene.ObjectType):
    hello = graphene.String(name=graphene.String(default_value="stranger"))
    users = graphene.List(lambda: UserType)

    async def resolve_hello(self, info, name):
        return "Hello " + name

    async def resolve_users(self, info):
        objs = await User.query.gino.all()
        return objs
