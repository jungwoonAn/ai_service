import os
from datetime import datetime

from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

pinecone = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pinecone.index('test-index')

# print(type(index))
# print(hasattr(index, "documents"))

text1 = """
신데렐라는 어려서 부모님을 잃고 불친절한 새어머니와 언니들과 삽니다. 요정 대모님의 마법으로 왕자님
의 무도회에 참석합니다. 밤 12시가 되면 마법이 풀린다는 조건 하에 왕자님과 춤을 추고, 서둘러 도망
치면서 유리구두 하나를 잃습니다. 왕자님은 유리구두를 가지고 신데렐라를 찾아 결혼하게 됩니다.
"""

text2 = """
컴퓨터 구조는 CPU, 메모리, 입출력 장치 등으로 구성되며, 이들은 버스로 연결됩니다. CPU는 명령어
를 실행하고, 메모리는 데이터와 프로그램을 저장합니다. 입출력 장치는 사용자와 시스템 간의 상호작
용을 담당합니다. 이 구성 요소들은 소프트웨어와 하드웨어의 효율적인 동작을 위해 설계되었습니다.
"""

# Pinecone index에 vector 저장
# index.documents.upsert(
#     namespace="test-index",
#     documents=[
#         {
#             "_id" : "id1",
#             "values": text1,
#             "input_date": datetime.now().strftime("%Y%m%d")
#         },
#         {
#             "_id" : "id2",
#             "values": text2,
#             "input_date": datetime.now().strftime("%Y%m%d")
#         }
#     ]
# )

query = """
이 내용은 컴퓨터 과학이나 IT 기술에 관한 기술 문서입니다.
컴퓨터 구조, CPU, 메모리, 하드웨어, 소프트웨어 등의 기술적인 내용을
설명하는 문서입니다.
"""

# top_k : 유사도가 높은 순으로 몇 개를 결과로 도출할지에 대한 인수
search_result = index.documents.search(
    namespace="test-index",
    score_by=[
        {
            "type": "embed",
            "field": "values",
            "query": query
        }
    ],
    top_k=2
)

print(f'search result = {search_result}')

for match in search_result.matches:
    print(match.id, match.score)