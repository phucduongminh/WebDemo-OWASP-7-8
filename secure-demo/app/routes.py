from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import magic
import sqlite3
import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
app.secret_key = "supersecretkey"
limiter = Limiter(get_remote_address, app=app)

DATABASE = "app.db"

# Cấu hình loại file cho phép và kích thước tối đa
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'}
ALLOWED_MIME_TYPES = {
    'text/plain', 
    'application/pdf', 
    'image/png', 
    'image/jpeg', 
    'image/gif', 
    'application/msword', 
    'application/vnd.ms-excel', 
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 
    'application/vnd.ms-powerpoint', 
    'application/vnd.openxmlformats-officedocument.presentationml.presentation'
}
MAX_CONTENT_LENGTH = 30 * 1024 * 1024  # 30 MB

app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
UPLOAD_FOLDER = "./uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"]) # Đã mã hóa
        try:
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
        except sqlite3.IntegrityError:
            return "Username already exists", 400
        finally:
            conn.close()
        return redirect(url_for("login"))
    return render_template("register.html")
@app.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute") # Giới hạn 5 lần đăng nhập mỗi phút
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()  # Trả về tuple hoặc None
        conn.close()
        if user and check_password_hash(user[0], password):  # So sánh mật khẩu dạng plain-text
            session["username"] = username
            return redirect(url_for("home"))
        return "Invalid credentials", 401
    return render_template("login.html")

def allowed_file(filename):
    # Kiểm tra phần mở rộng của file
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_mime_type(file_stream):
    # Sử dụng python-magic để đọc MIME type từ nội dung file
    mime = magic.Magic(mime=True)
    mime_type = mime.from_buffer(file_stream)
    return mime_type in ALLOWED_MIME_TYPES

@app.route("/", methods=["GET", "POST"])
def home():
    # Ensure the upload folder exists before listing files
    if not os.path.exists(app.config["UPLOAD_FOLDER"]):
        os.makedirs(app.config["UPLOAD_FOLDER"])
    
    files = os.listdir(app.config["UPLOAD_FOLDER"])

    message = None  # Thông báo kết quả upload

    if request.method == "POST":
        # Xử lý upload file
        if "file" not in request.files:
            message = "No file uploaded"
        else:
            file = request.files["file"]
            if file.filename == "":
                message = "No selected file"
            elif not allowed_file(file.filename):
                message = "File type not allowed by extension"
            else:
                # Kiểm tra MIME type từ nội dung file
                file_stream = file.stream.read()
                if not allowed_mime_type(file_stream):
                    message = "File type not allowed by MIME type"
                else:
                    # Đặt lại con trỏ file sau khi đọc
                    file.stream.seek(0)
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                    file.save(filepath)
                    message = f"File '{file.filename}' uploaded successfully"

        # Lấy danh sách file lại sau upload
        files = os.listdir(app.config["UPLOAD_FOLDER"])

    return render_template("home.html", user=session.get("username"), files=files, message=message)

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed by extension"}), 400

    # Kiểm tra MIME type từ nội dung file
    file_stream = file.stream.read()
    if not allowed_mime_type(file_stream):
        return jsonify({"error": "File type not allowed by MIME type"}), 400

    # Đặt lại con trỏ file sau khi đọc
    file.stream.seek(0)
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    if not os.path.exists(app.config["UPLOAD_FOLDER"]):
        os.makedirs(app.config["UPLOAD_FOLDER"])
    file.save(filepath)

    return jsonify({"message": f"File '{filename}' uploaded successfully"}), 200

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# Cấu hình bảo mật cookie
app.config["SESSION_COOKIE_SECURE"] = True  # Chỉ gửi cookie qua HTTPS
app.config["SESSION_COOKIE_HTTPONLY"] = True  # Chặn JavaScript truy cập cookie
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"  # Giảm nguy cơ cross-site attack
