from common import client, model
from characters import system_role
from pprint import pprint

# Conversation 생성(Assistants API의 Thread 역할)
conversation = client.conversations.create()

print("conversation created")
# Conversation 객체 내용 확인
pprint(conversation.model_dump())
print("=" * 50)

# 사용자 메시지 전송 및 응답 생성
# Responses API를 사용하여 응답 요청, conversation.id를 지정하면 대화가 누적됨
response = client.responses.create(
    model=model.basic,
    conversation=conversation.id,
    instructions=system_role,
    input="선생아 반가워! 잘 지냈지?"
)

print("assistant response")
# 생성된 답변 텍스트 출력
print(response.output_text)
print("=" * 50)

# Conversation 안에 저장된 모든 항목 조회
items = list(
    client.conversations.items.list(
        conversation_id=conversation.id
    )
)

pprint(items)