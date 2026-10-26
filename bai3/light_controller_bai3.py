import asyncio
import json
import os
import aiocoap

COAP_HOST = os.environ.get("COAP_HOST", "127.0.0.1")
COAP_PORT = int(os.environ.get("COAP_PORT", "5683"))
TIMEOUT_SECONDS = 8

async def send(context, message):
    try:
        return await asyncio.wait_for(
            context.request(message).response,
            timeout=TIMEOUT_SECONDS,
        )
    except asyncio.TimeoutError:
        print(f"Timeout: Server không phản hồi sau {TIMEOUT_SECONDS} giây.\n")
    except (aiocoap.error.Error, OSError) as error:
        print(f"Lỗi giao tiếp CoAP: {error}\n")
    return None

async def main():
    print("=== CHỌN THIẾT BỊ ĐIỀU KHIỂN ===")
    # Đã cập nhật danh sách hiển thị
    print("Các thiết bị mô phỏng: light01, light02, light03")
    device_input = await asyncio.to_thread(
        input, "Nhập mã thiết bị muốn điều khiển (mặc định light01): "
    )
    device_id = device_input.strip() or "light01"
    uri = f"coap://{COAP_HOST}:{COAP_PORT}/iot/lab/{device_id}/status"
    
    print(f"Đã kết nối tới thiết bị: [{device_id}] tại {uri}\n")

    context = await aiocoap.Context.create_client_context(transports=["simple6"])

    try:
        while True:
            try:
                command = await asyncio.to_thread(input, f"[{device_id}] Nhập lệnh (ON/OFF/STATUS/EXIT): ")
            except EOFError:
                break

            command = command.strip().upper()
            if command == "EXIT":
                break
            if command not in ("ON", "OFF", "STATUS"):
                print("Lệnh không hợp lệ.\n")
                continue

            # Lựa chọn cơ chế CON hoặc NON
            mtype = aiocoap.CON
            if command in ("ON", "OFF"):
                try:
                    type_input = await asyncio.to_thread(input, "Chọn loại bản tin (1: CON, 2: NON) [Mặc định 1]: ")
                    if type_input.strip() == "2":
                        mtype = aiocoap.NON
                except EOFError:
                    pass

            if command == "STATUS":
                print("\nĐang gửi yêu cầu GET (CON)...")
                message = aiocoap.Message(code=aiocoap.GET, uri=uri)
            else:
                msg_type_str = "NON" if mtype == aiocoap.NON else "CON"
                print(f"\nĐang gửi yêu cầu PUT ({msg_type_str})...")
                payload = {"device_id": device_id, "command": command}
                message = aiocoap.Message(
                    code=aiocoap.PUT,
                    uri=uri,
                    payload=json.dumps(payload).encode("utf-8"),
                    content_format=50,
                    mtype=mtype
                )

            response = await send(context, message)

            if response is None:
                continue

            if not response.code.is_successful():
                print("Mã phản hồi:", response.code)
                print("Payload:", response.payload.decode("utf-8", errors="replace"))
                print()
                continue

            if command == "STATUS":
                print("Phản hồi:")
                print(response.payload.decode("utf-8", errors="replace"))
            else:
                print(f"Mã phản hồi: {response.code} | Cập nhật thành công {device_id}")
            print(flush=True)
    finally:
        await context.shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nĐã dừng Client điều khiển.")