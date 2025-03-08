class Envelope:
    __slots__: tuple[str, ...]

    consumer_tag: str
    delivery_tag: int
    exchange_name: str
    routing_key: str
    is_redeliver: bool

    def __init__(
        self,
        consumer_tag: str,
        delivery_tag: int,
        exchange_name: str,
        routing_key: str,
        is_redeliver: bool,
    ) -> None: ...

class ReturnEnvelope:
    __slots__: tuple[str, ...]

    reply_code: int
    reply_text: str
    exchange_name: str
    routing_key: str

    def __init__(
        self,
        reply_code: int,
        reply_text: str,
        exchange_name: str,
        routing_key: str,
    ) -> None: ...
