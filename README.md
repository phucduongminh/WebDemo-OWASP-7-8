# Xây dựng Web Demo kiểm thử OWAPS 7 và 8
## Chuẩn bị bộ dữ liệu test và web demo
Web demo: Tạo ứng dụng Flask đơn giản với các chức năng như đăng nhập, đăng ký, quản lý mật khẩu, tải file (biểu hiện lỗ hổng OWASP 7 và 8).

## Chạy ứng dụng cục bộ

## Lỗ hổng cụ thể (OWASP 7, 8)
### OWASP 7:
Không giới hạn số lần đăng nhập sai.
Session không được bảo mật.
Không mã hóa dữ liệu đăng nhập.
### OWASP 8:
Thư viện không được kiểm tra tính toàn vẹn.
Xử lý file tải lên không an toàn.

## Test bảo mật với dữ liệu test
Viết script và hướng dẫn kiểm thử.

## Update bảo mật
Áp dụng các biện pháp phòng chống.

## Test bảo mật lần 2 và ghi lại kết quả
Lặp lại kiểm thử sau khi bảo mật.

## Cài đặt
pip install -r requirements.txt
python run.py

(Không cần chạy:
docker build -t flask-demo .
docker run -p 5000:5000 flask-demo)

## Tiến hành test
### Kiểm thử brute-force (OWASP 7)
python tests/test_auth.py

### Kiểm thử lưu mật khẩu dạng plain-text (OWASP 7)

### Kiểm thử upload file không an toàn (OWASP 8)
Sử dụng Git Bash:
curl -X POST -F "file=@malicious.py" http://localhost:5000/upload

### Thư viện không được kiểm tra tính toàn vẹn
Mô phỏng: Thêm một thư viện bên ngoài không đáng tin cậy, như:
pip install some-untrusted-package

Giải pháp: 
Sử dụng pip-audit để kiểm tra tính toàn vẹn:
pip install pip-audit
pip-audit

Thư viện không kiểm tra tính toàn vẹn
Mô phỏng: Sử dụng thư viện từ nguồn không đáng tin hoặc không khóa phiên bản cụ thể.
Cách triển khai lỗ hổng: Trong requirements.txt, dùng thư viện không khóa phiên bản:

flask
werkzeug

Thay vào đó, khóa phiên bản cụ thể trong requirements.txt
flask==2.0.3
werkzeug==2.0.3