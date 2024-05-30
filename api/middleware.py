from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth import get_user_model
from jwt import DecodeError, ExpiredSignatureError
import logging
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import UntypedToken
from urllib.parse import parse_qs

from .websocket_codes import WS_4001_UNAUTHORIZED


User = get_user_model()


@database_sync_to_async
def get_user(user_id):
    return User.objects.filter(id=user_id).first()


class JwtAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = parse_qs(scope["query_string"].decode())
        token = query_string.get("token", [None])[0]

        if token is None:
            logging.warning(
                "No token provided to websocket endpoint. Closing connection..."
            )
            return await self.close_connection(send, WS_4001_UNAUTHORIZED)

        try:
            validated_token = UntypedToken(token)
            user_id = validated_token["user_id"]
            scope["user"] = await get_user(user_id)
            if scope["user"] is None:
                raise InvalidToken("User does not exist.")
        except (
            DecodeError,
            ExpiredSignatureError,
            InvalidToken,
            TokenError,
        ) as error:
            if isinstance(error, DecodeError):
                logging.error(f"Decode Error: {error}")
            elif isinstance(error, ExpiredSignatureError):
                logging.error(f"Expired Signature Error: {error}")
            elif isinstance(error, InvalidToken):
                logging.error(f"Invalid Token Error: {error}")
            elif isinstance(error, TokenError):
                logging.error(f"Token Error: {error}")
            else:
                logging.error(f"Generic Token Error: {error}")

            return await self.close_connection(send, WS_4001_UNAUTHORIZED)

        return await super().__call__(scope, receive, send)

    async def close_connection(self, send, code: int):
        await send({"code": code, "type": "websocket.close"})
