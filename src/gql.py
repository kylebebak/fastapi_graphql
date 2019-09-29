from graphene import ObjectType, String  # type: ignore


class Query(ObjectType):
    hello = String(name=String(default_value="stranger"))
    goodbye = String()

    async def resolve_hello(self, info, name):
        return "Hello " + name

    async def resolve_goodbye(root, info):
        return "See ya!"
