# common.py
import os
from dotenv import load_dotenv
from dataclasses import dataclass

from openai import OpenAI

# 환경 변수 로드
load_dotenv()


# 자동으로 초기화 속성으로 사용, 외부 수정 방지
@dataclass(frozen=True)
class Model:
    basic: str = "gpt-4o-mini-2024-07-18"
    advanced: str = "gpt-5-mini-2025-08-07"

model = Model()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), timeout=30, max_retries=1)