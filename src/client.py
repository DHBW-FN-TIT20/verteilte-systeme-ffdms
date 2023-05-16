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

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        prog="Client",
        description="Client for Publisher"
    )

    parser.add_argument("-sub", "--subscribe", nargs="+", help="list of topics to subscribe", metavar="TOPIC")
    parser.add_argument("-p", "--publish", help="published topic", metavar="TOPIC")
    parser.add_argument("-m", "--message", help="message to be published to topic", metavar="STRING")
    parser.add_argument("-s", "--server", required=True, help="server address", metavar="ADDRESS:PORT")

    args = parser.parse_args()

    print(args)
    cli = Client("https://www.google.com")

