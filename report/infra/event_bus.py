import aio_pika
import json
import asyncio


class EventBus:
    def __init__(self, amqp_url: str = "amqp://guest:guest@rabbitmq/"):
        self.amqp_url = amqp_url

    async def connect(self):
        self.connection = await aio_pika.connect_robust(self.amqp_url)
        self.channel = await self.connection.channel()

    async def publish(self, event_name: str, message: dict):
        if not hasattr(self, "channel"):
            await self.connect()

        body = json.dumps(message).encode("utf-8")
        await self.channel.default_exchange.publish(
            aio_pika.Message(body=body),
            routing_key=event_name,
        )

    async def consume(self, event_name: str, callback):
        if not hasattr(self, "channel"):
            await self.connect()

        queue = await self.channel.declare_queue(event_name, durable=True)

        async for message in queue:
            async with message.process():
                data = json.loads(message.body)
                await callback(data)
