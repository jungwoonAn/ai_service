from common import client, model
from characters import system_role
from retry import retry

class Chatbot:
    def __init__(
        self,
        instructions=system_role,
        use_model=model.basic,
        conversation_id=None
    ):
        self.model = use_model
        self.instructions = instructions

        if conversation_id:
            # 기존 Conversation 재사용
            self.conversation_id = conversation_id
        else:
            # 새로운 Conversation 생성
            conversation = client.conversations.create()
            self.conversation_id = conversation.id

    @retry(tries=3, delay=2)
    def send_message(self, user_message):

        response = client.responses.create(
            model=self.model,

            # Conversation ID를 지정하면
            # 이전 대화 내용이 계속 누적됨
            conversation=self.conversation_id,

            # System Prompt
            instructions=self.instructions,

            # 사용자 메시지
            input=user_message
        )

        return response.output_text


if __name__ == "__main__":
    chatbot = Chatbot(use_model=model.basic)

    try:
        response_message = chatbot.send_message(
            "안녕 나는 안정운이야."
        )
        print(response_message)

        response_message = chatbot.send_message(
            "나는 수원에 살고 있어"
        )
        print(response_message)

        response_message = chatbot.send_message(
            "내가 누구지?"
        )
        print(response_message)
        print("=" * 50)

        # Conversation ID 확인
        print(f"conversation_id : {chatbot.conversation_id}")

    except Exception as e:
        print(f"conversation api error : {e}")