# Lab 1: Kiểm Tra Đầu Vào & Làm Sạch Dữ Liệu (SecureValidator)

Dự án xây dựng thư viện xác thực đầu vào và ứng dụng web Flask để phòng chống các lỗ hổng cơ bản: SSRF, Path Traversal, SQL Injection, XSS.

## Cấu trúc thư mục

```
Lab1/
├── securevalidator/
│   ├── __init__.py
│   └── core.py
├── templates/
│   └── index.html
├── tests/
│   └── test_validators.py
├── README.md
├── app.py
└── requirements.txt
```

## Các tính năng xác thực và làm sạch
1. **Email Validation (`validate_email`)**: Kiểm tra regex cấu trúc email hợp lệ, ngăn chặn double dots.
2. **URL Validation (`validate_url`)**: Kiểm tra scheme `http`/`https` và `netloc` nhằm ngăn chặn SSRF.
3. **Filename Validation (`validate_filename`)**: Chặn path traversal (`..`, `/`, `\`) và so sánh với basename.
4. **SQL Sanitization (`sanitize_sql_input`)**: Loại bỏ các ký tự đặc biệt (`--`, `;`, `'`, `"`, `#`) và các từ khóa SQL nhạy cảm (`OR`, `AND`, `SELECT`, `INSERT`, `DELETE`, `UPDATE`, `DROP`, `UNION`, `WHERE`).
5. **HTML Sanitization (`sanitize_html_input`)**: Escape các ký tự đặc biệt thành thực thể HTML (`&lt;`, `&gt;`, `&quot;`, `&amp;`) để phòng chống XSS.

## Cài đặt thư viện
```bash
pip install -r requirements.txt
```

## Chạy ứng dụng Web
```bash
python app.py
```
Truy cập giao diện tại: `http://127.0.0.1:5000` hoặc trang đã triển khai: `https://securevalidator-4ydb.onrender.com/`

## Chạy bộ kiểm thử tự động
```bash
python -m unittest discover tests
```

---

## Thực nghiệm Bypass các cơ chế kiểm tra (Bypass Analysis)

Dưới đây là các ca thực nghiệm bypass thực tế được thực hiện trực tiếp trên giao diện ứng dụng:

| Trường kiểm tra | Chuỗi Payload thực nghiệm | Kết quả trả về | Cơ chế & Phân tích lỗ hổng |
| :--- | :--- | :--- | :--- |
| **Email** | `_a@hihi._vd_` | **`Email hợp lệ` (Bypass)** | **Regex quá lỏng lẻo:** Biểu thức regex dùng `\w` bao gồm cả chữ cái, chữ số và dấu gạch dưới `_`. Phần đuôi domain `\.\w+$` chấp nhận cả `_vd_` dù theo chuẩn RFC và ICANN thì TLD không bao giờ chứa dấu gạch dưới. Dấu chấm lơ lửng `hihi.` cũng được chấp nhận. |
| **URL (SSRF)** | `http://1` | **`URL hợp lệ` (Bypass)** | **Thiếu kiểm tra IP nội bộ / định dạng mạng:** `urllib.parse.urlparse("http://1")` tách scheme là `http` và `netloc` là chuỗi `'1'` (khác rỗng nên `bool('1') == True`). Trong mạng máy tính, `1` là dạng số nguyên rút gọn của địa chỉ IP `0.0.0.1`. Hệ thống chỉ kiểm tra scheme và netloc mà không xác thực hostname/IP hợp lệ, dẫn đến lỗ hổng SSRF. |
| **Filename** | `_file.txt` *(hoặc `CON`, `PRN`, `AUX`)* | **`Tên file hợp lệ`** | Hàm kiểm tra chỉ loại trừ `..`, `/`, `\` nhưng không kiểm tra các tên file thiết bị dành riêng trên Windows (Reserved Device Names như `CON`, `PRN`, `AUX`, `NUL`). Nếu ứng dụng mở hoặc ghi file với các tên này trên Windows sẽ gây lỗi treo hệ thống (DoS). |
| **SQL Input** | `SSELECTELECT * FROM users` | **`Đã lọc: SSELECTELECT * FROM users` (Bypass)** | **Ranh giới từ trong Regex:** Regex dùng `\bSELECT\b` với ranh giới từ `\b`. Khi từ khóa `SELECT` nằm giữa `S` và `ELECT`, ranh giới từ không khớp nên chuỗi không hề bị xóa. Ngoài ra, việc dùng toán tử thay thế `1 \|\| 1=1`, hex `0x61646d696e` hay chú thích inline `/* */` cũng qua mặt bộ lọc hoàn toàn. |
| **HTML Input** | `javascript:alert(1)` | **`Đã mã hóa: javascript:alert(1)` (Bypass)** | **Ngữ cảnh không an toàn:** Hàm `html.escape` chỉ escape `<, >, &, ", '`. Payload `javascript:alert(1)` không chứa ký tự đặc biệt nên được giữ nguyên. Nếu lập trình viên đưa giá trị này vào thuộc tính thẻ `<a href="...">`, người dùng click vào sẽ bị thực thi mã độc XSS. |
