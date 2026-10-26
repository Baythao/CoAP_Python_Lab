# Thực hành giao tiếp IoT bằng CoAP với Python

Tài liệu hướng dẫn chạy và mô tả kết quả của 3 bài thực hành sử dụng giao thức **CoAP** (`aiocoap`) trên Python.

## Mục lục

- [Giới thiệu](#giới-thiệu)
- [Danh sách tệp](#danh-sách-tệp)
- [Yêu cầu](#yêu-cầu)
- [Bài 1: Gửi và nhận thông điệp bằng CoAP](#bài-1-gửi-và-nhận-thông-điệp-bằng-coap)
- [Bài 2: Giám sát cảm biến nhiệt độ và độ ẩm](#bài-2-giám-sát-cảm-biến-nhiệt-độ-và-độ-ẩm)
- [Bài 3: Giám sát và điều khiển đèn thông minh bằng CoAP Observe](#bài-3-giám-sát-và-điều-khiển-đèn-thông-minh-bằng-coap-observe)
- [Lưu ý khi chạy](#lưu-ý-khi-chạy)

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

> Các lệnh bên dưới giả định bạn đang ở thư mục gốc của dự án. Nếu tên hoặc vị trí tệp trong thư mục thực tế khác, hãy điều chỉnh đường dẫn tương ứng.

## Yêu cầu

- Python 3.
- Thư viện `aiocoap`.
- Môi trường ảo Python `.venv` được tạo và cài đặt các thư viện cần thiết.

Nếu chưa cài thư viện trong môi trường ảo, có thể kích hoạt môi trường rồi cài `aiocoap`:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install aiocoap
```

## Bài 1: Gửi và nhận thông điệp bằng CoAP

### Cách chạy

Mở **hai terminal** tại thư mục dự án sau khi kích hoạt môi trường ảo.

**Terminal 1 — Server**

```powershell
python ".\consumer_bai1.py"
```

**Terminal 2 — Client**

```powershell
python ".\producer_bai1.py"
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

**Lưu ý:** Thông điệp được lưu trong RAM và mất khi Server khởi động lại. Khi Server không hoạt động, hệ điều hành có thể báo lỗi kết nối ngay; timeout xảy ra khi Client không nhận được phản hồi trong 8 giây.

## Bài 2: Giám sát cảm biến nhiệt độ và độ ẩm

### Cách chạy

Mở hai terminal tại thư mục dự án.

**Terminal 1 — Sensor Server**

```powershell
.\.venv\Scripts\python.exe ".\sensor_producer_bai2.py"
```

**Terminal 2 — Monitoring Client**

```powershell
.\.venv\Scripts\python.exe ".\monitor_consumer_bai2.py"
```

Client cho phép chọn cảm biến bằng cách nhập `sensor01`, `sensor02` hoặc `sensor03`. Nhấn Enter để chọn mặc định `sensor01`. Trong log minh chứng, Client giám sát `sensor03`.

Nhấn `Ctrl+C` để dừng chương trình. Muốn đổi cảm biến, chạy lại Client và chọn mã khác.

### Thông số giao tiếp

- **Giao thức:** CoAP qua UDP.
- **Địa chỉ IP:** `127.0.0.1`.
- **Cổng:** `5683`.
- **Phương thức truy vấn:** GET.
- **Định dạng dữ liệu:** JSON, Content-Format `50`.
- **Chu kỳ cập nhật dữ liệu:** 3 giây.

| Thiết bị | URI |
|---|---|
| `sensor01` | `coap://127.0.0.1:5683/iot/lab/sensor01/data` |
| `sensor02` | `coap://127.0.0.1:5683/iot/lab/sensor02/data` |
| `sensor03` | `coap://127.0.0.1:5683/iot/lab/sensor03/data` |

### Chức năng

- Mô phỏng ba cảm biến nhiệt độ và độ ẩm.
- Tự động cập nhật dữ liệu cảm biến mỗi 3 giây.
- Thêm `timestamp` vào JSON để ghi nhận thời điểm tạo mẫu.
- Cho phép Client chọn mã thiết bị cần giám sát.
- Client gửi GET định kỳ, phân tích và hiển thị dữ liệu.
- Cảnh báo khi nhiệt độ **> 35°C** hoặc độ ẩm **< 40%**.
- Ghi nối tiếp dữ liệu nhận được vào CSV trong thư mục `logs`.
- Đếm số lần GET và tính thời gian phản hồi trung bình.

### Ví dụ dữ liệu JSON

```json
{
  "device_id": "sensor03",
  "temperature": 30.7,
  "humidity": 68.9,
  "timestamp": "2026-10-26T09:23:59+07:00"
}
```

### Kết quả chạy thực tế

Trong đoạn log Client từ `09:23:59` đến `09:24:38` ngày `26/10/2026`:

| Chỉ số | Kết quả |
|---|---:|
| Thiết bị được giám sát | `sensor03` |
| Số lần thực hiện GET | 14 |
| Số phản hồi nhận được | 14 |
| Tỷ lệ nhận phản hồi trong đoạn log | 100% |
| Khoảng cách giữa các lần nhận dữ liệu | 3 giây |
| Thời gian phản hồi trung bình sau lần thứ 14 | 3.580 ms |
| Thời gian phản hồi nhỏ nhất | 2.150 ms |
| Thời gian phản hồi lớn nhất | 10.927 ms |
| Ghi CSV | Client thông báo lưu thành công ở cả 14 lượt |

Dữ liệu Client nhận được khớp với dữ liệu Server tạo tại cùng timestamp. Các trường hợp cảnh báo được ghi nhận:

| Nhiệt độ | Độ ẩm | Kết quả |
|---:|---:|---|
| 30.7°C | 68.9% | Bình thường |
| 20.5°C | 38.8% | Cảnh báo độ ẩm thấp |
| 35.4°C | 38.1% | Cảnh báo nhiệt độ cao và độ ẩm thấp |

> Lưu ý: phần mô tả log gốc có một câu ghi “Nhiệt độ 38.1°C” cho trường hợp cảnh báo nhiệt độ cao, trong khi log minh chứng ghi nhiệt độ `35.4°C` và độ ẩm `38.1%`. Bảng trên sử dụng các giá trị hiển thị trong log minh chứng.

## Bài 3: Giám sát và điều khiển đèn thông minh bằng CoAP Observe

### Cách chạy

Cần mở **ba cửa sổ Terminal độc lập**. Kích hoạt môi trường ảo `.venv`, sau đó khởi chạy theo đúng thứ tự.

**Bước 1 — Khởi động CoAP Server**

```bash
python bai3/alert_producer_bai3.py
```

**Bước 2 — Khởi động Client giám sát (Observe)**

```bash
python bai3/critical_consumer_bai3.py
```

Nhập mã thiết bị muốn theo dõi khi được yêu cầu.

**Bước 3 — Khởi động Client điều khiển (Controller)**

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

## Lưu ý khi chạy

1. Các bài đều sử dụng UDP cổng `5683`. **Dừng Server của bài khác trước khi chạy bài tiếp theo** để tránh xung đột cổng.
2. Bài 1 và Bài 2 sử dụng các tệp ở thư mục gốc theo danh sách tệp. Lệnh Bài 3 ở trên giả định các tệp nằm trong thư mục `bai3/`; hãy điều chỉnh nếu cấu trúc dự án thực tế khác.
3. Thư mục `logs` có thể được tạo hoặc cập nhật trong quá trình chạy, tùy cách triển khai của từng chương trình.
4. Các kết quả và số liệu trong README là log minh chứng của một lần chạy, không phải cam kết về thời gian phản hồi trong mọi môi trường.

---

**Công nghệ:** Python · CoAP · UDP · `aiocoap` · JSON · CSV · CoAP Observe
