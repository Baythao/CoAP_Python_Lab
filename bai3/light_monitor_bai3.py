import asyncio
import json
import os
from datetime import datetime

import aiocoap

COAP_HOST = os.environ.get("COAP_HOST", "127.0.0.1")
COAP_PORT = int(os.environ.get("COAP_PORT", "5683"))
TIMEOUT_SECONDS = 8

def handle_message(response, target_device_id, initial=False):
    if not response.code.is_successful():
        raise ValueError(f"Server trả lỗi {response.code}: {response.payload.decode('utf-8', errors='replace')}")

    if response.opt.content_format != 50:
        raise ValueError("Phản hồi không phải định dạng application/json")

    data = json.loads(response.payload.decode("utf-8"))

    if data.get("device_id") != target_device_id:
        raise ValueError(f"Mã thiết bị không khớp. Mong đợi: {target_device_id}")

    label = "Trạng thái ban đầu" if initial else "Trạng thái đã cập nhật"

    print(f"[{datetime.now():%H:%M:%S}] {label}")
    print("Thiết bị:", data["device_id"])
    print("Trạng thái:", data["status"])
    if "timestamp" in data:
        print("Thời gian từ Server:", data["timestamp"])
    print("-" * 30, flush=True)

async def main():
    print("=== CHỌN THIẾT BỊ GIÁM SÁT (OBSERVE) ===")
    # Đã cập nhật danh sách hiển thị
    print("Các thiết bị mô phỏng: light01, light02, light03")
    device_input = await asyncio.to_thread(
        input, "Nhập mã thiết bị muốn theo dõi (mặc định light01): "
    )
    device_id = device_input.strip() or "light01"
    uri = f"coap://{COAP_HOST}:{COAP_PORT}/iot/lab/{device_id}/status"
    
    print(f"Đang giám sát thiết bị: [{device_id}] tại URI: {uri}\n")

    context = await aiocoap.Context.create_client_context(transports=["simple6"])
    request = None

    try:
        print("Đang đăng ký CoAP Observe...", flush=True)
        request = context.request(aiocoap.Message(code=aiocoap.GET, uri=uri, observe=0))
        
        response = await asyncio.wait_for(request.response, timeout=TIMEOUT_SECONDS)

        if not response.code.is_successful():
            print("Mã phản hồi:", response.code)
            return

        if response.opt.observe is None:
            print("Server không chấp nhận đăng ký Observe.")
            return

        print("Đăng ký Observe thành công\n", flush=True)
        handle_message(response, device_id, initial=True)

        async for notification in request.observation:
            handle_message(notification, device_id)

    except asyncio.TimeoutError:
        print(f"Timeout: Server không phản hồi đăng ký Observe sau {TIMEOUT_SECONDS} giây.")
    except Exception as error:
        print(f"Lỗi: {error}")
    finally:
        if request is not None and not request.observation.cancelled:
            request.observation.cancel()
        await context.shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nĐã dừng Client giám sát.")