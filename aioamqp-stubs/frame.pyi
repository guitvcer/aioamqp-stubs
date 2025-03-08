from asyncio import StreamReader, StreamWriter

from pamqp.base import Frame as BaseFrame
from pamqp.body import ContentBody
from pamqp.frame import FrameTypes
from pamqp.header import ContentHeader
from pamqp.heartbeat import Heartbeat

DUMP_FRAMES: bool
_Frame = BaseFrame | ContentHeader | ContentBody | Heartbeat | None

def write(writer: StreamWriter, channel: int, encoder: FrameTypes) -> None: ...
async def read(reader: StreamReader) -> tuple[int, _Frame]: ...
