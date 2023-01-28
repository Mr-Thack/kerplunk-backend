class SocketManager():
    def __init__(self):
        self.clients: dict = {}
        # uuid: ws

    async def connect(self, ws, uuid):
        await ws.accept()
        self.clients[uuid] = ws
        print(self.clients)

    def disconnect(self, uuid):
        """Disconnect by UUID"""
        print('Disconnecting')
        print(self.clients, uuid)
        del self.clients[uuid]

    async def dm(self, uuid, msg: str):
        await self.clients[uuid].send_text(msg)

    async def broadcast(self, msg: str):
        """Broadcast to all"""
        for ws in self.clients.values():
            await ws.send_text(msg)

    async def broadcast_ex(self, exuuid, msg: str):
        """Broadcast Excluding a Client"""
        for (uuid, ws) in self.clients.items():
            if uuid != exuuid:
                await ws.send_text(msg)

    async def recv(self, uuid):
        msg = await self.clients[uuid].receive_text()
        return msg
