# common.py
import os
from dotenv import load_dotenv
from dataclasses import dataclass
import tiktoken
import pytz
from datetime import datetime, timedelta

from openai import OpenAI

# 환경 변수 로드
load_dotenv()

# 자동으로 초기화 속성으로 사용, 외부 수정 방지
@dataclass(frozen=True)
class Model:
    basic: str = "gpt-4o-mini-2024-07-18"
    advanced: str = "gpt-5-mini-2025-08-07"

model = Model()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), timeout = 30, max_retries = 1 )

# 한 번에 너무 많은 메시지가 API를 통해 전송되는 것을 막기 위해
# token 양을 체크한 후 임계점을 넘어가면 예외처리
# Responses API용 임의 응답 생성
def makeup_response(message, status="ERROR"):
    """
    Responses API의 Response 객체와 유사한
    dictionary 형태의 임의 응답을 생성한다.

    정상적인 OpenAI Response 객체가 아니라
    오류 발생 시 프로그램 흐름을 유지하기 위한 용도이다.
    """
    return {
        "id": "error-response",
        "object": "response",
        "status": status,
        "output": [
            {
                "type": "message",
                "role": "assistant",
                "content": [
                    {
                        "type": "output_text",
                        "text": message
                    }
                ]
            }
        ],
        "output_text": message,
        "usage": {
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0
        }
    }


# Responses API input 토큰 수 계산
def gpt_num_tokens(messages, model="gpt-4o-mini"):
    """
    Responses API에 전달할 input/context의
    문자열 기반 예상 토큰 수를 계산한다.

    messages에는 일반적인 message뿐 아니라
    function_call, function_call_output 등의
    Responses API 항목도 들어올 수 있다.
    """
    encoding = tiktoken.encoding_for_model(model)
    num_tokens = 0

    for item in messages:
        # dictionary인 경우
        if isinstance(item, dict):
            for key, value in item.items():
                # 문자열은 그대로 토큰 계산
                if isinstance(value, str):
                    num_tokens += len(encoding.encode(value))
                # list / dict 등은 문자열로 변환하여 계산
                elif value is not None:
                    try:
                        num_tokens += len(encoding.encode(str(value)))
                    except Exception as e:
                        print(f"[gpt_num_tokens] 인코딩 실패: {key}={value} / 오류: {e}")
        # 문자열인 경우
        elif isinstance(item, str):
            num_tokens += len(encoding.encode(item))
        # 그 외 객체
        else:
            try:
                num_tokens += len(encoding.encode(str(item)))
            except Exception as e:
                print(f"[gpt_num_tokens] 인코딩 실패: {item} / 오류: {e}")

    return num_tokens

def today():
    korea = pytz.timezone('Asia/Seoul')  # 한국 시간대를 얻습니다.
    now = datetime.now(korea)  # 현재 시각을 얻습니다.
    return(now.strftime("%Y%m%d"))  # 시각을 원하는 형식의 문자열로 변환합니다.

def yesterday():    
    korea = pytz.timezone('Asia/Seoul')  # 한국 시간대를 얻습니다.
    now = datetime.now(korea)  # 현재 시각을 얻습니다.
    one_day = timedelta(days=1)  # 하루 (1일)를 나타내는 timedelta 객체를 생성합니다.
    yesterday = now - one_day  # 현재 날짜에서 하루를 빼서 어제의 날짜를 구합니다.
    return yesterday.strftime('%Y%m%d')  # 어제의 날짜를 yyyymmdd 형식으로 변환합니다.

def currTime():
    # 한국 시간대를 얻습니다.
    korea = pytz.timezone('Asia/Seoul')
    # 현재 시각을 얻습니다.
    now = datetime.now(korea)
    # 시각을 원하는 형식의 문자열로 변환합니다.
    formatted_now = now.strftime("%Y.%m.%d %H:%M:%S")
    return(formatted_now)