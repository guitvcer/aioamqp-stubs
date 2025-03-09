import asyncio
from asyncio import BaseTransport, Task
from logging import Logger
from typing import Any, Awaitable, Callable, Iterable, NotRequired, Type, TypedDict
from typing_extensions import Unpack

from pamqp.commands import Connection
from pamqp.common import FieldTable
from pamqp.heartbeat import Heartbeat

from .channel import Channel, _Callback as Callback
from .frame import _Frame as Frame

logger: Logger

CONNECTING: int
OPEN: int
CLOSING: int
CLOSED: int

class _StreamWriter(asyncio.StreamWriter):
    def write(self, data: bytes | bytearray | memoryview) -> None: ...
    def writelines(self, data: Iterable[bytes | bytearray | memoryview]) -> None: ...
    def write_eof(self) -> None: ...

_Coro = Callable[[], Awaitable[Any]]

class _ConnectionTunning(TypedDict):
    channel_max: NotRequired[int]
    frame_max: NotRequired[int]
    heartbeat: NotRequired[int]

class _AmqpProtocolKwargs(TypedDict):
    on_error: NotRequired[Callable[[Exception], Any] | None]
    client_properties: NotRequired[FieldTable]
    channel_max: NotRequired[int]
    frame_max: NotRequired[int]
    heartbeat: NotRequired[int]

class _AmqpProtocolChannelKwargs(TypedDict):
    return_callback: NotRequired[Callback | None]

class AmqpProtocol(asyncio.StreamReaderProtocol):
    CHANNEL_FACTORY: Type[Channel]

    _reader: asyncio.StreamReader
    _on_error_callback: Callable[[Exception], Any] | None
    client_properties: FieldTable
    connection_tunning: _ConnectionTunning
    connecting: asyncio.Future
    connection_closed: asyncio.Event
    stop_now: asyncio.Event
    state: int
    version_major: int | None
    version_minor: int | None
    server_properties: FieldTable | None
    server_mechanisms: str | None
    server_locales: str | None
    worker: Task[_Coro] | None
    server_heartbeat: int | None
    _heartbeat_last_recv: float | None
    _heartbeat_last_send: float | None
    _heartbeat_recv_worker: Task[_Coro] | None
    _heartbeat_send_worker: Task[_Coro] | None
    channels: dict[int, Channel]
    server_frame_max: int | None
    server_channel_max: int | None
    channels_ids_ceil: int
    channels_ids_free: set[int]
    _drain_lock: asyncio.Lock

    def __init__(self, *args: Any, **kwargs: Unpack[_AmqpProtocolKwargs]) -> None: ...
    def connection_made(self, transport: BaseTransport) -> None: ...
    def eof_received(self) -> bool: ...
    def connection_lost(self, exc: Exception | None) -> None: ...
    def data_received(self, data: bytes) -> None: ...
    async def ensure_open(self) -> None: ...
    async def _drain(self) -> None: ...
    async def _write_frame(
        self,
        channel_id: int,
        request: Connection.Close
        | Heartbeat
        | Connection.StartOk
        | Connection.CloseOk
        | Connection.TuneOk
        | Connection.Open,
        drain: bool = True,
    ) -> None: ...
    async def close(
        self, no_wait: bool = False, timeout: float | None = None
    ) -> None: ...
    async def wait_closed(self, timeout: float | None = None) -> None: ...
    async def start_connection(
        self,
        host: Any,
        port: Any,
        login: str,
        password: str,
        virtualhost: str,
        ssl: Any = False,
        login_method: str = "PLAIN",
        insist: bool = False,
    ) -> None: ...
    async def get_frame(self) -> tuple[int, Frame]: ...
    async def dispatch_frame(
        self, frame_channel: int | None = None, frame: Frame | None = None
    ) -> None: ...
    def release_channel_id(self, channel_id: int) -> None: ...
    @property
    def channels_ids_count(self) -> int: ...
    def _close_channels(
        self,
        reply_code: int | None = None,
        reply_text: str | None = None,
        exception: Exception | None = None,
    ) -> None: ...
    async def run(self) -> None: ...
    async def heartbeat(self) -> None: ...
    async def send_heartbeat(self) -> None: ...
    def _heartbeat_timer_recv_reset(self) -> None: ...
    def _heartbeat_timer_send_reset(self) -> None: ...
    def _heartbeat_stop(self) -> None: ...
    async def _heartbeat_recv(self) -> None: ...
    async def _heartbeat_send(self) -> None: ...
    async def start(self, frame: Connection.Start) -> None: ...
    async def start_ok(
        self,
        client_properties: FieldTable,
        mechanism: str,
        auth: dict[str, str],
        locale: str,
    ) -> None: ...
    async def close_ok(self, frame: Any) -> None: ...
    async def server_close(self, frame: Connection.Close) -> None: ...
    async def _close_ok(self) -> None: ...
    async def tune(self, frame: Connection.Tune) -> None: ...
    async def tune_ok(
        self, channel_max: int, frame_max: int, heartbeat: int
    ) -> None: ...
    async def secure_ok(self, login_response: Any) -> None: ...
    async def open(
        self,
        virtual_host: str,
        capabilities: str = "",
        insist: bool = False,
    ) -> None: ...
    async def open_ok(self, frame: Any) -> None: ...
    async def channel(self, **kwargs: Unpack[_AmqpProtocolChannelKwargs]) -> None: ...
