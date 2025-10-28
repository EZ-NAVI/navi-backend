import aio_pika
import asyncio
import json
from fastapi import FastAPI, WebSocket
from contextlib import asynccontextmanager

connections = {}  # user_id → websocket


@asynccontextmanager
async def lifespan(app: FastAPI):
    connection = None
    for attempt in range(10):  # 10번까지 재시도 (약 30초)
        try:
            connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq/")
            print("Connected to RabbitMQ")
            break
        except Exception as e:
            await asyncio.sleep(3)
    else:
        raise RuntimeError("RabbitMQ connection failed after retries")

    channel = await connection.channel()
    exchange = await channel.declare_exchange(
        "navi.events", aio_pika.ExchangeType.TOPIC
    )

    async def setup_queue(routing_key: str):
        queue = await channel.declare_queue("", exclusive=True)
        await queue.bind(exchange, routing_key)
        print(f"Bound to {routing_key}")

        async def handler(message):
            async with message.process():
                data = json.loads(message.body)
                print(f"Received from RabbitMQ ({routing_key}):", data)
                target_id = data.get("parentId") or data.get("childId")
                if target_id in connections:
                    await connections[target_id].send_json(data)
                    print(f"Sent to {target_id}")

        asyncio.create_task(queue.consume(handler))

    for rk in ["report.created", "report.reviewed"]:
        asyncio.create_task(setup_queue(rk))

    yield
    print("🧹 Relay server shutting down...")
    if connection:
        await connection.close()
        print("RabbitMQ connection closed")


app = FastAPI(title="NAVI Relay Server", lifespan=lifespan)


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(ws: WebSocket, user_id: str):
    """부모/자녀가 WebSocket으로 연결"""
    await ws.accept()
    connections[user_id] = ws
    print(f"Connected: {user_id}")
    try:
        while True:
            await ws.receive_text()  # keep-alive ping
    except Exception:
        pass
    finally:
        print(f"Disconnected: {user_id}")
        connections.pop(user_id, None)
