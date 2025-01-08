class Response:
    def __init__(self, status: int = 200) -> None:
        self._headers = {}
        self._body = None
        self._status = status

    @property
    def body(self) -> bytes | None:
        if self._body is not None:
            return str(self._body).encode()
        return self._body

    @property
    def status(self) -> int:
        return self._status

    @staticmethod
    def from_bytes(raw_response: bytes):
        return Response()

