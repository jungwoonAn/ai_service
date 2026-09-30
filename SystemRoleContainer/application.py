from flask import Flask, render_template, request

from chatbot import Chatbot
from common import model
from characters import system_role, instruction

# Chatbot 객체 생성
chatbot = Chatbot(
    system_role=system_role,
    instruction=instruction,
    use_model=model.basic
)
application = Flask( __name__ )

@application.route( "/" )
def index():
    return "Hello, ChatGPT"

# chat_app 함수 정의
@application.route( "/chat-app" )
def chat_app():
    return render_template( "chat.html" )  

# chat_api 함수 정의
@application.route("/chat-api", methods=['POST'])
def chat_api():
    # 사용자 입력 내용
    print(f'request_message : {request.json}')
    user_input = request.json['request_message']

    # Chatbot 객체를 이용하여 ChatGPT에 요청 및 응답 수신
    chatbot.add_user_message(user_input)  # 사용자 메시지 추가
    response = chatbot.send_request()  # API 요청
    chatbot.add_response(response)  # 응답 메시지 context 추가

    # 응답 결과 출력
    response_message = chatbot.get_response(response)  # 응답 출력
    chatbot.handle_token_limit(response)  # 토큰수 제어 메서드 실행
    chatbot.clear_context()  # instruction 삭제
    print(f'response_message : {response_message}')

    return {"response_message": response_message}

if __name__ == "__main__":
    application.run( host = '0.0.0.0', port = 8080, debug = True )
