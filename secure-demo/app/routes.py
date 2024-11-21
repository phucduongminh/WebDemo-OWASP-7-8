from flask import Flask, render_template, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Lỗ hổng: Secret key không an toàn
limiter = Limiter(get_remote_address, app=app)

DATABASE = "app.db"
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

@app.route("/", methods=["GET", "POST"])
def home():
    files = os.listdir(app.config["UPLOAD_FOLDER"]) if os.path.exists(app.config["UPLOAD_FOLDER"]) else []
    message = None  # Thông báo kết quả upload

    if request.method == "POST":
        # Xử lý upload file
        if "file" not in request.files:
            message = "No file uploaded"
        else:
            file = request.files["file"]
            if file.filename == "":
                message = "No selected file"
            else:
                if not os.path.exists(app.config["UPLOAD_FOLDER"]):
                    os.makedirs(app.config["UPLOAD_FOLDER"])
                
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
                file.save(filepath)
                message = f"File '{file.filename}' uploaded successfully"

        # Lấy danh sách file lại sau upload
        files = os.listdir(app.config["UPLOAD_FOLDER"])

    return render_template("home.html", user=session.get("username"), files=files, message=message)

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return {"error": "No file uploaded"}, 400 if request.accept_mimetypes["application/json"] else "No file uploaded", 400
    file = request.files["file"]
    if file.filename == "":
        return {"error": "No selected file"}, 400 if request.accept_mimetypes["application/json"] else "No selected file", 400

    if not os.path.exists(app.config["UPLOAD_FOLDER"]):
        os.makedirs(app.config["UPLOAD_FOLDER"])
    
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)

    if request.accept_mimetypes["application/json"]:
        return {"message": "File uploaded successfully", "filename": file.filename}, 200
    else:
        return redirect(url_for("home"))

@app.route("/logout")
def logout():
    session.clear()  # Xóa toàn bộ session
    return redirect(url_for("home"))

app.config["SESSION_COOKIE_SECURE"] = True  # Chỉ gửi cookie qua HTTPS
app.config["SESSION_COOKIE_HTTPONLY"] = True  # Chặn JavaScript truy cập cookie
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"  # Giảm nguy cơ cross-site attack

