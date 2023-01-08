class SocketManager():
    def __init__(self):
        self.clients: dict = {}
        # uuid: ws

    async def connect(self, ws, uuid):
        await ws.accept()
        self.clients[uuid] = ws

    def disconnect(self, uuid):
        """Disconnect by UUID"""
        del self.clients[uuid]

    async def dm(self, uuid, msg: str):
        await self.clients[uuid].send_text(msg)

    async def broadcast(self, msg: str):
        """Broadcast to all"""
        for ws in self.clients.values():
            await ws.send_text(str)

    async def broadcast_ex(self, exuuid, msg: str):
        """Broadcast Excluding a Client"""
        for uuid, ws in self.clients:
            if uuid != ex_uuid:
                await ws.send_text(str)

    async def recv(self, uuid):
        msg = await self.clients[uuid].receive_text()
        return msg
