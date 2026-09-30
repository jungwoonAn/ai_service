# app.py
from flask import Flask   # Flask 객체 load

app = Flask(__name__)     # Flask 객체 생성

@app.route('/')           # 기본 주소에 대한 route 함수
def index():
    return 'Hello, World!!'

if __name__ == '__main__':  # 파이썬 파일을 직접 실행했을 때만 아래 코드를 실행하겠다는 의미
    # host='0.0.0.0' -> 모든 client로부터 요청 수신 하겠다.
    # port='8080' -> 현재 server의 8080 port 사용
    app.run(host='0.0.0.0', port='8080', debug=True)  # Application Server 실행