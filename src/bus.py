from typing import Set, Dict

from starlette.websockets import WebSocket


class Bus:
    """Not thread-safe.
    """

    def __init__(self) -> None:
        self.channels: Dict[str, Set[WebSocket]] = {}

    def add(self, ws: WebSocket, ch: str) -> None:
        self.channels.setdefault(ch, set()).add(ws)

    def remove(self, ws: WebSocket, ch: str = '') -> None:
        if not ch:
            for _, channel in self.channels.items():
                channel.remove(ws)
            return

        chnl = self.channels.get(ch)
        if chnl is None:
            return
        chnl.remove(ws)

    async def send(self, text: str, ch: str) -> None:
        channel = self.channels.get(ch)
        if channel is None:
            return
        for ws in channel:
            ws.send_text(text)
