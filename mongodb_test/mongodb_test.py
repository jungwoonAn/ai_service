import os
from dotenv import load_dotenv

from pymongo import MongoClient

load_dotenv()

uri = os.getenv('MONGO_CLUSTER_URI')

cluster = MongoClient(uri)  # cluster 접속
db = cluster['chatbot']  # cluster DB 이름 사용
collection = db['chats']  # collection 이름사용

my_friend = {
    "name": "선생",
    "age": 26,
    "job": "IT 강의",
    "character": "당신은 진지한 것을 싫어하며, 항상 밝고 명랑한 성격임",
    "best friend": { "name": "학생",
                     "situations": [ "회사 생활에 의욕을 찾지 못하고 창업을 준비하고 있음",
                                     "매운 음식을 좋아함",
                                     "가장 좋아하는 가수는 '아이유'" ]
                    }
}

# 하나의 document(레코드) 추가
# collection.insert_one(my_friend)

# 모든 document 삭제
collection.delete_many({})

# collection에 있는 모든 내용 읽기
for result in collection.find({}):
    print(result)