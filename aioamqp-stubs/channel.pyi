import asyncio
import datetime
from logging import Logger
from typing import Any, Awaitable, Callable, Iterator, TypedDict
from typing_extensions import NotRequired

from pamqp.commands import Basic, Channel as pChannel, Confirm, Exchange, Queue
from pamqp.common import Arguments, FieldTable
from pamqp.frame import FrameTypes

from .envelope import ReturnEnvelope
from .properties import Properties
from .protocol import AmqpProtocol, _Coro as Coro

logger: Logger

_Callback = Callable[["Channel", bytes, ReturnEnvelope, Properties], Awaitable[Any]]
_Frame = (
    pChannel.OpenOk
    | pChannel.FlowOk
    | pChannel.CloseOk
    | pChannel.Close
    | Exchange.DeclareOk
    | Exchange.BindOk
    | Exchange.UnbindOk
    | Exchange.DeleteOk
    | Queue.DeclareOk
    | Queue.DeleteOk
    | Queue.BindOk
    | Queue.UnbindOk
    | Queue.PurgeOk
    | Basic.QosOk
    | Basic.ConsumeOk
    | Basic.CancelOk
    | Basic.GetOk
    | Basic.GetEmpty
    | Basic.Deliver
    | Basic.Cancel
    | Basic.Ack
    | Basic.Nack
    | Basic.RecoverOk
    | Basic.Return
    | Confirm.SelectOk
)

class _FlowResult(TypedDict):
    active: bool

class _QueueDeclareResult(TypedDict):
    message_count: int
    consumer_count: int
    queue: str

class _QueuePurgeResult(TypedDict):
    message_count: int

class _Properties(TypedDict):
    content_type: NotRequired[str | None]
    content_encoding: NotRequired[str | None]
    headers: NotRequired[FieldTable | None]
    delivery_mode: NotRequired[int | None]
    priority: NotRequired[int | None]
    correlation_id: NotRequired[str | None]
    reply_to: NotRequired[str | None]
    expiration: NotRequired[str | None]
    message_id: NotRequired[str | None]
    timestamp: NotRequired[datetime.datetime | None]
    message_type: NotRequired[str | None]
    user_id: NotRequired[str | None]
    app_id: NotRequired[str | None]
    cluster_id: NotRequired[str]

class _BasicConsumeResult(TypedDict):
    consumer_tag: str

class _BasicGetResult(TypedDict):
    routing_key: str
    redelivered: bool
    delivery_tag: int
    exchange_name: str
    message: bytes | bytearray | memoryview
    properties: Properties
    message_count: int

class Channel:
    protocol: AmqpProtocol
    channel_id: int
    consumer_queues: dict
    consumer_callbacks: dict[str, _Callback]
    cancellation_callbacks: list[Callable[["Channel", str], Awaitable[Any]]]
    return_callback: _Callback | None
    response_future: None
    close_event: asyncio.Event
    cancelled_consumers: set[str]
    last_consumer_tag: str | None
    publisher_confirms: bool
    delivery_tag_iter: Iterator[int] | None
    _exchange_declare_lock: asyncio.Lock
    _queue_bind_lock: asyncio.Lock
    _futures: dict[str, asyncio.Future]
    _ctag_events: dict[str, asyncio.Event]

    def __init__(
        self,
        protocol: AmqpProtocol,
        channel_id: int,
        return_callback: _Callback | None = None,
    ) -> None: ...
    def _set_waiter(self, rpc_name: str) -> asyncio.Future: ...
    def _get_waiter(self, rpc_name: str) -> asyncio.Future: ...
    @property
    def is_open(self) -> bool: ...
    def connection_closed(
        self,
        server_code: int | None = None,
        server_reason: str | None = None,
        exception: Exception | None = None,
    ) -> None: ...
    async def dispatch_frame(self, frame: _Frame) -> None: ...
    async def _write_frame(
        self,
        channel_id: int,
        request: FrameTypes,
        check_open: bool = True,
        drain: bool = True,
    ) -> None: ...
    async def _write_frame_awaiting_response(
        self,
        waiter_id: str,
        channel_id: int,
        request: FrameTypes,
        no_wait: bool,
        check_open: bool = True,
        drain: bool = True,
    ) -> _FlowResult | bool | None: ...
    async def open(self) -> None: ...
    async def open_ok(self, frame: Any) -> None: ...
    async def close(
        self,
        reply_code: int = 0,
        reply_text: str = "Normal Shutdown",
    ) -> bool | None: ...
    async def close_ok(self, frame: Any) -> None: ...
    async def _send_channel_close_ok(self) -> None: ...
    async def server_channel_close(self, frame: pChannel.Close) -> None: ...
    async def flow(self, active: bool) -> _FlowResult: ...
    async def flow_ok(self, frame: pChannel.FlowOk) -> None: ...
    async def exchange_declare(
        self,
        exchange_name: str,
        type_name: str,
        passive: bool = False,
        durable: bool = False,
        auto_delete: bool = False,
        no_wait: bool = False,
        arguments: Arguments | None = None,
    ) -> bool: ...
    async def exchange(
        self,
        exchange_name: str,
        type_name: str,
        passive: bool = False,
        durable: bool = False,
        auto_delete: bool = False,
        no_wait: bool = False,
        arguments: Arguments | None = None,
    ) -> bool: ...
    async def exchange_declare_ok(self, frame: Any) -> asyncio.Future[bool]: ...
    async def exchange_delete(
        self,
        exchange_name: str,
        if_unused: bool = False,
        no_wait: bool = False,
    ) -> bool: ...
    async def exchange_delete_ok(self, frame: Any) -> None: ...
    async def exchange_bind(
        self,
        exchange_destination: str,
        exchange_source: str,
        routing_key: str,
        no_wait: bool = False,
        arguments: Arguments | None = None,
    ) -> bool: ...
    async def exchange_bind_ok(self, frame: Any) -> None: ...
    async def exchange_unbind(
        self,
        exchange_destination: str,
        exchange_source: str,
        routing_key: str,
        no_wait: bool = False,
        arguments: Arguments | None = None,
    ) -> bool: ...
    async def exchange_unbind_ok(self, frame: Any) -> None: ...
    async def queue_declare(
        self,
        queue_name: str | None = None,
        passive: bool = False,
        durable: bool = False,
        exclusive: bool = False,
        auto_delete: bool = False,
        no_wait: bool = False,
        arguments: Arguments | None = None,
    ) -> _QueueDeclareResult: ...
    async def queue(
        self,
        queue_name: str | None = None,
        passive: bool = False,
        durable: bool = False,
        exclusive: bool = False,
        auto_delete: bool = False,
        no_wait: bool = False,
        arguments: Arguments | None = None,
    ) -> _QueueDeclareResult: ...
    async def queue_declare_ok(self, frame: Queue.DeclareOk) -> None: ...
    async def queue_delete(
        self,
        queue_name: str,
        if_unused: bool = False,
        if_empty: bool = False,
        no_wait: bool = False,
    ) -> bool: ...
    async def queue_delete_ok(self, frame: Any) -> None: ...
    async def queue_bind(
        self,
        queue_name: str,
        exchange_name: str,
        routing_key: str,
        no_wait: bool = False,
        arguments: Arguments | None = None,
    ) -> bool: ...
    async def queue_bind_ok(self, frame: Any) -> None: ...
    async def queue_unbind(
        self,
        queue_name: str,
        exchange_name: str,
        routing_key: str,
        arguments: Arguments | None = None,
    ) -> bool: ...
    async def queue_unbind_ok(self, frame: Any) -> None: ...
    async def queue_purge(
        self, queue_name: str, no_wait: bool = False
    ) -> _QueuePurgeResult: ...
    async def queue_purge_ok(self, frame: Queue.PurgeOk) -> None: ...
    async def basic_publish(
        self,
        payload: bytes | bytearray | memoryview,
        exchange_name: str,
        routing_key: str,
        properties: _Properties | None = None,
        mandatory: bool = False,
        immediate: bool = False,
    ) -> None: ...
    async def basic_qos(
        self,
        prefetch_size: int = 0,
        prefetch_count: int = 0,
        connection_global: bool = False,
    ) -> bool: ...
    async def basic_qos_ok(self, frame: Any) -> bool: ...
    async def basic_server_nack(
        self,
        frame: Basic.Nack,
        delivery_tag: int | None = None,
    ) -> None: ...
    async def basic_consume(
        self,
        callback: Coro,
        queue_name: str = "",
        consumer_tag: str = "",
        no_local: bool = False,
        no_ack: bool = False,
        exclusive: bool = False,
        no_wait: bool = False,
        arguments: Arguments | None = None,
    ) -> _BasicConsumeResult: ...
    async def basic_consume_ok(self, frame: Basic.ConsumeOk) -> None: ...
    async def basic_deliver(self, frame: Basic.Deliver) -> None: ...
    async def server_basic_cancel(self, frame: Basic.Cancel) -> None: ...
    async def basic_cancel(self, consumer_tag: str, no_wait: bool = False) -> bool: ...
    async def basic_cancel_ok(self, frame: Basic.CancelOk) -> None: ...
    async def basic_get(
        self, queue_name: str = "", no_ack: bool = False
    ) -> _BasicGetResult: ...
    async def basic_get_ok(self, frame: Basic.GetOk) -> None: ...
    async def basic_get_empty(self, frame: Any) -> None: ...
    async def basic_client_ack(
        self, delivery_tag: str, multiple: bool = False
    ) -> None: ...
    async def basic_client_nack(
        self,
        delivery_tag: str,
        multiple: bool = False,
        requeue: bool = True,
    ) -> None: ...
    async def basic_server_ack(self, frame: Basic.Ack) -> None: ...
    async def basic_reject(self, delivery_tag: int, requeue: bool = False) -> None: ...
    async def basic_recover_async(self, requeue: bool = True) -> None: ...
    async def basic_recover(self, requeue: bool = True) -> bool: ...
    async def basic_recover_ok(self, frame: Any) -> None: ...
    async def basic_return(self, frame: Basic.Return) -> None: ...
    async def publish(
        self,
        payload: bytes | bytearray | memoryview,
        exchange_name: str,
        routing_key: str,
        properties: _Properties | None = None,
        mandatory: bool = False,
        immediate: bool = False,
    ) -> None: ...
    async def confirm_select(self, *, no_wait: bool = False) -> bool: ...
    async def confirm_select_ok(self, frame: Any) -> bool: ...
    def add_cancellation_callback(
        self,
        callback: Callable[["Channel", str], Awaitable[Any]],
    ) -> None: ...
