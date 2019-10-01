from typing import Dict, List
from collections import defaultdict

from memoization import cached  # type: ignore
import graphene  # type: ignore
from aiodataloader import DataLoader  # type: ignore

from src.db import User, Address, Details, Group


@cached
def get_loader(context, Loader):
    return Loader()


class AddressesByUserIdLoader(DataLoader):
    async def batch_load_fn(self, ids: List[int]) -> List[List[Address]]:
        adresses_by_user_id: Dict[int, List[Address]] = defaultdict(list)

        for address in await Address.query.where(Address.user_id.in_(ids)).gino.all():
            adresses_by_user_id[address.user_id].append(address)

        return [adresses_by_user_id.get(uid, []) for uid in ids]


class DetailsByAddressIdLoader(DataLoader):
    async def batch_load_fn(self, ids: List[int]) -> List[List[Details]]:
        details_by_address_id: Dict[int, List[Details]] = defaultdict(list)

        for details in await Details.query.where(Details.address_id.in_(ids)).gino.all():
            details_by_address_id[details.address_id].append(details)

        return [details_by_address_id.get(aid, []) for aid in ids]


class GroupLoader(DataLoader):
    async def batch_load_fn(self, group_ids: List[int]) -> List[Group]:
        group_by_id: Dict[int, Group] = {}

        for group in await Group.query.where(Group.id.in_(group_ids)).gino.all():
            group_by_id[group.id] = group

        return [group_by_id[group_id] for group_id in group_ids]


class AddressDetailsType(graphene.ObjectType):
    id = graphene.String()
    address_id = graphene.String()
    details = graphene.String()


class GroupType(graphene.ObjectType):
    id = graphene.String()
    name = graphene.String()


class AddressType(graphene.ObjectType):
    id = graphene.String()
    user_id = graphene.String()
    email_address = graphene.String()
    details = graphene.List(AddressDetailsType)

    async def resolve_details(self, info):
        loader = get_loader(info.context, DetailsByAddressIdLoader)
        return await loader.load(self.id)


class UserType(graphene.ObjectType):
    id = graphene.String()
    name = graphene.String()
    age = graphene.Int()
    group_id = graphene.String()
    addresses = graphene.List(AddressType)
    group = graphene.Field(GroupType)

    async def resolve_addresses(self, info):
        loader = get_loader(info.context, AddressesByUserIdLoader)
        return await loader.load(self.id)

    async def resolve_group(self, info):
        loader = get_loader(info.context, GroupLoader)
        return await loader.load(self.group_id)


class Query(graphene.ObjectType):
    hello = graphene.String(name=graphene.String(default_value="stranger"))
    users = graphene.List(UserType)
    addresses = graphene.List(AddressType)

    async def resolve_hello(self, info, name):
        return "Hello " + name

    async def resolve_users(self, info):
        objs = await User.query.gino.all()
        return objs

    async def resolve_addresses(self, info):
        objs = await Address.query.gino.all()
        return objs
