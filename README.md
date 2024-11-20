pip install -r requirements.txt
python run.py

docker build -t flask-demo .
docker run -p 5000:5000 flask-demo

Test:
python tests/test_auth.py
curl -X POST -F "file=@malicious.py" http://localhost:5000/upload

