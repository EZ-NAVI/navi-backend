import aio_pika
import asyncio
import json
from fastapi import FastAPI, WebSocket
from contextlib import asynccontextmanager

connections = {}  # user_id → websocket


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작 / 종료 시 수행할 로직"""
    print("Relay server starting...")

    # RabbitMQ 연결
    connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq/")
    channel = await connection.channel()

    # 기본 exchange 선언
    exchange = await channel.declare_exchange(
        "navi.events", aio_pika.ExchangeType.TOPIC
    )

    for routing_key in ["report.created", "report.reviewed"]:
        # 큐 선언 및 바인딩
        queue = await channel.declare_queue(routing_key, durable=True)
        await queue.bind(exchange, routing_key)
        print(f"Subscribed to {routing_key}")

        async def handler(message):
            async with message.process():
                data = json.loads(message.body)
                print(f"Received from RabbitMQ ({routing_key}):", data)
                target_id = data.get("parentId") or data.get("childId")
                if target_id in connections:
                    await connections[target_id].send_json(data)
                    print(f"Sent to {target_id}: {data}")

        asyncio.create_task(queue.consume(handler))

    yield  # 앱 실행 유지

    print("🧹 Relay server shutting down...")
    await connection.close()


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
