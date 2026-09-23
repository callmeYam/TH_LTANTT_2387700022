# Lab 2: Tự Động Hóa Kiểm Tra An Toàn Mã Nguồn Với Git Hooks (GitSecure)

Dự án xây dựng công cụ Pre-commit Hook tự động quét và ngăn chặn việc commit các thông tin nhạy cảm (API keys, secrets, passwords, tokens, AWS keys), kiểm tra phân quyền file nguy hiểm và quét lỗ hổng mã nguồn bằng Bandit.

## Cấu trúc thư mục

```
Lab2/
├── .githooks/
│   └── pre-commit
├── pre-commit-hook-test/
│   └── bad.py
├── .gitignore
├── README.md
└── requirements.txt
```

## Các tính năng kiểm tra của GitSecure
1. **Quét thông tin nhạy cảm (`scan_sensitive`)**: Dùng Regex phát hiện các secret bị hardcode như `password`, `secret`, `apikey`, `token` và `AKIA/ASIA` (AWS Access Key).
2. **Kiểm tra phân quyền file (`check_permissions`)**: Cảnh báo file world-writable (`stat.S_IWOTH`) trên Unix/Linux, tự động tương thích và bỏ qua trên Windows.
3. **Quét lỗ hổng tĩnh (`run_bandit`)**: Chạy công cụ Bandit (`bandit -r .`) để tự động phát hiện các lỗ hổng mã nguồn Python mức độ nghiêm trọng (High Severity).
4. **Ghi nhật ký (`log`)**: Tự động ghi lại thời gian và chi tiết vi phạm vào tệp `gitsecure.log`.
5. **Chặn lệnh commit (`main`)**: Dừng tiến trình commit với mã thoát `sys.exit(1)` khi phát hiện bất kỳ nguy cơ bảo mật nào.

## Cài đặt thư viện
```bash
pip install -r requirements.txt
```

## Kích hoạt Hook trong Git
Để Git nhận diện pre-commit hook trong thư mục `.githooks`:
```bash
git config core.hooksPath Buoi1/Lab2/.githooks
```
*(Nếu trên Linux/macOS hoặc Git Bash, hãy cấp quyền thực thi: `chmod +x Buoi1/Lab2/.githooks/pre-commit`)*

## Thử nghiệm Hook tiêu chuẩn
Thử nghiệm thêm file chứa thông tin nhạy cảm `pre-commit-hook-test/bad.py` (chứa `password = "123456"`):
```bash
git add Buoi1/Lab2/pre-commit-hook-test/bad.py
git commit -m "test commit password"
```

**Kết quả nhận được (Hook chặn thành công):**
```text
COMMIT BLOCKED by GitSecure:
 - Sensitive info found in Buoi1/Lab2/pre-commit-hook-test/bad.py: pattern password\s*=\s*['"][^'"]{4,}['"]
```
Nhật ký vi phạm được ghi tự động vào file `gitsecure.log`.

---

## Thực nghiệm Bypass các cơ chế kiểm tra (Bypass Analysis)

Dưới đây là các ca thực nghiệm bypass thực tế được nghiên cứu và thử nghiệm nhằm đánh giá giới hạn phát hiện của bộ lọc Regex trong GitSecure:

| Kỹ thuật kiểm tra | Chuỗi Payload thực nghiệm | Kết quả trả về | Cơ chế & Phân tích lỗ hổng |
| :--- | :--- | :--- | :--- |
| **Tách & Nối chuỗi** *(String Concatenation)* | `password = "12" + "3456"` | **`An toàn` (Bypass)** | **Giới hạn độ dài Regex:** Regex bắt buộc chuỗi liền sau `password =` phải có từ 4 ký tự trở lên (`{4,}`). Khi chia nhỏ thành `"12"` (chỉ 2 ký tự) rồi nối với `"3456"`, Regex không khớp được, nhưng khi chạy code Python thì mật khẩu thực tế vẫn là `"123456"`. |
| **Dùng Dictionary / JSON** | `config = {"password": "super_secret_123"}` | **`An toàn` (Bypass)** | **Ràng buộc toán tử gán:** Regex của GitSecure chỉ tìm kiếm cú pháp có dấu gán `\s*=\s*`. Trong khi đó, các file config, Dictionary hay JSON sử dụng dấu hai chấm `:` để ngăn cách key-value. Bộ lọc hoàn toàn bỏ sót các trường hợp lưu trữ secret dạng này. |
| **Đổi tên biến đồng nghĩa** *(Synonym Variables)* | `passwd = "admin_pass"`<br>`db_pass = "root_123456"`<br>`pwd = "secret_pass"` | **`An toàn` (Bypass)** | **Danh sách từ khóa cố định:** Regex chỉ bắt cứng chuỗi ký tự `password`. Lập trình viên hoặc kẻ xấu chỉ cần đổi tên biến thành các từ đồng nghĩa như `passwd`, `pwd`, `db_pass` là vượt qua kiểm tra dễ dàng. |
| **Mã hóa chuỗi Base64** | `import base64`<br>`password = base64.b64decode("MTIzNDU2").decode()` | **`An toàn` (Bypass)** | **Che giấu văn bản thô (Obfuscation):** Chuỗi bí mật được mã hóa Base64 không còn ở dạng văn bản rõ (cleartext). Kỹ thuật này vừa qua mặt được Regex quét chuỗi, vừa không bị công cụ phân tích tĩnh Bandit cảnh báo. |
| **Bỏ qua Hook bằng cờ Git CLI** | `git commit -m "bypass" --no-verify` | **`Bỏ qua toàn bộ Hook` (Bypass)** | **Hạn chế của Client-side Hook:** Đây là cờ mặc định của Git (`--no-verify` hoặc `-n`). Vì pre-commit hook chỉ chạy ở máy local của người dùng, cờ này sẽ ra lệnh cho Git bỏ qua toàn bộ script kiểm tra và đẩy thẳng file vi phạm lên repo. |
