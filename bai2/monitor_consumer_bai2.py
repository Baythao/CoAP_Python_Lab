import asyncio
import csv
import json
import math
import os
from datetime import datetime
from pathlib import Path

import aiocoap


COAP_HOST = os.environ.get("COAP_HOST", "127.0.0.1")
COAP_PORT = int(os.environ.get("COAP_PORT", "5683"))

SENSOR_IDS = ("sensor01", "sensor02", "sensor03")
LOG_DIR = Path(__file__).resolve().parent / "logs"


def choose_device():
    print("Các cảm biến: sensor01, sensor02, sensor03")

    while True:
        device_id = input(
            "Nhập mã thiết bị cần giám sát [Enter = sensor01]: "
        ).strip().lower()

        if not device_id:
            device_id = "sensor01"

        if device_id in SENSOR_IDS:
            return device_id

        print("Mã thiết bị không hợp lệ. Vui lòng nhập lại.\n")


def handle_message(body, expected_device):
    data = json.loads(body.decode("utf-8"))

    if not isinstance(data, dict):
        raise ValueError("Dữ liệu JSON phải là một đối tượng")

    if data.get("device_id") != expected_device:
        raise ValueError("Dữ liệu không thuộc thiết bị đang giám sát")

    temperature = float(data["temperature"])
    humidity = float(data["humidity"])
    timestamp = data["timestamp"]

    if not math.isfinite(temperature) or not math.isfinite(humidity):
        raise ValueError("Giá trị cảm biến không hợp lệ")

    datetime.fromisoformat(timestamp)

    print(f"\n[{datetime.now():%H:%M:%S}] Received sensor data\n")
    print("Device:", data["device_id"])
    print(f"Temperature: {temperature:.1f} C")
    print(f"Humidity: {humidity:.1f} %")
    print("Timestamp:", timestamp)
    print()

    # Giữ nguyên các điều kiện cảnh báo.
    if temperature > 35:
        print("CANH BAO: Nhiet do cao")

    if humidity < 40:
        print("CANH BAO: Do am thap")

    if temperature <= 35 and humidity >= 40:
        print("Trang thai: Binh thuong")

    return data


def save_csv(file_path, data, received_at, response_ms):
    file_path.parent.mkdir(parents=True, exist_ok=True)

    write_header = (
        not file_path.exists()
        or file_path.stat().st_size == 0
    )

    # Ghi nối tiếp và giữ dữ liệu của những lần chạy trước.
    with file_path.open(
        "a",
        newline="",
        encoding="utf-8-sig",
    ) as file:
        writer = csv.writer(file)

        if write_header:
            writer.writerow([
                "device_id",
                "temperature",
                "humidity",
                "timestamp",
                "received_at",
                "response_ms",
            ])

        writer.writerow([
            data["device_id"],
            data["temperature"],
            data["humidity"],
            data["timestamp"],
            received_at,
            round(response_ms, 3),
        ])


def print_statistics(get_count, response_count, total_response_ms):
    print(f"\nSố lần thực hiện GET: {get_count}")
    print(f"Số lần nhận phản hồi: {response_count}")

    if response_count:
        average_ms = total_response_ms / response_count
        print(f"Thời gian phản hồi trung bình: {average_ms:.3f} ms")
    else:
        print("Thời gian phản hồi trung bình: Chưa có phản hồi")

    print("-" * 40, flush=True)


async def main(device_id):
    uri = (
        f"coap://{COAP_HOST}:{COAP_PORT}"
        f"/iot/lab/{device_id}/data"
    )

    csv_file = LOG_DIR / f"{device_id}.csv"

    get_count = 0
    response_count = 0
    total_response_ms = 0.0

    context = await aiocoap.Context.create_client_context(
        transports=["simple6"]
    )

    print("\nĐang giám sát:", uri)
    print("File lưu dữ liệu:", csv_file)
    print("GET mỗi 3 giây. Nhấn Ctrl+C để dừng.")

    try:
        while True:
            start = asyncio.get_running_loop().time()
            get_count += 1

            try:
                response = await asyncio.wait_for(
                    context.request(
                        aiocoap.Message(
                            code=aiocoap.GET,
                            uri=uri,
                        )
                    ).response,
                    timeout=8,
                )

                # Đo trước khi phân tích, hiển thị và ghi dữ liệu.
                response_ms = (
                    asyncio.get_running_loop().time() - start
                ) * 1000

                response_count += 1
                total_response_ms += response_ms

                received_at = (
                    datetime.now()
                    .astimezone()
                    .isoformat(timespec="seconds")
                )

                if not response.code.is_successful():
                    print("\nServer trả lỗi:", response.code)

                elif response.opt.content_format != 50:
                    print("\nPhản hồi không phải application/json.")

                else:
                    data = handle_message(
                        response.payload,
                        device_id,
                    )

                    print(
                        f"\nThời gian phản hồi: {response_ms:.3f} ms"
                    )

                    try:
                        save_csv(
                            csv_file,
                            data,
                            received_at,
                            response_ms,
                        )
                        print("Đã lưu dữ liệu vào CSV.")

                    except OSError as error:
                        print(f"Không ghi được CSV: {error}")

            except asyncio.TimeoutError:
                print("\nTimeout: Server không phản hồi sau 8 giây.")

            except (
                ValueError,
                KeyError,
                TypeError,
                UnicodeDecodeError,
            ) as error:
                print(f"\nDữ liệu không hợp lệ: {error}")

            except (aiocoap.error.Error, OSError) as error:
                print(f"\nLỗi giao tiếp CoAP: {error}")

            print_statistics(
                get_count,
                response_count,
                total_response_ms,
            )

            # Khoảng cách giữa các lần GET là 3 giây
            # khi Server phản hồi đúng hạn.
            elapsed = asyncio.get_running_loop().time() - start
            await asyncio.sleep(max(0, 3 - elapsed))

    finally:
        print("\nTHỐNG KÊ KẾT THÚC")
        print_statistics(
            get_count,
            response_count,
            total_response_ms,
        )
        await context.shutdown()


if __name__ == "__main__":
    try:
        selected_device = choose_device()
        asyncio.run(main(selected_device))

    except (KeyboardInterrupt, EOFError):
        print("\nĐã dừng Client.")

    except (OSError, aiocoap.error.Error) as error:
        print(f"Lỗi Client: {error}")