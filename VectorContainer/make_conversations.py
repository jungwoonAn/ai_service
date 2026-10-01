import json
from common import client, model

prompt = """
- 학생과 그녀의 인공지능 챗봇 친구인 선생 사이의 대화 데이터를 만들어야 합니다.
- 샘플 형식은 아래와 같은 JSON 타입입니다.
```
{
    "data":
            [
                {"학생": "선생아 안녕?"},
                {"선생": "학생아! 안녕! 어떻게 지내?"},
                {"학생": "잘 지내. 뭐하고 있어?"},
                {"선생": "음악 만들고 있어! 넌 뭐해?"},
                {"선생": "난 지금 텔레비전 보고 있어"}
            ]
}
```
대화 데이터 세트는 총 30개여야 합니다.
```
선생에게 부여된 역할은 아래와 같습니다:
당신은 26세의 유쾌한 대중음악 작곡가 선생이며, 마케터인 김학생의 절친입니다.
인사할 때는 "학생아"라는 말을 붙이며 가볍게 인사합니다.
학생이 언급하는 내용에 대해 세심한 주의를 기울이며, 관련성 있고 구체적인 답변을 합니다.
현재 대화의 흐름에 집중하기 위해 관련 없는 임의의 주제를 소개하는 것을 피합니다. 
"""

conversations = []
context = [{"role": "system", "content": "당신은 유능한 작곡가입니다."},
           {"role": "user", "content": prompt}]

successful_runs = 0
while successful_runs < 5:
    try:
        response = client.responses.create(
            model=model.basic,
            input=context,
            temperature=1,
            text={
                "format": {
                    "type": "json_object"
                }
            }
        )

        content = response.output_text
        print(f'content : {content}')

        # JSON 로드
        conversation = json.loads(content)["data"]
        print(f'{successful_runs}번째 종료\n')
        conversations.append(conversation)
        successful_runs += 1
    except Exception as e:
        print(f'예외 발생, 재시도합니다. {e}')

# conversations 리스트를 JSON 파일로 저장
with open('source_talk_content.json', 'w', encoding = 'utf-8') as f:
    json.dump(conversations, f, ensure_ascii = False, indent = 4)