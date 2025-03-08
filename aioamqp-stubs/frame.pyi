from asyncio import StreamReader, StreamWriter

from pamqp.base import Frame
from pamqp.body import ContentBody
from pamqp.frame import FrameTypes
from pamqp.header import ContentHeader

DUMP_FRAMES: bool

def write(writer: StreamWriter, channel: FrameTypes, encoder: int) -> None: ...
async def read(
    reader: StreamReader,
) -> tuple[int, Frame | ContentHeader | ContentBody | None]: ...
