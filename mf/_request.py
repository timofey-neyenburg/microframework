class Request:
    def __init__(self) -> None:
        self._headers = {}
        self._query = {}
        self._body = None

    @staticmethod
    def from_bytes(raw_request: bytes):
        return Request()
