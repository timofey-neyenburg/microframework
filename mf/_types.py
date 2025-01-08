from typing import Callable
from collections.abc import Awaitable

from mf._request import Request
from mf._response import Response


ASGIEvent = dict
Scope = dict
ASGIReceive = Callable[[], Awaitable[ASGIEvent]]
ASGISend = Callable[[ASGIEvent], Awaitable[None]]

AsyncRequestHandler = Callable[[Request], Awaitable[Response]]
