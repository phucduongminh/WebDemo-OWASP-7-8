from app.routes import app, init_db

if __name__ == "__main__":
    with app.app_context():  # Đảm bảo sử dụng app context
        init_db()  # Khởi tạo cơ sở dữ liệu
    app.run(debug=True)
