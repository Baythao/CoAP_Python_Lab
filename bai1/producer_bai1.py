import asyncio
import os

import aiocoap


COAP_HOST = os.environ.get("COAP_HOST", "127.0.0.1")
COAP_PORT = int(os.environ.get("COAP_PORT", "5683"))

STUDENT_ID = "B22DCCN072"
STUDENT_NAME = "Thào A Bảy"

URI = f"coap://{COAP_HOST}:{COAP_PORT}/iot/lab/message"

# Tài nguyên cố tình không tồn tại để kiểm tra lỗi 4.04.
INVALID_URI = (
    f"coap://{COAP_HOST}:{COAP_PORT}/iot/lab/not-found"
)

TIMEOUT_SECONDS = 8


async def send(context, message):
    try:
        response = await asyncio.wait_for(
            context.request(message).response,
            timeout=TIMEOUT_SECONDS,
        )

        print("\nResponse:")
        print("Code:", response.code)
        print(
            "Payload:",
            response.payload.decode("utf-8", errors="replace"),
        )

        if response.code == aiocoap.NOT_FOUND:
            print("Lỗi: Tài nguyên không tồn tại.")

        elif not response.code.is_successful():
            print("Lỗi: Server không xử lý thành công yêu cầu.")

        print(flush=True)
        return response

    except asyncio.TimeoutError:
        print("\nTimeout:")
        print(
            f"Không nhận được phản hồi sau "
            f"{TIMEOUT_SECONDS} giây."
        )
        print("Kiểm tra Server, địa chỉ IP và cổng UDP.")
        print("Bạn có thể nhập lệnh để thử lại.\n", flush=True)

    except (aiocoap.error.Error, OSError) as error:
        print("\nLỗi giao tiếp CoAP:")
        print(error)
        print("Server có thể chưa chạy hoặc không truy cập được.")
        print("Bạn có thể nhập lệnh để thử lại.\n", flush=True)

    return None


async def main():
    context = await aiocoap.Context.create_client_context(
        transports=["simple6"]
    )

    try:
        print("CoAP Client")
        print("Sending GET request...")
        print("URI:", URI)

        # GET ban đầu. Nếu Server chưa chạy, báo lỗi
        # nhưng vẫn tiếp tục cho người dùng nhập yêu cầu.
        await send(
            context,
            aiocoap.Message(
                code=aiocoap.GET,
                uri=URI,
            ),
        )

        print("Nhập nội dung lời chào để gửi POST.")
        print("Có thể gửi nhiều thông điệp liên tiếp.")
        print()
        print("/get     : Lấy thông điệp POST gần nhất.")
        print("/missing : Truy cập tài nguyên không tồn tại.")
        print("/exit    : Thoát chương trình.")
        print("Enter rỗng cũng kết thúc chương trình.\n")

        while True:
            try:
                greeting = await asyncio.to_thread(
                    input,
                    "Nhập nội dung hoặc lệnh: ",
                )
            except EOFError:
                break

            greeting = greeting.strip()

            if not greeting or greeting.lower() == "/exit":
                break

            if greeting.lower() == "/get":
                print("\nSending GET request...")
                print("URI:", URI)

                await send(
                    context,
                    aiocoap.Message(
                        code=aiocoap.GET,
                        uri=URI,
                    ),
                )

            elif greeting.lower() == "/missing":
                print("\nSending GET request...")
                print("URI:", INVALID_URI)

                await send(
                    context,
                    aiocoap.Message(
                        code=aiocoap.GET,
                        uri=INVALID_URI,
                    ),
                )

            elif greeting.startswith("/"):
                print(
                    "Lệnh không hợp lệ. "
                    "Dùng /get, /missing hoặc /exit.\n"
                )

            else:
                message = (
                    f"{greeting} - {STUDENT_ID} - {STUDENT_NAME}"
                )

                print("\nSending POST request...")
                print("Payload:", message)

                await send(
                    context,
                    aiocoap.Message(
                        code=aiocoap.POST,
                        uri=URI,
                        payload=message.encode("utf-8"),
                        content_format=0,
                    ),
                )

    finally:
        await context.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print("\nĐã dừng Client.")

    except (OSError, aiocoap.error.Error) as error:
        print(f"Lỗi khởi tạo Client: {error}")