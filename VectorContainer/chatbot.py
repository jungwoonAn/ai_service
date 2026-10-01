import math
import threading
import time

from common import model, client, gpt_num_tokens, makeup_response
from warning_agent import WarningAgent
from memory_manager import MemoryManager

class Chatbot:
    def __init__(self, system_role, instruction, use_model=model.basic, **kwargs):
        # context 초기화 및 대화 문맥 생성
        self.model = use_model
        self.context = [
            {"role": "system", "content": system_role}
        ]
        self.instruction = instruction  # 지시 추가
        self.max_token_size = 16 * 1024  # 최대 token 수
        # WarningAgent에 전달할 파라미터 추가
        self.kwargs = kwargs
        self.user = kwargs["user"]
        self.assistant = kwargs["assistant"]
        self.warningAgent = self._create_warning_agent()
        # 메모리 추가 및 DB저장
        self.memoryManager = MemoryManager(**kwargs)  # MemoryManager에 role 전달
        self.context.extend(self.memoryManager.restore_chat())

        # 데몬 백그라운드 스레드 실행
        bg_thread = threading.Thread(target=self.background_task)
        bg_thread.daemon = True
        bg_thread.start()

    def _create_warning_agent(self):
        return WarningAgent(
            model=self.model,
            user=self.user,
            assistant=self.assistant
        )

    # 누적 token 수가 임계점을 넘지 않도록 제어
    def handle_token_limit(self, response):
        try:
            if hasattr(response, "usage") and response.usage is not None:
                total_tokens = response.usage.total_tokens
            elif isinstance(response, dict):
                total_tokens = response.get("usage", {}).get("total_tokens", 0)
            else:
                total_tokens = 0

            if total_tokens > self.max_token_size:
                remove_size = math.ceil(len(self.context) / 10)
                # system message는 유지
                self.context = ([self.context[0]] + self.context[remove_size + 1:])
        except Exception as e:
            print(f'handle_token_limit exception : {e}')

    # openai로 전달할 context
    def to_openai_context(self):
        return [{"role": v["role"], "content": v["content"]} for v in self.context ]

    # 대화 내용 저장
    def save_chat(self):
        self.memoryManager.save_chat(self.context)
        # DB에 저장한 메시지는 저장 완료 처리
        for message in self.context:
            if message.get("saved", False) is False:
                message["saved"] = True

    # 사용자 메시지를 context에 추가
    def add_user_message(self, message):
        self.context.append(
            {"role": "user", "content": message, "saved": False}
        )

    # context 전체를 OpenAI API로 전송
    def _send_request(self):  # _ : 내장 메서드(외부에서 접근 불가)
        try:
            # saved 제외한 context의 max_token 크기를 벗어날 때 처리
            if gpt_num_tokens(self.to_openai_context()) > self.max_token_size:
                self.context.pop()
                return makeup_response('메시지를 조금 짧게 보내 줄래?')

            response = client.responses.create(
                model=self.model,
                input=self.to_openai_context(),  # saved 제외한 context 전달
                temperature=0.5,
                top_p=1,
                max_output_tokens=256
            )
            return response

        except Exception as e:
            print(f'Exception 오류({type(e)}) 발생 : {e}')

    def send_request(self):
        # 사용자의 질문에 대해 유사 기억을 DB에서 검색한 내용
        memory_instruction = self.retrieve_memory()
        # WarningAgent가 사용자의 마지막 대화를 검사
        if self.warningAgent.monitor_user(self.context):
            warning_message = self.warningAgent.warn_user()
            print(f"WarningAgent response: {warning_message}")
            return warning_message
        else:
            # 요청 전에 마지막 사용자 메시지에 instruction 추가
            # 과거 유사 기억을 instruction에 추가
            self.context[-1]["content"] += self.instruction  + (memory_instruction if memory_instruction else "")
            return self._send_request()

    # 답변 받은 후 context에서 instruction 삭제
    def clear_context(self):
        for idx in reversed(range(len(self.context))):
            if self.context[idx]["role"] == "user":
                content = self.context[idx]["content"]
                if "instruction:\n" in content:
                    self.context[idx]["content"] = content.split("instruction:\n")[0].strip()
                break

    # 응답 내용을 context에 추가
    def add_response(self, response):
        if hasattr(response, "output_text"):
            # 정상적인 Responses API Response 객체
            response_text = response.output_text
        elif isinstance(response, dict):
            # makeup_response()의 임의 응답
            response_text = response.get("output_text", "")
        elif isinstance(response, str):
            # WarningAgent의 경고 메시지
            response_text = response
        else:
            response_text = str(response)

        self.context.append({
            "role": "assistant",
            "content": response_text,
            "saved": False
        })

    # 응답 내용을 출력하고 반환
    def get_response(self, response):
        if hasattr(response, "output_text"):
            # 정상 Responses API 응답
            return response.output_text
        elif isinstance(response, dict):
            # makeup_response()
            return response.get("output_text", "")
        elif isinstance(response, str):
            # WarningAgent
            return response

        return str(response)

    # 유사 대화를 메모리에서 검색하여 귓속말로 사용자 메시지에 삽입
    def retrieve_memory(self):
        user_message = self.context[-1]['content']
        if not self.memoryManager.needs_memory(user_message):
            return ""

        memory = self.memoryManager.retrieve_memory(user_message)
        if memory is not None:
            whisper = (f"[귓속말]\n{self.assistant}야! 기억 속 대화 내용이야. 앞으로 이 내용을 참조하면서 답해 줘."
                       f"얼마 전에 나누었던 대화라는 점을 자연스럽게 말해 줘.\n{memory}")
            return whisper

        return "[기억이 안 난다고 답할 것]"

    # 주기적으로 context를 저장하고 memory 구축하는 백그라운드 태스크
    def background_task(self):
        while True:
            self.save_chat()
            self.context = [{"role": v['role'], "content": v['content'], "saved": True} for v in self.context]
            self.memoryManager.build_memory()
            # time.sleep( 3600 )  # 1시간마다 반복
            time.sleep(120)  # test