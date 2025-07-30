# GraphQL schema definitions
import strawberry

from .mutation import Mutation
from .query import Query
from .subscription import Subscription

schema = strawberry.Schema(query=Query, mutation=Mutation, subscription=Subscription) 