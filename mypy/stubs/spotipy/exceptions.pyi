from _typeshed import Incomplete

class SpotifyException(Exception):
    http_status: Incomplete
    code: Incomplete
    msg: Incomplete
    reason: Incomplete
    headers: Incomplete
    def __init__(self, http_status, code, msg, reason: Incomplete | None = None, headers: Incomplete | None = None) -> None: ...
