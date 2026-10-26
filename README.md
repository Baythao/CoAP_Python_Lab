
## Thành viên nhóm

| Mã sinh viên | Họ và tên |
|---|---|
| B23DCCN365 | Hoàng Khải Hưng |
| B22DCCN072 | Thào A Bảy |
| B23DCCN055 | Trịnh Quang Anh |

---

# Thực hành giao tiếp IoT bằng CoAP với Python
Tài liệu hướng dẫn chạy và mô tả kết quả của 3 bài thực hành sử dụng giao thức **CoAP** (`aiocoap`) trên Python.



## Giới thiệu

Dự án mô phỏng một số chức năng IoT bằng giao thức CoAP qua UDP trên máy cục bộ (`127.0.0.1`), cổng `5683`, gồm:

1. Trao đổi thông điệp bằng các phương thức GET và POST.
2. Giám sát dữ liệu nhiệt độ, độ ẩm của nhiều cảm biến.
3. Điều khiển trạng thái đèn thông minh và nhận cập nhật tự động bằng CoAP Observe.

## Danh sách tệp

| Tệp | Vai trò |
|---|---|
| `consumer_bai1.py` | Bài 1 — CoAP Server GET/POST |
| `producer_bai1.py` | Bài 1 — CoAP Client GET rồi POST |
| `sensor_producer_bai2.py` | Bài 2 — Sensor CoAP Server |
| `monitor_consumer_bai2.py` | Bài 2 — Monitoring CoAP Client |
| `alert_producer_bai3.py` | Bài 3 — Smart Light CoAP Server |
| `warning_consumer_bai3.py` | Bài 3 — Light Controller Client |
| `critical_consumer_bai3.py` | Bài 3 — Light Monitoring Client (Observe) |
| `all_alert_consumer_bai3.py` | Mở rộng — một client Observe khác, có ghi log |


## Yêu cầu

- Python 3.
- Cài môi trường ảo Python `.venv` và kích hoạt môi trường ảo:
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
- Cài thư viện`aiocoap` trong môi trường ảo :
```bash
python -m pip install aiocoap
```

## Bài 1: Gửi và nhận thông điệp bằng CoAP

### Cách chạy

Mở **hai terminal** tại thư mục dự án sau khi kích hoạt môi trường ảo.
**Terminal 1 — Server**
```bash
python bai1/consumer_bai1.py
```
**Terminal 2 — Client**
```bash
python bai1/producer_bai1.py
```

### Cách hoạt động

Client gửi yêu cầu GET tới tài nguyên:

```text
coap://127.0.0.1:5683/iot/lab/message
```

Server trả về lời chào ban đầu. Sau đó, người dùng nhập nội dung; Client tự thêm mã sinh viên và họ tên rồi gửi POST. Server hiển thị nội dung nhận được cùng thời điểm nhận, đồng thời lưu thông điệp POST gần nhất để trả về cho yêu cầu GET tiếp theo.

Các lệnh tại Client:

| Lệnh | Chức năng |
|---|---|
| Nhập nội dung bất kỳ | Gửi thông điệp POST; có thể gửi nhiều lần liên tiếp |
| `/get` | Lấy thông điệp POST gần nhất |
| `/missing` | Thử truy cập tài nguyên không tồn tại |
| `/exit` hoặc nhấn Enter khi để trống | Kết thúc Client |

### Kết quả minh chứng

**Phản hồi GET ban đầu:**

```text
Code: 2.05 Content
Payload: Xin chao tu CoAP Server
```

**Phản hồi POST:**

```text
Payload: Xin chào từ CoAP Clieant - B22DCCN072 - Thào A Bảy
Code: 2.04 Changed
Payload: Server da nhan thong diep
```

Nội dung log trên được giữ theo lần chạy thực tế, bao gồm cả cách viết `Clieant` do người dùng nhập.

### Kết quả đạt được

- Xây dựng CoAP Server và Client bằng Python với thư viện `aiocoap`.
- Giao tiếp qua UDP cổng `5683`.
- GET nhận lời chào với mã phản hồi `2.05 Content`.
- POST gửi nội dung, mã sinh viên và họ tên; nhận xác nhận `2.04 Changed`.
- Server hiển thị nội dung và thời điểm nhận.
- Client tiếp tục chờ nhập thông điệp mới sau khi gửi thành công.

### Chức năng mở rộng

- Gửi nhiều thông điệp POST liên tiếp.
- Lưu thông điệp POST gần nhất và trả về khi Client nhập `/get`.
- Trả về lỗi `4.04 Not Found` khi Client nhập `/missing`.
- Xử lý lỗi kết nối hoặc timeout sau 8 giây không nhận phản hồi.
- Cho phép Client tiếp tục gửi yêu cầu sau khi gặp lỗi giao tiếp.


## Bài 2: Giám sát cảm biến nhiệt độ và độ ẩm

### Cách chạy

Mở hai terminal tại thư mục dự án.

**Terminal 1 — Sensor Server**
```bash
python bai2/sensor_producer_bai2.py
```

**Terminal 2 — Monitoring Client**
```bash
python bai3/monitor_consumer_bai2.py
```

Client yêu cầu chọn thiết bị:

```text
Các cảm biến: sensor01, sensor02, sensor03
Nhập mã thiết bị cần giám sát [Enter = sensor01]: sensor03
```

Nhập mã cảm biến cần giám sát; Enter chọn mặc định `sensor01`. Nhập sai sẽ được yêu cầu nhập lại. Muốn đổi thiết bị, nhấn `Ctrl+C`, chạy lại Client và chọn mã khác.

### 2. IP, cổng và URI

- IP: `127.0.0.1`.
- Cổng: UDP `5683`.
- Phương thức: GET.
- Dữ liệu: JSON, Content-Format `50`.

| Thiết bị | URI |
| --- | --- |
| sensor01 | `coap://127.0.0.1:5683/iot/lab/sensor01/data` |
| sensor02 | `coap://127.0.0.1:5683/iot/lab/sensor02/data` |
| sensor03 | `coap://127.0.0.1:5683/iot/lab/sensor03/data` |

### 3. Chức năng và kết quả đạt được

- Mô phỏng ba cảm biến, cập nhật dữ liệu mỗi 3 giây.
- Bổ sung `timestamp` trong JSON.
- Cho phép Client chọn thiết bị và GET dữ liệu định kỳ.
- Cảnh báo khi nhiệt độ >35°C hoặc độ ẩm <40%.
- Ghi nối tiếp dữ liệu vào `logs/<mã thiết bị>.csv`.
- Đếm số GET và tính thời gian phản hồi trung bình.
- Xử lý lỗi giao tiếp và timeout sau 8 giây.

### 4. Log minh chứng

**Server:**

```text
Sensor CoAP Server started.
Resource: coap://127.0.0.1:5683/iot/lab/sensor01/data
Resource: coap://127.0.0.1:5683/iot/lab/sensor02/data
Resource: coap://127.0.0.1:5683/iot/lab/sensor03/data

Cập nhật dữ liệu mỗi 3 giây. Ctrl+C để dừng.
```

**Client — trích log thực tế:**

```text
[09:24:23] Received sensor data

Device: sensor03
Temperature: 35.4 C
Humidity: 38.1 %
Timestamp: 2026-10-26T09:24:23+07:00

CANH BAO: Nhiet do cao
CANH BAO: Do am thap

Thời gian phản hồi: 2.173 ms
Đã lưu dữ liệu vào CSV.

Số lần thực hiện GET: 9
Số lần nhận phản hồi: 9
Thời gian phản hồi trung bình: 2.957 ms
----------------------------------------
```


## Bài 3: Giám sát và điều khiển đèn thông minh bằng CoAP Observe

### Cách chạy

Cần mở **ba cửa sổ Terminal độc lập**. Kích hoạt môi trường ảo `.venv`, sau đó khởi chạy theo đúng thứ tự.

**Terminal 1 — Khởi động CoAP Server**
```bash
python bai3/alert_producer_bai3.py
```

**Terminal 2 — Khởi động Client giám sát (Observe)**
```bash
python bai3/critical_consumer_bai3.py
```
Nhập mã thiết bị muốn theo dõi khi được yêu cầu.

**Terminal 3 — Khởi động Client điều khiển (Controller)**
```bash
python bai3/warning_consumer_bai3.py
```
Nhập mã thiết bị muốn điều khiển khi được yêu cầu.

### Thông số và URI

- **Địa chỉ IP Server:** `127.0.0.1` (localhost).
- **Cổng giao tiếp:** `5683`.

| Thiết bị | URI |
|---|---|
| `light01` | `coap://127.0.0.1:5683/iot/lab/light01/status` |
| `light02` | `coap://127.0.0.1:5683/iot/lab/light02/status` |
| `light03` | `coap://127.0.0.1:5683/iot/lab/light03/status` |

### Chức năng đã thực hiện

- **Server đa thiết bị:** quản lý trạng thái của `light01`, `light02`, `light03` bằng `ObservableResource`.
- **CoAP Observe:** Monitor Client đăng ký Observe và nhận sự kiện tự động khi trạng thái đèn thay đổi.
- **Điều khiển GET/PUT:** Controller Client gửi các lệnh `ON`, `OFF`, `STATUS`.
- Bổ sung trường `timestamp` vào payload.
- Hỗ trợ chọn loại bản tin CoAP: Confirmable (`CON`) hoặc Non-confirmable (`NON`).
- Ghi lịch sử thay đổi trạng thái vào `logs/device_log.txt`.
- Cho phép người dùng chọn mã thiết bị khi chạy Client.

### Kết quả minh chứng

Server ghi nhận đăng ký Observe và yêu cầu PUT:

```text
Đã đăng ký tài nguyên: /iot/lab/light01/status
Đã đăng ký tài nguyên: /iot/lab/light02/status
Đã đăng ký tài nguyên: /iot/lab/light03/status

CoAP IoT Server đã khởi động thành công...

[light02] Đã nhận đăng ký Observe mới từ Client
[light02] Đã nhận yêu cầu PUT | Lệnh: ON
[light02] Loại bản tin: CON (Confirmable)

Trạng thái light02 thay đổi: OFF -> ON
[light02] Thông báo tới các observers: ON
```

Monitor Client nhận được trạng thái ban đầu và cập nhật:

```text
Đăng ký Observe thành công

Trạng thái ban đầu
Thiết bị: light02
Trạng thái: OFF
Thời gian từ Server: 2026-10-26 10:30:15

Trạng thái đã cập nhật
Thiết bị: light02
Trạng thái: ON
Thời gian từ Server: 2026-10-26 10:30:25
```

Controller Client gửi lệnh bật đèn:

```text
[light02] Nhập lệnh (ON/OFF/STATUS/EXIT): on
Chọn loại bản tin (1: CON, 2: NON) [Mặc định 1]: 1

Đang gửi yêu cầu PUT (CON)...
Mã phản hồi: 2.04 Changed | Cập nhật thành công light02
```

### Kết quả đạt được

Hệ thống mô phỏng được việc quản lý nhiều đèn, điều khiển trạng thái qua PUT và tự động thông báo cho Client đã đăng ký Observe khi trạng thái thay đổi.

---

**Công nghệ:** Python · CoAP · UDP · `aiocoap` · JSON · CSV · CoAP Observe
