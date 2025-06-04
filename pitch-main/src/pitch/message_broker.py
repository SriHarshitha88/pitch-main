import aio_pika
import json
from typing import Any, Callable, Dict
import os
import asyncio
from functools import wraps

# Get RabbitMQ URL from environment variable
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost/")

class MessageBroker:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.exchange = None
        self.queues = {}
        self.handlers = {}

    async def connect(self):
        """Connect to RabbitMQ"""
        self.connection = await aio_pika.connect_robust(RABBITMQ_URL)
        self.channel = await self.connection.channel()
        self.exchange = await self.channel.declare_exchange(
            "pitch_analyzer",
            aio_pika.ExchangeType.TOPIC
        )

    async def declare_queue(self, queue_name: str):
        """Declare a queue"""
        if queue_name not in self.queues:
            queue = await self.channel.declare_queue(queue_name)
            self.queues[queue_name] = queue
        return self.queues[queue_name]

    async def publish(self, queue_name: str, message: Dict[str, Any]):
        """Publish a message to a queue"""
        queue = await self.declare_queue(queue_name)
        await self.exchange.publish(
            aio_pika.Message(
                body=json.dumps(message).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            ),
            routing_key=queue_name
        )

    async def consume(self, queue_name: str, handler: Callable):
        """Consume messages from a queue"""
        queue = await self.declare_queue(queue_name)
        self.handlers[queue_name] = handler

        async def process_message(message: aio_pika.IncomingMessage):
            async with message.process():
                try:
                    body = json.loads(message.body.decode())
                    await handler(body)
                except Exception as e:
                    print(f"Error processing message: {e}")

        await queue.consume(process_message)

    async def close(self):
        """Close the connection"""
        if self.connection:
            await self.connection.close()

# Create message broker instance
message_broker = MessageBroker()

# Decorator for async message handlers
def message_handler(queue_name: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            await message_broker.consume(queue_name, func)
        return wrapper
    return decorator 