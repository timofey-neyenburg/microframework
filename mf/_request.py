from pprint import pprint
from typing import Optional


class Request:
    def __init__(
        self,
        path: str,
        method: str,
        headers: dict,
        query_params: dict,
        client: tuple[str, int],
        body: Optional[bytes] = None,
    ) -> None:
        self._path = path
        self._method = method
        self._headers = headers
        self._query = query_params
        self._client = client
        self._body = body

    @property
    def method(self):
        return self._method

    @property
    def body(self):
        return self._body

    @property
    def client(self):
        return self._client

    @property
    def query(self):
        return self._query

    @property
    def headers(self):
        return self._headers

    @property
    def path(self):
        return self._path

    def add_body(self, body: bytes):
        self._body = body

    @staticmethod
    def from_scope(
        url_path: str,
        http_method: str,
        query_params: bytes,
        headers: list[tuple[bytes, bytes]],
        client: tuple[str, int],
        body: Optional[bytes] = None,
    ):
        http_method = http_method.lower()
        headers_dict = Request.prepare_headers(headers)
        query_dict = Request.prepare_query_params(query_params)

        pprint((
            url_path,
            http_method,
            headers_dict,
            query_dict,
            client,
            body
        ))

        return Request(
            path=url_path,
            method=http_method,
            headers=headers_dict,
            query_params=query_dict,
            client=client,
            body=body
        )

    @staticmethod
    def convert_query_param_value(value: str):
        if value == "true":
            return True
        if value == "false":
            return False
        if value == "null":
            return None
        try:
            value_coverted = int(value)
            return value_coverted
        except:
            pass

        try:
            value_coverted = float(value)
            return value_coverted
        except:
            pass

        return value


    @staticmethod
    def prepare_headers(headers: list[tuple[bytes, bytes]]):
        return {
            key.decode().lower(): value.decode()
            for key, value in headers
        }

    @staticmethod
    def prepare_query_params(query: bytes):
        query_string = query.decode()

        if "&" in query_string:
            query_pairs = [pair.split("=") for pair in query_string.split("&")]
            query_dict = {}
            for k, v in query_pairs:
                converted = Request.convert_query_param_value(v)
                if k in query_dict:
                    if isinstance(query_dict[k], list):
                        query_dict[k].append(converted)
                    else:
                        query_dict[k] = [query_dict[k], converted]
                else:
                    query_dict[k] = converted
        else:
            pair = query_string.split("=")
            query_dict = {pair[0]: pair[1]}

        return query_dict


