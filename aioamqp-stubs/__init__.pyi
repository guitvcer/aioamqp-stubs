from asyncio import Transport
from ssl import SSLContext
from typing import NotRequired, Type, Unpack

from .protocol import AmqpProtocol, _AmqpProtocolKwargs as AmqpProtocolKwargs

async def connect(
    host: str = "localhost",
    port: int | None = None,
    login: str = "guest",
    password: str = "guest",
    virtualhost: str = "/",
    ssl: SSLContext | bool | None = None,
    login_method: str = "PLAIN",
    insist: bool = False,
    protocol_factory: Type[AmqpProtocol] = AmqpProtocol,
    **kwargs: Unpack[AmqpProtocolKwargs],
) -> tuple[Transport, AmqpProtocol]: ...

class _FromUrlKwargs(AmqpProtocolKwargs):
    ssl: NotRequired[SSLContext | bool | None]

async def from_url(
    url: str,
    login_method: str = "PLAIN",
    insist: bool = False,
    protocol_factory: Type[AmqpProtocol] = AmqpProtocol,
    **kwargs: Unpack[_FromUrlKwargs],
) -> tuple[Transport, AmqpProtocol]: ...
