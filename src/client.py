import asyncio
import socketio
import argparse

class Client:

    def __init__(self, serverId) -> None:
        asyncio.run(self.intializeConnection(serverId))

    async def intializeConnection(self,serverId):
        self.socket = socketio.AsyncClient()
        await self.socket.connect(serverId)
        await self.socket.wait()

    def subscribe(self,topic):
        pass

    def unsubscribe(self,topic):
        pass

    def publish(self,topic, message):
        pass

    def listTopics(self):
        pass

    def getTopicStatus(self,topic):
        pass

    def handleUpdateTopic(message):
        pass

cli = Client("https://www.google.com")