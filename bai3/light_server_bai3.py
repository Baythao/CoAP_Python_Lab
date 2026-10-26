import asyncio
import json
import os
from datetime import datetime

import aiocoap
from aiocoap import resource

COAP_HOST = os.environ.get("COAP_HOST", "127.0.0.1")
COAP_PORT = int(os.environ.get("COAP_PORT", "5683"))

# Tạo thư mục logs
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "device_log.txt")


def write_log(message):
    """Ghi nhật ký thay đổi trạng thái thiết bị ra file."""
    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp_str}] {message}\n"
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Lỗi khi ghi file log: {e}")


class IoTDeviceResource(resource.ObservableResource):
    def __init__(self, device_id):
        super().__init__()
        self.device_id = device_id
        self.status = "OFF"
        self.observer_count = 0

    def update_observation_count(self, newcount):
        if newcount > self.observer_count:
            print(f"[{self.device_id}] Đã nhận đăng ký Observe mới từ Client\n", flush=True)
        self.observer_count = newcount

    def make_response(self, code):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        payload = {
            "device_id": self.device_id,
            "status": self.status,
            "timestamp": current_time,
        }

        return aiocoap.Message(
            code=code,
            payload=json.dumps(payload, separators=(",", ":")).encode("utf-8"),
            content_format=50,
        )

    async def render_get(self, request):
        return self.make_response(aiocoap.CONTENT)

    async def render_put(self, request):
        if request.opt.content_format != 50:
            return aiocoap.Message(
                code=aiocoap.UNSUPPORTED_CONTENT_FORMAT,
                payload=b"Payload must use application/json",
                content_format=0,
            )

        try:
            data = json.loads(request.payload.decode("utf-8"))

            if not isinstance(data, dict):
                raise ValueError("Payload phải là một đối tượng JSON")

            if data.get("device_id") != self.device_id:
                raise ValueError(f"device_id phải là {self.device_id}")

            command = data.get("command")
            if command not in ("ON", "OFF"):
                raise ValueError("Lệnh (command) phải là ON hoặc OFF")

        except (ValueError, UnicodeDecodeError) as error:
            # Kiểm tra lệnh không hợp lệ, trả về mã BAD_REQUEST
            return aiocoap.Message(
                code=aiocoap.BAD_REQUEST,
                payload=str(error).encode("utf-8"),
                content_format=0,
            )

        print(f"[{self.device_id}] Đã nhận yêu cầu PUT | Lệnh: {command}")
        
        # Nhận diện cơ chế CON/NON từ Client
        msg_type = "CON (Confirmable)" if request.mtype == aiocoap.CON else "NON (Non-confirmable)"
        print(f"[{self.device_id}] Loại bản tin: {msg_type}\n", flush=True)

        if command != self.status:
            old_status = self.status
            self.status = command

            change_msg = f"Trạng thái {self.device_id} thay đổi: {old_status} -> {self.status}"
            print(change_msg)
            print(f"[{self.device_id}] Thông báo tới các observers: {self.status}\n", flush=True)

            write_log(change_msg)
            self.updated_state()

        return self.make_response(aiocoap.CHANGED)


async def main():
    site = resource.Site()

    # Khởi tạo mô phỏng nhiều thiết bị (Đã thay đổi thành light02, light03)
    devices = ["light01", "light02", "light03"]
    
    for dev_id in devices:
        uri_path = ["iot", "lab", dev_id, "status"]
        site.add_resource(uri_path, IoTDeviceResource(dev_id))
        print(f"Đã đăng ký tài nguyên: /iot/lab/{dev_id}/status")

    context = await aiocoap.Context.create_server_context(
        site,
        bind=(COAP_HOST, COAP_PORT),
        transports=["simplesocketserver"],
    )

    print("\nCoAP IoT Server đã khởi động thành công...\n", flush=True)

    try:
        await asyncio.get_running_loop().create_future()
    finally:
        await context.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nĐã dừng Server.")
    except (OSError, aiocoap.error.Error) as error:
        print(f"Lỗi Server: {error}")