import aio_pika
import asyncio
import json
from fastapi import FastAPI, WebSocket

app = FastAPI(title="NAVI Relay Server")

connections = {}  # user_id → websocket


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


@app.on_event("startup")
async def startup_event():
    """RabbitMQ에서 메시지를 받아 WebSocket으로 중계"""
    connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq/")
    channel = await connection.channel()

    for routing_key in ["report.created", "report.reviewed"]:
        queue = await channel.declare_queue(routing_key, durable=True)

        async def handler(message):
            async with message.process():
                data = json.loads(message.body)
                target_id = data.get("parentId") or data.get("childId")
                if target_id in connections:
                    await connections[target_id].send_json(data)
                    print(f"Sent to {target_id}: {data}")

        asyncio.create_task(queue.consume(handler))
