# main.py
from chatbot import Chatbot


chatbot = Chatbot()

# 첫 번째 질문
chatbot.add_user_message(
    "Who won the world series in 2020?"
)

response = chatbot.send_request()
chatbot.add_response(response)
chatbot.get_response(response)

# 두 번째 질문
chatbot.add_user_message(
    "Where was it played?"
)

print("\n현재 context:")
print(chatbot.context)