from pprint import pprint as debug

from mf._request import Request
from mf._response import Response
from mf._types import Scope, ASGIReceive, ASGISend, AsyncRequestHandler
from mf._asgi import ASGIEventType


class Microframework:
    def __init__(self) -> None:
        self._request_handlers_stack = {
            "get": {
                "404": self._default_404_handler,
            },
            "post": {
                "404": self._default_404_handler,
            },
        }

    async def __call__(self, scope: Scope, receive: ASGIReceive, send: ASGISend):
        debug(scope)

        proto_type = scope["type"]

        if proto_type == ASGIEventType.LIFESPAN.value:
            await self._handle_lifespan_events(scope, receive, send)
        elif proto_type == "http":
            await self._handle_http_events(scope, receive, send)
        else:
            raise

    async def _handle_http_events(self, scope: Scope, receive: ASGIReceive, send: ASGISend):
        handler = self._get_handler(scope["path"], scope["method"])

        response = await handler(Request())
        print(response)

        http_event = await receive()

        print("http event", http_event)

        await send({"type": "http.response.start", "status": response.status})
        await send({"type": "http.response.body", "body": response.body, "more_body": False})

    async def _handle_lifespan_events(self, scope: Scope, receive: ASGIReceive, send: ASGISend):
        while True:
            lifespan_event = await receive()

            if lifespan_event["type"] == ASGIEventType.LIFESPAN_STARTUP.value:
                try:
                    self._prepare()
                except Exception as err:
                    await send({
                        "type": ASGIEventType.LIFESPAN_STARTUP_FAILED.value,
                        "message": f"Unable to prepare application: {err}"
                    })
                else:
                    await send({
                        "type": ASGIEventType.LIFESPAN_STARTUP_COMPLETE.value
                    })
            elif lifespan_event["type"] == "lifespan.shutdown":
                try:
                    self._finalize()
                except Exception as err:
                    await send({
                        "type": ASGIEventType.LIFESPAN_SHUTDOWN_FAILED.value,
                        "message": f"Unable to finalize application: {err}"
                    })
                else:
                    await send({
                        "type": ASGIEventType.LIFESPAN_SHUTDOWN_COMPLETE.value
                    })
                    return

    def _get_handler(self, path: str, method: str) -> AsyncRequestHandler:
        if method.lower() not in self._request_handlers_stack:
            raise
        method_handlers = self._request_handlers_stack[method.lower()]
        return method_handlers["404"]

    def _prepare(self):
        pass

    def _finalize(self):
        pass

    def get(self, path: str):
        def dec(handler: AsyncRequestHandler):
            async def wrap(*args, **kwargs):
                response = await handler(*args, **kwargs)
                return response
            self._request_handlers_stack["get"][path] = wrap
            return wrap
        return dec

    def post(self, path: str):
        def dec(handler: AsyncRequestHandler):
            async def wrap(*args, **kwargs):
                response = await handler(*args, **kwargs)
                return response
            self._request_handlers_stack["post"][path] = wrap
            return wrap
        return dec

    async def _default_404_handler(self, *args, **kwargs):
        return Response(status=404)
