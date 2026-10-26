import asyncio
import os
from datetime import datetime

import aiocoap
from aiocoap import resource


COAP_HOST = os.environ.get("COAP_HOST", "127.0.0.1")
COAP_PORT = int(os.environ.get("COAP_PORT", "5683"))

URI_PATH = "iot/lab/message"


def on_message(body):
    message = body.decode("utf-8")

    print("POST request received:")
    print("Payload:", message)
    print("Time:", datetime.now().strftime("%H:%M:%S"))
    print(flush=True)

    return message


class MessageResource(resource.Resource):
    def __init__(self):
        super().__init__()

        # Khi chưa nhận POST, GET trả về lời chào này.
        self.message = "Xin chao tu CoAP Server"

    async def render_get(self, request):
        print(
            f"GET request received: /{URI_PATH}\n",
            flush=True,
        )

        # Trả về thông điệp POST gần nhất.
        return aiocoap.Message(
            code=aiocoap.CONTENT,
            payload=self.message.encode("utf-8"),
            content_format=0,
        )

    async def render_post(self, request):
        try:
            # Chỉ cập nhật sau khi giải mã UTF-8 thành công.
            self.message = on_message(request.payload)

        except UnicodeDecodeError:
            return aiocoap.Message(
                code=aiocoap.BAD_REQUEST,
                payload=b"Payload phai la UTF-8",
                content_format=0,
            )

        return aiocoap.Message(
            code=aiocoap.CHANGED,
            payload=b"Server da nhan thong diep",
            content_format=0,
        )


async def main():
    site = resource.Site()

    site.add_resource(
        URI_PATH.split("/"),
        MessageResource(),
    )

    # URI không được đăng ký sẽ tự nhận lỗi 4.04 Not Found.
    context = await aiocoap.Context.create_server_context(
        site,
        bind=(COAP_HOST, COAP_PORT),
        transports=["simplesocketserver"],
    )

    print(
        f"CoAP Server started on port {COAP_PORT}\n",
        flush=True,
    )

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
        print("Kiểm tra địa chỉ IP và cổng UDP.")