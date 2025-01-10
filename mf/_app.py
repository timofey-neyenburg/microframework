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
        self._openapi_schema = {
        }

    async def __call__(self, scope: Scope, receive: ASGIReceive, send: ASGISend):
        try:
            asgi_version = tuple(map(int, scope["asgi"]["version"].split(".")))
        except KeyError as kerr:
            asgi_version = (2, 0)

        if asgi_version[0] < 3:
            raise ValueError("ASGI version < 3 is not supported")

        proto_type = scope["type"]

        if proto_type == ASGIEventType.LIFESPAN.value:
            await self._handle_lifespan_events(scope, receive, send)
        elif proto_type == "http":
            await self._handle_http_events(scope, receive, send)
        else:
            raise

    async def _handle_http_events(self, scope: Scope, receive: ASGIReceive, send: ASGISend):
        scheme = scope["scheme"]
        if scheme == "https":
            raise ValueError("HTTPS is not supported yet")

        url_path = scope["path"]
        http_method = scope["method"]
        query_params = scope["query_string"]
        headers = scope["headers"]
        client = scope["client"]

        if http_method.lower() not in ["get", "post"]:
            raise ValueError(f"Unsupported HTTP method: {http_method}")

        handler = self._get_handler(scope["path"], scope["method"])

        response = await handler(
            Request
            .from_scope(
                url_path,
                http_method,
                query_params,
                headers,
                client,
            )
        )

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
        handler = method_handlers.get(path)
        if handler is None:
            return method_handlers["404"]
        return handler

    def _prepare(self):
        pass

    def _finalize(self):
        pass

    def get(self, path: str):
        self.validate_path(path)
        dec = self.create_handler_decorator("get", path)
        return dec

    def post(self, path: str):
        self.validate_path(path)
        dec = self.create_handler_decorator("post", path)
        return dec

    def create_handler_decorator(self, method: str, path: str):
        def dec(handler: AsyncRequestHandler):
            async def wrap(*args, **kwargs):
                response = await handler(*args, **kwargs)
                return response
            self._request_handlers_stack[method][path] = wrap
            return wrap
        return dec

    def validate_path(self, path: str):
        if not path.startswith("/"):
            raise ValueError("Path must start with a '/' symbol")

    async def _default_404_handler(self, *args, **kwargs):
        return Response(status=404)
