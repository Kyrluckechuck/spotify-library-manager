# GraphQL schema definitions
import strawberry

from ..graphql_types.scalars import DateTime
from .mutation import Mutation
from .query import Query
from .subscription import Subscription

schema = strawberry.Schema(
    query=Query, mutation=Mutation, subscription=Subscription, types=[DateTime]
)
