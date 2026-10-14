### Họ và Tên: Phạm Gia Huy_2387700022

## BÀI 4: BẢO MẬT WEB APP VÀ API
### BÁO CÁO THỰC HÀNH: BỘ CÔNG CỤ QUÉT LỖ HỔNG WEB (WEBVULNSCANNER) & BẢO MẬT TOKEN (JWTSECURE)

---

## 1. Giới thiệu tổng quan

Bài thực hành số 4 trang bị kiến thức chuyên sâu và kỹ năng thực hành về kiểm thử an toàn ứng dụng web (Web Application Security) và bảo mật giao diện lập trình ứng dụng (API Security), bao gồm hai hợp phần trọng tâm:

1. **WebVulnScanner (`Buoi4/web-vuln-scanner`):** Xây dựng bộ công cụ quét và phát hiện các lỗ hổng web phổ biến thuộc Top 10 OWASP:
   - **XSSScanner:** Tự động phát hiện lỗ hổng Cross-Site Scripting (Reflected XSS) thông qua thư viện payload chuẩn hóa (`<script>alert(1)</script>`, `"><svg/onload=alert(1)>`).
   - **SQLInjectionTester:** Kiểm thử và phát hiện các mẫu tấn công SQL Injection phổ biến (`' OR '1'='1`, `'; DROP TABLE users;--`, `" OR 1=1--`, `' UNION SELECT NULL--`) trong tham số URL.
   - **CSRFDetector:** Phân tích mã HTML để phát hiện sự hiện diện của CSRF token nhằm đánh giá khả năng phòng vệ trước tấn công giả mạo yêu cầu người dùng (Cross-Site Request Forgery).
   - **SSRFTester:** Phát hiện các endpoint có nguy cơ bị tấn công Server-Side Request Forgery thông qua nhận diện địa chỉ IP nội bộ (`127.0.0.1`, `localhost`, các dải mạng riêng tư `10.x.x.x`, `192.168.x.x`, `172.16-31.x.x`).
   - **ReportGenerator & Web UI:** Tập hợp các phát hiện thành báo cáo lỗ hổng có phân loại mức độ rủi ro (Critical, High, Medium, Low) và hiển thị trực quan thông qua giao diện Web Flask.

2. **JWTSecure (`Buoi4/jwt-security-tools`):** Xây dựng và kiểm thử bộ công cụ bảo mật Token JWT & OAuth 2.0:
   - **JWTValidator:** Kiểm tra toàn diện tính hợp lệ của chữ ký số (HMAC SHA-256), hạn sử dụng (`exp`) và cấu trúc của JWT token.
   - **JWTCracker:** Mô phỏng kỹ thuật tấn công dò quét khóa bí mật (Dictionary / Brute-force attack) sử dụng cơ chế xử lý đa luồng (`ThreadPoolExecutor`).
   - **OAuthClient:** Xây dựng OAuth 2.0 Client chuẩn hóa cho luồng Authorization Code Flow (`get_auth_url`, `get_token`).
   - **TokenManager:** Quản lý toàn bộ vòng đời Token bao gồm phát hành cặp Access Token (hạn ngắn) / Refresh Token (hạn dài) và làm mới Access Token an toàn.
   - **APIGateway:** Xây dựng cổng API Gateway với Flask Middleware bảo vệ các tài nguyên nhạy cảm (`/protected`) dựa trên xác thực JWT Bearer Token trong HTTP Header.
   - **GitSecure Pre-commit Protection:** Kiểm soát và ngăn chặn việc vô tình đưa khóa bí mật (Hardcoded Secrets) lên hệ thống quản lý phiên bản Git.

---

## 2. Cấu trúc thư mục Buổi 4

```text
Buoi4/
├── web-vuln-scanner/
│   ├── report/
│   │   ├── __init__.py
│   │   └── report_generator.py
│   ├── scanners/
│   │   ├── __init__.py
│   │   ├── csrf_detector.py
│   │   ├── sql_injection_tester.py
│   │   ├── ssrf_tester.py
│   │   └── xss_scanner.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_csrf.py
│   │   ├── test_report.py
│   │   ├── test_sql_injection.py
│   │   ├── test_ssrf.py
│   │   └── test_xss.py
│   ├── ui/
│   │   ├── templates/
│   │   │   ├── index.html
│   │   │   └── result.html
│   │   └── app.py
│   ├── __init__.py
│   ├── main.py
│   └── requirements.txt
├── jwt-security-tools/
│   ├── api_gateway/
│   │   ├── __init__.py
│   │   └── gateway.py
│   ├── jwt_cracker/
│   │   ├── __init__.py
│   │   └── cracker.py
│   ├── jwt_validator/
│   │   ├── __init__.py
│   │   └── validator.py
│   ├── oauth_client/
│   │   ├── __init__.py
│   │   └── client.py
│   ├── token_manager/
│   │   ├── __init__.py
│   │   └── manager.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_api_gateway.py
│   │   ├── test_cracker.py
│   │   ├── test_oauth_client.py
│   │   ├── test_token_manager.py
│   │   └── test_validator.py
│   ├── main.py
│   ├── pytest.ini
│   └── requirements.txt
├── ảnh/
└── README.md
```

---

## 3. Bảng tổng hợp công nghệ & Cơ chế an toàn

| Hợp phần | Thành phần kỹ thuật | Tiêu chuẩn / Kỹ thuật | Thư viện & Công cụ | Đặc tính bảo mật cốt lõi |
|---|---|---|---|---|
| **WebVulnScanner** | XSS Scanner | Reflected XSS Detection | `requests`, `unittest.mock` | Gửi payload kiểm thử phản hồi mã script động trên HTTP GET query. |
| **WebVulnScanner** | SQLi Tester | Pattern & Signature Matching | `urllib.parse` | Trích xuất các query parameters và nhận diện payload phá vỡ cú pháp SQL. |
| **WebVulnScanner** | CSRF Detector | Anti-CSRF Token Validation | `re` (Regular Expression) | Kiểm tra sự hiện diện của input token ẩn trong form biểu mẫu. |
| **WebVulnScanner** | SSRF Tester | Private IP & Loopback Filter | `re`, `urllib.parse` | Phát hiện hành vi điều hướng request về IP nội bộ / Loopback (`127.0.0.1`, RFC 1918). |
| **WebVulnScanner** | Giao diện điều khiển Web | Web UI Dashboard | `Flask`, `Jinja2` | Cho phép quét theo từng module, hiển thị bảng đánh giá mức độ rủi ro trực quan. |
| **JWTSecure** | Cấu trúc Token | RFC 7519 JSON Web Token | `PyJWT` | Định dạng Stateless Token gồm 3 phần: Header, Payload (Claims), Signature. |
| **JWTSecure** | Kiểm tra toàn vẹn | HMAC-SHA256 (HS256) | `jwt.decode` | Xác minh chữ ký số và từ chối token giả mạo, chỉnh sửa hoặc đã hết hạn (`exp`). |
| **JWTSecure** | Kiểm thử Brute-force | Dictionary Attack | `concurrent.futures.ThreadPoolExecutor` | Rà soát khóa yếu đa luồng chứng minh nguy cơ khi dùng secret ngắn/dễ đoán. |
| **JWTSecure** | Quản lý vòng đời Token | Dual-Token Lifecycle | `TokenManager` | Phân tách Access Token (hạn ngắn 15 phút) và Refresh Token (hạn dài 24 giờ). |
| **JWTSecure** | Ủy quyền OAuth 2.0 | Authorization Code Flow | `OAuthClient`, `requests` | Luồng xác thực chuyển hướng chuẩn hóa an toàn cho ứng dụng web. |
| **JWTSecure** | Bảo vệ API Endpoint | Bearer Authentication | `Flask Middleware` | Xác thực token từ Authorization header trước khi cấp quyền truy cập tài nguyên. |
| **DevSecOps** | Kiểm soát mã nguồn | Pre-commit Git Hook | `GitSecure (.githooks)` | Tự động quét regex phát hiện thông tin nhạy cảm, chặn commit khi lộ secret. |

---

## 4. Hướng dẫn thiết lập & Chạy ứng dụng

Kích hoạt môi trường ảo Python (`venv`) tại thư mục gốc của repository:
```powershell
.\venv\Scripts\Activate.ps1
```

Cài đặt các gói phụ thuộc cần thiết:
```powershell
pip install -r Buoi4/web-vuln-scanner/requirements.txt
pip install -r Buoi4/jwt-security-tools/requirements.txt
```

---

## 5. Thực nghiệm và minh chứng

### HỢP PHẦN 1: BỘ CÔNG CỤ QUÉT LỖ HỔNG (WEBVULNSCANNER)

#### Bước 1: Chạy và kiểm tra Unit Test WebVulnScanner
* **Thao tác:** Mở Terminal, di chuyển vào thư mục `Buoi4/web-vuln-scanner` và chạy unittest kiểm thử toàn diện 4 module scanner và report generator:
  ```powershell
  cd "Buoi4\web-vuln-scanner"
  ..\..\venv\Scripts\python -m unittest discover tests
  ```
* **Kết quả đạt được:** Hệ thống thực thi hoàn thành toàn bộ 9/9 unit test cases trong 0.001 giây với kết quả `OK`. Tất cả các module kiểm thử riêng biệt (XSS Scanner, SQLi Tester, CSRF Detector, SSRF Tester và Report Generator) đều đạt tính đúng đắn và độ tin cậy tuyệt đối.

![Unit Test Web Scanner](ảnh/01_web_scanner_unittest.jpg)

---

#### Bước 2: Chạy kiểm tra chương trình chính `main.py`
* **Thao tác:** Tại thư mục `Buoi4/web-vuln-scanner`, chạy lệnh kiểm tra phân tích tổng hợp:
  ```powershell
  ..\..\venv\Scripts\python .\main.py
  ```
* **Kết quả đạt được:** Chương trình `main.py` tự động tổng hợp kết quả quét từ 4 module, bóc tách và phân loại thành công 3 nguy cơ bảo mật trong chuỗi URL và form mẫu:
  - Lỗ hổng SQL Injection tại tham số `id` (Mức độ rủi ro: `Critical`).
  - Lỗ hổng SSRF truy cập tài nguyên nội bộ `127.0.0.1` tại tham số `url` (Mức độ rủi ro: `High`).
  - Form HTML mẫu chứa token hợp lệ nên đạt trạng thái an toàn trước CSRF.

![Chạy Main Web Scanner](ảnh/02_web_scanner_main.jpg)

---

#### Bước 3: Giao diện Form kiểm thử Web Scanner
* **Thao tác:** Khởi động máy chủ Flask UI (`python .\ui\app.py`), mở trình duyệt web truy cập `http://127.0.0.1:5000/`. Nhập URL kiểm thử (ví dụ: `http://example.com/page?input=<script>alert(1)</script>&id=' OR '1'='1&url=http://127.0.0.1/admin`), tích chọn cả 4 công cụ (XSS, SQL, CSRF, SSRF):
* **Kết quả đạt được:** Khởi chạy thành công máy chủ Flask Web trên cổng nội bộ `http://127.0.0.1:5000/`. Giao diện Web trực quan hiển thị đầy đủ trường nhập URL mục tiêu cùng các checkbox linh hoạt cho phép tùy chọn quét đồng thời hoặc riêng lẻ từng loại lỗ hổng.

![Form Web Scanner](ảnh/04_web_scanner_ui_form.jpg)

---

#### Bước 4: Báo cáo kết quả quét lỗ hổng trên Web UI (Khớp 100% Slide bài giảng)
* **Thao tác:** Nhập URL mục tiêu kiểm thử `http://testphp.vulnweb.com/artists.php?artist=1'` và bấm nút **"Bắt đầu kiểm thử"** để nhận kết quả phân tích lỗ hổng:
* **Kết quả đạt được:** Hệ thống phân tích sâu và trả về trang báo cáo trực quan với thiết kế phân loại màu sắc rủi ro rõ rệt:
  - Phát hiện **2 lỗ hổng Reflected XSS** (Mức độ `HIGH`) với hai payload kiểm thử `<script>alert(1)</script>` và `"><svg/onload=alert(1)>`.
  - Phát hiện lỗ hổng thiếu token bảo vệ **CSRF** (Mức độ `Medium`).
  - Giao diện và kết quả trả về khớp hoàn toàn 100% với kịch bản thực nghiệm trong slide bài giảng của Giảng viên.

![Kết quả Web Scanner](ảnh/05_web_scanner_ui_result.jpg)

---

### HỢP PHẦN 2: BẢO MẬT TOKEN & API GATEWAY (JWTSECURE)

#### Bước 5: Chạy kiểm thử toàn diện bằng Pytest
* **Thao tác:** Mở Terminal, di chuyển vào thư mục `Buoi4/jwt-security-tools` và chạy Pytest kiểm thử APIGateway, JWTCracker, OAuthClient, TokenManager, JWTValidator (7/7 Passed):
  ```powershell
  cd "..\jwt-security-tools"
  ..\..\venv\Scripts\pytest tests/
  ```
* **Kết quả đạt được:** Thực thi hoàn tất bộ kiểm thử tự động với kết quả **7/7 test passed (100%)** bao gồm: xác thực tính hợp lệ của JWT (`test_validator.py`), bẻ khóa bí mật yếu bằng dictionary attack (`test_cracker.py`), luồng cấp mã xác thực OAuth 2.0 (`test_oauth_client.py`), phát hành & làm mới token (`test_token_manager.py`), và bảo vệ API Gateway (`test_api_gateway.py`).

![Pytest JWTSecure](ảnh/07_jwt_pytest.jpg)

---

#### Bước 6: Khởi động chương trình chính `main.py` cấp phát Token cho user Huy
* **Thao tác:** Tại thư mục `Buoi4/jwt-security-tools`, chạy:
  ```powershell
  ..\..\venv\Scripts\python .\main.py
  ```
* **Kết quả đạt được:** Ứng dụng khởi tạo thành công cặp mã định danh chuẩn RFC 7519 cho người dùng **Huy**:
  - `Access Token` (thời hạn 15 phút) phục vụ truy cập nhanh vào các endpoint tài nguyên.
  - `Refresh Token` (thời hạn 24 giờ) phục vụ cơ chế cấp mới token không cần đăng nhập lại.
  - Kích hoạt thành công cổng `APIGateway` lắng nghe kết nối tại cổng `5000`.

![Chạy Main JWTSecure](ảnh/08_jwt_main_run.jpg)

---

#### Bước 7: Kiểm tra xác thực Bearer Token bằng cURL
* **Thao tác:** Mở cửa sổ Terminal mới (hoặc Command Prompt `cmd`), copy chuỗi `Access Token` của user Huy và thực thi lệnh cURL để kiểm tra quyền truy cập endpoint `/protected`:
  ```cmd
  curl -H "Authorization: Bearer <access_token_cua_Huy>" http://127.0.0.1:5000/protected
  ```
* **Kết quả đạt được:** Cổng APIGateway giải mã chữ ký HMAC SHA-256 của token, trích xuất claim `sub` hợp lệ và phản hồi mã trạng thái HTTP `200 OK` với dữ liệu JSON: `{"message": "Access granted", "user": "Huy"}`. Chứng minh cơ chế xác thực Bearer Token của API Gateway hoạt động an toàn và bảo mật đúng theo thiết kế.

![Xác thực cURL](ảnh/09_jwt_curl_test.jpg)



