from typing import List, Dict

from starlette.websockets import WebSocket


class Bus:
    """Not thread-safe.
    """

    def __init__(self) -> None:
        self.channels: Dict[str, List[WebSocket]] = {}

    def add(self, ws: WebSocket, ch: str) -> None:
        self.channels.setdefault(ch, []).append(ws)

    def remove(self, ws: WebSocket, ch: str = '') -> None:
        if not ch:
            for _, channel in self.channels.items():
                try:
                    channel.remove(ws)
                except ValueError:
                    pass
            return

        chnl = self.channels.get(ch)
        if chnl is None:
            return
        try:
            chnl.remove(ws)
        except ValueError:
            pass

    async def send(self, text: str, ch: str) -> None:
        channel = self.channels.get(ch)
        if channel is None:
            return

        closed = []
        for ws in channel:
            try:
                await ws.send_text(text)
            except RuntimeError:
                closed.append(ws)

        for ws in closed:
            self.remove(ws)
