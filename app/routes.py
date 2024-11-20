from flask import Flask, render_template, request, session, redirect, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Lỗ hổng: Secret key không an toàn

DATABASE = "app.db"

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
        password = request.form["password"]  # Lỗ hổng: Lưu mật khẩu không mã hóa
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
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()  # Trả về tuple hoặc None
        conn.close()
        if user and user[0] == password:  # So sánh mật khẩu dạng plain-text
            session["username"] = username
            return redirect(url_for("home"))
        return "Invalid credentials", 401
    return render_template("login.html")

@app.route("/")
def home():
    return render_template("home.html", user=session.get("username"))

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return "No file uploaded", 400
    file = request.files["file"]
    if file.filename == "":
        return "No selected file", 400
    filepath = f"./uploads/{file.filename}"  # Lỗ hổng: Không kiểm tra loại file hoặc path traversal
    file.save(filepath)
    return f"File uploaded to {filepath}"

@app.route("/logout")
def logout():
    # Không hủy toàn bộ session
    session.pop("username", None)  # Lỗ hổng: Session ID vẫn tồn tại
    return redirect(url_for("home"))

app.config["SESSION_COOKIE_SECURE"] = False  # Chỉ gửi cookie qua HTTPS
app.config["SESSION_COOKIE_HTTPONLY"] = False  # Chặn JavaScript truy cập cookie
# app.config["SESSION_COOKIE_SAMESITE"] = "Lax"  # Giảm nguy cơ cross-site attack

