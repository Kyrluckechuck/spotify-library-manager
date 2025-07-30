from typing import Optional

import strawberry
from strawberry.types import Info

from ..services.auth import AuthToken, LoginInput, auth_service


@strawberry.type
class AuthMutation:
    @strawberry.mutation
    def login(self, input: LoginInput) -> Optional[AuthToken]:
        user = auth_service.authenticate_user(input.username, input.password)
        if not user:
            return None

        access_token = auth_service.create_access_token(data={"sub": user.username})
        return AuthToken(access_token=access_token)


def get_current_user(info: Info) -> Optional[str]:
    context = info.context
    request = context.get("request")
    if not request:
        return None

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ")[1]
    return auth_service.verify_token(token)
