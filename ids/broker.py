# Broker.py
from hbmqtt.broker import Broker
import asyncio

config = {
    'listeners': {
        'default': {
            'type': 'tcp',
            'bind': '0.0.0.0:1883'
        }
    },
    'auth': {
        'allow-anonymous': True
    }
}

async def start_broker():
    broker = Broker(config)
    await broker.start()

if __name__ == "__main__":
    try:
        asyncio.run(start_broker())
    except KeyboardInterrupt:
        print("Broker stopped")

