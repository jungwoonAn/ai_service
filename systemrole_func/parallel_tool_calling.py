from common import client, model, makeup_response 
import json
import requests
from pprint import pprint 
from tavily import TavilyClient
import os

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

#위도/경도
global_lat_lon = { 
    '서울':[37.57,126.98],'강원도':[37.86,128.31],'경기도':[37.44,127.55],
    '경상남도':[35.44,128.24],'경상북도':[36.63,128.96],'광주':[35.16,126.85],
    '대구':[35.87,128.60],'대전':[36.35,127.38],'부산':[35.18,129.08],
    '세종시':[36.48,127.29],'울산':[35.54,129.31],'전라남도':[34.90,126.96],
    '전라북도':[35.69,127.24],'제주도':[33.43,126.58],'충청남도':[36.62,126.85],
    '충청북도':[36.79,127.66],'인천':[37.46,126.71],
    'Boston':[42.36, -71.05],
    '도쿄':[35.68, 139.69]
}

#화폐 코드
global_currency_code = {'달러':'USD','엔화':'JPY','유로화':'EUR','위안화':'CNY','파운드':'GBP'}

# 날씨 조회 함수
def get_celsius_temperature(**kwargs):
    location = kwargs['location']
    lat_lon = global_lat_lon.get(location, None)
    if lat_lon is None:
        return None
    lat = lat_lon[0]
    lon = lat_lon[1]

    # API endpoint
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"

    # API를 호출하여 데이터 가져오기
    response = requests.get(url)
    # 응답을 JSON 형태로 변환
    data = response.json()
    # 현재 온도 가져오기 (섭씨)
    temperature = data['current_weather']['temperature']

    print("temperature:",temperature) 
    return temperature

# 환율 조회 함수
def get_currency(**kwargs):
    currency_name = kwargs['currency_name']
    currency_name = currency_name.replace("환율", "")
    currency_code = global_currency_code.get(currency_name)
    
    if currency_code is None:
        return None

    response = requests.get(
        f"https://api.exchangerate-api.com/v4/latest/{currency_code}",
        timeout = 10
    )
    data = response.json()
    krw = data['rates']['KRW']

    print("환율:", krw) 
    return krw

# 인터넷 검색 함수
def search_internet(**kwargs):
    print("search_internet",kwargs)
    answer = tavily.search(query=kwargs['search_query'], include_answer=True)['answer']
    print("answer",answer)
    return answer

# Responses API용 tools
tools = [
    {
        "type": "function",
        "name": "get_celsius_temperature",
        "description": "지정된 위치의 현재 섭씨 날씨 확인",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "광역시도, e.g. 서울, 경기"
                }
            },
            "required": ["location"]
        }
    },
    {
        "type": "function",
        "name": "get_currency",
        "description": "지정된 통화의 원(KRW) 기준의 환율 확인.",
        "parameters": {
            "type": "object",
            "properties": {
                "currency_name": {
                    "type": "string",
                    "description": "통화명, e.g. 달러환율, 엔화환율"
                }
            },
            "required": ["currency_name"]
        }
    },
    {
        "type": "function",
        "name": "search_internet",
        "description": "답변 시 인터넷 검색이 필요하다고 판단되는 경우 수행",
        "parameters": {
            "type": "object",
            "properties": {
                "search_query": {
                    "type": "string",
                    "description": "인터넷 검색을 위한 검색어"
                }
            },
            "required": ["search_query"]
        }
    }
]

# ToolCalling
class ToolCalling:
    def __init__(self, model):
        self.available_functions = {
            "get_celsius_temperature": get_celsius_temperature,
            "get_currency": get_currency,
            "search_internet": search_internet,
        }
        self.model = model

    # 1. 사용자 메시지 분석
    def analyze(self, user_message, tools):
        try:
            response = client.responses.create(
                    model=self.model,
                    input=[{"role": "user", "content": user_message}],
                    tools=tools,
                    tool_choice="auto", 
                )
            print(("response =>", response))
            return response
        except Exception as e:
            print("Error occurred(analyze):",e)
            return makeup_response("[analyze 오류입니다]")

    def run(self, analyzed, context):
        try:
            # Responses API의 output에서 function_call 항목만 추출
            function_calls = [ item for item in analyzed.output if item.type == "function_call" ]

            # 함수 호출이 없는 경우
            if not function_calls:
                return analyzed

            # 모델이 요청한 모든 function_call을 context에 먼저 추가
            for tool_call in function_calls:
                context.append( tool_call.model_dump() )

            # 모든 함수 실행
            for tool_call in function_calls:
                func_name = tool_call.name
                func_to_call = self.available_functions[ func_name ]
                # JSON 문자열 → Python dictionary
                func_args = json.loads( tool_call.arguments )
                print( f"function: {func_name}, " f"arguments: {func_args}" )
                # 실제 Python 함수 호출
                func_response = func_to_call( **func_args )

                # 함수 실행 결과를 context에 추가
                context.append(
                    {
                        "type": "function_call_output",
                        "call_id": tool_call.call_id,
                        "output": str(func_response)
                    }
                )

            # 모든 함수 실행 결과를 포함하여 Responses API 다시 호출
            final_response = client.responses.create(
                model=self.model,
                input=context,
                tools=tools
            )
            return final_response
        except Exception as e:
            print("Error occurred(run):",e)
            return makeup_response("[run 오류입니다]")