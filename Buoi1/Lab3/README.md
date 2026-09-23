# Lab 3: Ghi Nhật Ký Ưu Tiên Bảo Mật (SecureLogger)

Dự án xây dựng hệ thống ghi nhật ký an toàn cho ứng dụng Flask với các cơ chế: che giấu thông tin định danh cá nhân (PII), chống tấn công Log Injection bằng định dạng JSON, kiểm tra tính toàn vẹn (Tamper Detection) bằng chữ ký băm SHA-256 và tự động xoay vòng nén log (Gzip).

## Cấu trúc thư mục

```
Lab3/
├── securelogger/
│   ├── __init__.py
│   └── logger.py
├── securevalidator/
│   ├── __init__.py
│   └── core.py
├── .gitignore
├── README.md
├── app.py
└── requirements.txt
```

## Các tính năng bảo mật của SecureLogger
1. **Che giấu thông tin cá nhân (`mask_pii`)**: Dùng Regex tự động phát hiện và thay thế các chuỗi nhạy cảm (Email, API Key, Token, Password) thành `<email_masked>`, `<token_masked>`.
2. **Chống tấn công Log Injection (`JSONFormatter`)**: Định dạng mọi dòng log thành đối tượng JSON có cấu trúc, tự động escape ký tự xuống dòng và điều khiển, kèm trường thời gian UTC theo chuẩn ISO 8601.
3. **Phát hiện sửa đổi nhật ký (`append_signature`)**: Băm SHA-256 nội dung của từng dòng log và lưu tuần tự vào file chữ ký `secure.log.sig` để phục vụ xác thực toàn vẹn.
4. **Quản lý xoay vòng và nén file log (`GZipRotator`)**: Tự động xoay file log khi đạt dung lượng tối đa 1MB, lưu trữ tối đa 2 bản sao dự phòng và nén các file cũ dưới định dạng `.gz`.

## Cài đặt thư viện
```bash
pip install -r requirements.txt
```

## Chạy ứng dụng API
```bash
python app.py
```
Ứng dụng Flask sẽ lắng nghe tại: `http://127.0.0.1:5000`

## Thử nghiệm tiêu chuẩn (Standard Testing)
Gửi yêu cầu POST đến endpoint `/validate`:
```bash
curl -X POST http://127.0.0.1:5000/validate \
     -H "Content-Type: application/json" \
     -d "{\"email\":\"phuoc@example.com\",\"url\":\"https://secure.com\",\"filename\":\"report.pdf\",\"sql\":\"' OR 1=1 --\",\"html\":\"<script>alert(1)</script>\"}"
```

**Kết quả ghi nhận trong file `secure.log`:**
```json
{"timestamp": "2026-09-23T...", "level": "INFO", "message": "Validation check performed", "data": "{'email': '<email_masked>', ...}", "results": "..."}
```
Và file `secure.log.sig` được tạo ra chứa chuỗi băm SHA-256 tương ứng để xác thực tính toàn vẹn.

---

## Thực nghiệm Bypass các cơ chế kiểm tra (Bypass Analysis)

Để đi sâu phân tích cơ chế hoạt động, tôi tiến hành nghiên cứu các góc độ lập trình khác nhau nhằm tìm ra các trường hợp mà `SecureLogger` bỏ sót dữ liệu nhạy cảm hoặc cơ chế phát hiện giả mạo bị vô hiệu hóa:

| Trường kiểm tra | Dữ liệu Payload thực nghiệm | Kết quả ghi nhận trong `secure.log` | Cơ chế & Phân tích lỗ hổng |
| :--- | :--- | :--- | :--- |
| **Mật khẩu ngắn (< 8 ký tự)** | `password = "123456"` *(hoặc `root`, `admin1`)* | **`password = "123456"` (Bị rò rỉ!)** | **Giới hạn độ dài Regex:** Biểu thức regex chỉ che mật khẩu có độ dài từ 8 ký tự trở lên (`[^\'\"]{8,}`). Nếu người dùng đặt mật khẩu ngắn 6 hay 7 ký tự thì regex hoàn toàn bỏ sót, khiến mật khẩu bị ghi lộ nguyên văn dưới dạng cleartext vào log. |
| **Dữ liệu cấu hình JSON / Dict** | `{"password": "super_secret_password_123"}` | **`{"password": "super_secret_password_123"}` (Bị rò rỉ!)** | **Ràng buộc toán tử gán:** Regex của hàm `mask_pii` chỉ bắt cú pháp có dấu gán `\s*=\s*`. Khi ứng dụng nhận payload JSON từ request (`data`), cặp key-value được ngăn cách bằng dấu hai chấm `:`. Do đó, toàn bộ mật khẩu gửi qua JSON không hề bị che giấu. |
| **Email chứa ký tự đặc biệt (RFC tags)** | `user+admin@company.com` | **`user+<email_masked>` (Bị lộ một phần!)** | **Regex email thiếu ký tự hợp lệ:** Regex chỉ cho phép `[\w\.-]`, không chứa dấu cộng `+`. Do đó hàm chỉ nhận diện phần `admin@company.com` là email để che, còn phần định danh nhạy cảm `user+` phía trước vẫn bị phơi bày trong log. |
| **Giả mạo chữ ký (Tamper Detection Bypass)** | Sửa dòng log và tự tính `hashlib.sha256(new_line)` | **Chữ ký hoàn toàn hợp lệ (Bypass)** | **Thiếu Secret Key (Không dùng HMAC):** Hàm `hash_line` chỉ băm thuần SHA-256 mà không kết hợp với khóa bí mật (Secret Key). Nếu kẻ xấu có quyền truy cập vào máy chủ để sửa trộm log, họ hoàn toàn có thể tự băm lại dòng log mới và ghi đè vào `secure.log.sig` mà không hề bị phát hiện. |
| **Tấn công cắt xén log (Truncation Attack)** | Xóa bỏ $N$ dòng log cuối ở cả 2 tệp | **Hệ thống không phát hiện được** | **Thiếu liên kết chuỗi băm (Hash Chain):** Mỗi dòng log được băm độc lập rải rác từng dòng. Nếu kẻ tấn công xóa dòng vi phạm cuối cùng trong `secure.log` đồng thời xóa dòng chữ ký tương ứng ở `secure.log.sig`, các dòng còn lại vẫn khớp từng đôi một và hệ thống không biết rằng log đã bị xóa bớt. |
