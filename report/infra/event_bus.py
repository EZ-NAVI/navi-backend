import aio_pika
import json
import asyncio


class EventBus:
    def __init__(self, amqp_url: str = "amqp://guest:guest@rabbitmq/"):
        self.amqp_url = amqp_url
        self._connection = None
        self._channel = None
        self._exchange = None

    async def connect(self):
        if not self._connection or self._connection.is_closed:
            self._connection = await aio_pika.connect_robust(self.amqp_url)
            self._channel = await self._connection.channel()
            self._exchange = await self._channel.declare_exchange(
                "navi.events", aio_pika.ExchangeType.TOPIC
            )

    async def publish(self, routing_key: str, message: dict):
        await self.connect()
        body = json.dumps(message).encode("utf-8")
        await self._exchange.publish(
            aio_pika.Message(body=body),
            routing_key=routing_key,
        )

    async def consume(self, routing_key: str, callback):
        await self.connect()
        # 임시 큐 생성 (자동 삭제)
        queue = await self._channel.declare_queue("", exclusive=True)
        await queue.bind(self._exchange, routing_key)

        async for message in queue:
            async with message.process():
                data = json.loads(message.body)
                await callback(data)
