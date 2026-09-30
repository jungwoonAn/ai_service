from common import model, client

class Chatbot:
    def __init__(self, system_role="You are a helpful assistant", use_model=model.basic):
        # context 초기화 및 대화 문맥 생성
        self.model = use_model
        self.context = [
            {"role": "system", "content": system_role}
        ]

    # 사용자 메시지를 context에 추가
    def add_user_message(self, message):
        self.context.append(
            {"role": "user", "content": message}
        )

    # context 전체를 OpenAI API로 전송
    def send_request(self):
        response = client.responses.create(
            model=self.model,
            input=self.context
        )
        return response

    # 응답 내용을 context에 추가
    def add_response(self, response):
        response_text = response.output_text
        self.context.append(
            {"role": "assistant","content": response_text}
        )

    # 응답 내용을 출력하고 반환
    def get_response(self, response):
        response_text = response.output_text
        print(response_text)
        return response_text