import asyncio
import json
import os
import random
from contextlib import suppress
from datetime import datetime

import aiocoap
from aiocoap import resource


COAP_HOST = os.environ.get("COAP_HOST", "127.0.0.1")
COAP_PORT = int(os.environ.get("COAP_PORT", "5683"))

SENSOR_IDS = ("sensor01", "sensor02", "sensor03")


class SensorResource(resource.Resource):
    def __init__(self, device_id="sensor01"):
        super().__init__()
        self.device_id = device_id
        self.update_data()

    def update_data(self):
        self.data = {
            "device_id": self.device_id,
            "temperature": round(random.uniform(20, 45), 1),
            "humidity": round(random.uniform(25, 85), 1),
            "timestamp": datetime.now().astimezone().isoformat(
                timespec="seconds"
            ),
        }

        print(
            "Dữ liệu mới:",
            json.dumps(self.data, ensure_ascii=False),
            flush=True,
        )

    async def update_loop(self):
        while True:
            await asyncio.sleep(3)
            self.update_data()

    async def render_get(self, request):
        return aiocoap.Message(
            code=aiocoap.CONTENT,
            payload=json.dumps(
                self.data,
                ensure_ascii=False,
            ).encode("utf-8"),
            content_format=50,  # application/json
        )


async def main():
    site = resource.Site()
    sensors = []

    for device_id in SENSOR_IDS:
        sensor = SensorResource(device_id)
        sensors.append(sensor)

        path = f"iot/lab/{device_id}/data"
        site.add_resource(path.split("/"), sensor)

    context = await aiocoap.Context.create_server_context(
        site,
        bind=(COAP_HOST, COAP_PORT),
        transports=["simplesocketserver"],
    )

    tasks = [
        asyncio.create_task(sensor.update_loop())
        for sensor in sensors
    ]

    print("\nSensor CoAP Server started.")

    for device_id in SENSOR_IDS:
        print(
            f"Resource: coap://{COAP_HOST}:{COAP_PORT}"
            f"/iot/lab/{device_id}/data"
        )

    print("\nCập nhật dữ liệu mỗi 3 giây. Ctrl+C để dừng.\n")

    try:
        await asyncio.get_running_loop().create_future()

    finally:
        for task in tasks:
            task.cancel()

        for task in tasks:
            with suppress(asyncio.CancelledError):
                await task

        await context.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print("\nĐã dừng Server.")

    except (OSError, aiocoap.error.Error) as error:
        print(f"Lỗi Server: {error}")