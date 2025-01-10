import json


class Response:
    def __init__(
        self,
        content: dict | str | None = None,
        status: int = 200,
        headers: dict = {},
    ) -> None:
        self._status = status
        self._headers = headers

        if content is not None:
            self._body = content.encode() if isinstance(content, str) else json.dumps(content).encode()
        else:
            self._body = None

    @property
    def body(self) -> bytes | None:
        return self._body

    @property
    def status(self):
        return self._status

    @property
    def headers(self) -> dict:
        return self._headers
