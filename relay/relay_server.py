import aio_pika
import asyncio
import json
from fastapi import FastAPI, WebSocket

connections = {}  # user_id → websocket
app = FastAPI(title="NAVI Relay Server")


@app.on_event("startup")
async def startup_event():
    print("⚡ Relay server startup_event fired!", flush=True)

    for attempt in range(10):
        try:
            connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq/")
            print("Connected to RabbitMQ", flush=True)
            break
        except Exception as e:
            print(
                f"RabbitMQ connect failed (attempt {attempt + 1}/10): {e}",
                flush=True,
            )
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
        print(f"Bound to {routing_key}", flush=True)

        async def handler(message):
            async with message.process():
                data = json.loads(message.body)
                print(f"Received ({routing_key}): {data}", flush=True)
                target_id = data.get("parentId") or data.get("childId")
                if target_id in connections:
                    await connections[target_id].send_json(data)
                    print(f"Sent to {target_id}", flush=True)

        asyncio.create_task(queue.consume(handler))

    for rk in ["report.created", "report.reviewed"]:
        asyncio.create_task(setup_queue(rk))


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(ws: WebSocket, user_id: str):
    await ws.accept()
    connections[user_id] = ws
    print(f"🔗 Connected: {user_id}", flush=True)
    try:
        while True:
            await ws.receive_text()
    except Exception:
        pass
    finally:
        print(f"Disconnected: {user_id}", flush=True)
        connections.pop(user_id, None)
