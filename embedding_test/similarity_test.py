# similarity_test.py
# 유사도
import os
from dotenv import load_dotenv
import scipy.spatial.distance as ssd

from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

category1 = """
이 내용은 동화나 소설과 같은 문학 작품에 관한 이야기입니다.
등장인물, 사건, 이야기의 전개 등이 중심이 되는 문학적인 내용입니다.
"""


category2 = """
이 내용은 컴퓨터 과학이나 IT 기술에 관한 기술 문서입니다.
컴퓨터 구조, CPU, 메모리, 하드웨어, 소프트웨어 등의 기술적인 내용을
설명하는 문서입니다.
"""

embedding_model = 'text-embedding-3-small'

text1_vector = client.embeddings.create(input=text1, model=embedding_model).data[0].embedding
text2_vector = client.embeddings.create(input=text2, model=embedding_model).data[0].embedding

category1_vector = client.embeddings.create(input=category1, model=embedding_model).data[0].embedding
category2_vector = client.embeddings.create(input=category2, model=embedding_model).data[0].embedding

print(f'신데렐라 이야기 - 문학 작품 : {1 - ssd.cosine(text1_vector, word1_vector)}')
print(f'컴퓨터 구조 설명 - 기술 문서 : {1 - ssd.cosine(text2_vector, word2_vector)}\n')
print(f'신데렐라 이야기 - 기술 문서 : {1 - ssd.cosine(text1_vector, word2_vector)}')
print(f'컴퓨터 구조 설명 - 문학 작품 : {1 - ssd.cosine(text2_vector, word1_vector)}')