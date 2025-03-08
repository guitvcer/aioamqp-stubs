import datetime
from typing import Iterable

from pamqp.commands import Basic
from pamqp.common import FieldTable

class Properties:
    __slots__: str | Iterable[str]

    content_type: str | None = None
    content_encoding: str | None = None
    headers: FieldTable | None = None
    delivery_mode: int | None = None
    priority: int | None = None
    correlation_id: str | None = None
    reply_to: str | None = None
    expiration: str | None = None
    message_id: str | None = None
    timestamp: datetime.datetime | None = None
    message_type: str | None = None
    user_id: str | None = None
    app_id: str | None = None
    cluster_id: str | None = None

    def __init__(
        self,
        content_type: str | None = None,
        content_encoding: str | None = None,
        headers: FieldTable | None = None,
        delivery_mode: int | None = None,
        priority: int | None = None,
        correlation_id: str | None = None,
        reply_to: str | None = None,
        expiration: str | None = None,
        message_id: str | None = None,
        timestamp: datetime.datetime | None = None,
        message_type: str | None = None,
        user_id: str | None = None,
        app_id: str | None = None,
        cluster_id: str | None = None,
    ) -> None: ...

def from_pamqp(instance: Basic.Properties) -> Properties: ...
