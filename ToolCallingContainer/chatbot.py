import math

from common import model, client, gpt_num_tokens, makeup_response

class Chatbot:
    def __init__(self, system_role, instruction, use_model=model.basic):
        # context 초기화 및 대화 문맥 생성
        self.model = use_model
        self.context = [
            {"role": "system", "content": system_role}
        ]
        self.instruction = instruction  # 지시 추가
        self.max_token_size = 16 * 1024  # 최대 token 수

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

    # 사용자 메시지를 context에 추가
    def add_user_message(self, message):
        self.context.append(
            {"role": "user", "content": message}
        )

    # context 전체를 OpenAI API로 전송
    def _send_request(self):  # _ : 내장 메서드(외부에서 접근 불가)
        try:
            # 현재 context의 max_token 크기를 벗어날 때 처리
            if gpt_num_tokens(self.context) > self.max_token_size:
                self.context.pop()
                return makeup_response('메시지를 조금 짧게 보내 줄래?')

            response = client.responses.create(
                model=self.model,
                input=self.context,
                temperature=0.5,
                top_p=1,
                max_output_tokens=256
            )
            return response

        except Exception as e:
            print(f'Exception 오류({type(e)}) 발생 : {e}')

    # api 요청전에 context 마지막에 instruction 추가
    def send_request(self):
        if self.context and self.context[-1]["role"] == "user":
            self.context[-1]["content"] += self.instruction

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
        response_text = response.output_text
        self.context.append(
            {"role": "assistant", "content": response_text}
        )

    # 응답 내용을 출력하고 반환
    def get_response(self, response):
        response_text = response.output_text
        # print(response_text)
        return response_text