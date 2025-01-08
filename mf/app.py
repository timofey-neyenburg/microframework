from pprint import pprint as debug

from mf._types import Scope, ASGIReceive, ASGISend, AsyncRequestHandler
from mf._exceptions import ProtocolError


class Microframework:
    def __init__(self) -> None:
        self._request_handlers_stack = {}

    async def __call__(self, scope: Scope, receive: ASGIReceive, send: ASGISend):
        debug(scope)

        try:
            asgi_version = scope["asgi"]["version"]
        except KeyError:
            asgi_version = "3.0"

        proto_type = scope["type"]

        if proto_type == "lifespan":
            lifespan_event = await receive()
            debug(("lifespan event:", lifespan_event))

        if proto_type != "http":
            raise ProtocolError

        event = await receive()

        debug(("receive:", event))

        if proto_type == "http":
            await send(scope)

    def get(self, path: str):
        def dec(handler: AsyncRequestHandler):
            async def wrap(*args, **kwargs):
                response = await handler(*args, **kwargs)
                return response
            self._request_handlers_stack[path] = wrap
            return wrap
        return dec

