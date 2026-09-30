import sys
import json

from tool_calling import ToolCalling, tools_report
from common import client, model

# ToolCalling 객체 생성
tool_calling = ToolCalling(model=model.advanced)

# 보고서 작성 단계 계획
template = """
[{과제}]를 해결하기 위해 해야 할 일을 2단계로 아래 JSON 포맷으로 말하세요.
사용할 수 있는 도구에는 "인터넷검색"과 "보고서작성"이 있습니다.

반드시 다음 JSON 형식으로만 응답하세요.

{{
    "step-1": "<1단계 할일>",
    "step-2": "<2단계 할일>"
}}
"""

# 1. 보고서 작성 작업을 2단계로 분리
def create_step_plan(message):
    response = client.responses.create(
        model=model.advanced,
        input=[{"role": "user","content": message}],
        # JSON 형태로 출력
        text={
            "format": {
                "type": "json_object"
            }
        }
    )

    return json.loads(response.output_text)

# 2. 사용자 과제
print("sys.argv[1]", sys.argv[1])
steps = create_step_plan(template.format(과제=sys.argv[1]))

# 3. 단계별 Tool Calling 실행
response_message = ""

for step in steps.values():
    print("step:", step)
    user_message = f"{step}:\n{response_message}"
    # Responses API로 사용자 요청 분석
    analyzed = tool_calling.analyze(user_message,tools_report)
    # function_call 찾기
    function_calls = [item for item in analyzed.output if item.type == "function_call"]
    # 함수 호출이 있는 경우
    if function_calls:
        response_message = tool_calling.call_function(analyzed)

# 4. 최종 결과
print(f"최종결과:\n{response_message}")