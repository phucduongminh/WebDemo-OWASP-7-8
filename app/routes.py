from flask import Flask, render_template, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "insecure_key"  # Lỗ hổng: Secret key không an toàn

# Mock database
users = {}

@app.route("/")
def home():
    return render_template("home.html", user=session.get("username"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = users.get(username)
        if user and user["password"] == password:  # Lỗ hổng: Mật khẩu không mã hóa
            session["username"] = username
            return redirect(url_for("home"))
        return "Invalid credentials", 401
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        users[username] = {"password": password}  # Lỗ hổng: Lưu mật khẩu dạng plain text
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return "No file uploaded", 400
    file = request.files["file"]
    filepath = f"./uploads/{file.filename}"  # Lỗ hổng: Không kiểm tra loại file hoặc path traversal
    file.save(filepath)
    return f"File uploaded to {filepath}"

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("home"))
