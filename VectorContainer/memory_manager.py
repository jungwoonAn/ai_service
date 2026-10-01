import os
from dotenv import load_dotenv
from pymongo import MongoClient

from common import client, model, today, yesterday, currTime
from pinecone.grpc import PineconeGRPC as Pinecone
import json

load_dotenv()

# MongoDB
mongo_cluster = MongoClient(os.getenv("MONGO_CLUSTER_URI"))
mongo_chats_collection = mongo_cluster["chatbot"]["chats"]
mongo_memory_collection = mongo_cluster["chatbot"]["memory"]

# Pinecone
pinecone = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
pinecone_index = pinecone.Index('chatbot-memory')

# Embedding
embedding_model = "text-embedding-3-small"

# 아래 사용자 질의가 오늘 이전의 기억에 대해 묻는 것인지 참/거짓으로만 응답하세요.
NEEDS_MEMORY_TEMPLATE = """
Answer only true/false if the user query below asks about memories before today.
```
{message}
"""

# statement1은 기억에 대한 질문입니다.
# statement2는 학생과 선생이 공유하는 기억입니다.
# statment2는 statement1에 대한 기억으로 적절한지 아래 json 포맷으로 답하세요
# {"0과 1 사이의 확률": <확률값>}
MEASURING_SIMILARITY_SYSTEM_ROLE = """
statement1 is a question about memory.
statement2 is a memory shared by '학생' and '선생'.
Answer whether statement2 is appropriate as a memory for statement1 in the following JSON format
{"probability": <between 0 and 1>}
"""

SUMMARIZING_TEMPLATE = """
당신은 사용자의 메시지를 아래의 JSON 형식으로 대화 내용을 주제별로 요약하는 기계입니다.
1. 주제는 구체적이며 의미가 있는 것이어야 합니다.
2. 요약 내용에는 '학생아...', '선생아...'처럼 대화자의 이름이 들어가야 합니다.
3. 원문을 최대한 유지하며 요약해야 합니다. 
4. 주제의 갯수는 무조건 5개를 넘지 말아야 하며 비슷한 내용은 하나로 묶어야 합니다.
```
{
    "data":
            [
                {"주제":<주제>, "요약":<요약>},
                {"주제":<주제>, "요약":<요약>},
            ]
}
"""

class MemoryManager:
    """
    사용자와 AI의 대화 내용을 저장하고,
    특정 시점의 대화를 요약하여 벡터 DB와 MongoDB에 기억으로 저장하고,
    필요한 경우 기억을 불러오는 역할을 하는 클래스
    """

    def __init__(self, **kwargs):
        self.user = kwargs['user']
        self.assistant = kwargs['assistant']

    # 새로운 대화 내용을 MongoDB에 저장
    def save_chat(self, context):
        messages = []

        for message in context:
            if message.get("saved", True):
                continue
            messages.append({
                "date": today(),
                "role": message["role"],
                "content": message["content"]
            })

        if len(messages) > 0:
            mongo_chats_collection.insert_many(messages)

    # 특정 날짜의 대화를 불러옴
    def restore_chat(self, date=None):
        search_date = date if date is not None else today()
        search_results = mongo_chats_collection.find({"date": search_date})
        restored_chat = [
            {"role": v['role'], "content": v['content'], "saved": True} for v in search_results
        ]

        print(f'\n{restored_chat}\n')
        return restored_chat

    # 현재 질문이 과거 기억을 요구하는지 판단(True/False)
    def needs_memory(self, message):
        context = [
            {"role": "user", "content": NEEDS_MEMORY_TEMPLATE.format(message=message)}
        ]
        try:
            response = client.responses.create(
                model=model.advanced,
                input=context,
                temperature=0
            )

            content = response.output_text.strip()
            print(f"needs_memory : {content}")
            return content.upper() == "TRUE"

        except Exception as e:
            print(f"needs_memory error : {e}")
            return False

    # 특정 요약 ID로 MongoDB에서 기억 검색
    def search_mongo_db(self, _id):
        search_result = mongo_memory_collection.find_one({"_id": int(_id)})
        print(f'search_result : {search_result}')

        return search_result['summary']

    # 사용자의 질문과 가장 유사한 기억을 벡터 DB에서 검색
    def search_vector_db(self, message):
        # 사용자 질문을 임베딩
        query_vector = client.embeddings.create(input=message, model=embedding_model).data[0].embedding
        # pinecone 검색
        results = pinecone_index.query(
            top_k=1,
            vector=query_vector,
            include_metadata=True
        )

        # 검색 결과가 없는 경우
        if not results["matches"]:
            return None

        vector_id = results["matches"][0]["id"]
        score = results["matches"][0]["score"]
        print(f"id : {vector_id}\tscore : {score}")

        # 유사도가 0.7 이상인 경우에만 id값을 mongoDB에 인수로 전달
        return vector_id if score > 0.7 else None

    # 사용자의 질문에 대해 적절한 기억을 DB에서 검색하고, 필터링 후 반환
    def retrieve_memory(self, message):
        vector_id = self.search_vector_db(message)
        if not vector_id:
            return None

        memory = self.search_mongo_db(vector_id)
        if self.filter(message, memory):
            return memory
        else:
            return None

    # 기억이 질문과 충분히 유사한지 판단 (확률 기반)
    def filter(self, message, memory, threshhold=0.6):
        context = [
            {"role": "system", "content": MEASURING_SIMILARITY_SYSTEM_ROLE},
            {
                "role": "user",
                "content": json.dumps({
                    "statement1": f"학생:{message}",
                    "statement2": memory
                }, ensure_ascii=False)
            }
        ]

        try:
            response = client.responses.create(
                model=model.advanced,
                input=context,
                temperature=0,
                text={
                    "format": {
                        "type": "json_object"
                    }
                }
            )

            content = response.output_text
            prob = json.loads(content)["probability"]
            print(f"filter prob : {prob}")

        except Exception as e:
            print(f"filter error : {e}")
            prob = 0

        return prob >= threshhold

    # 어제 날짜의 대화를 기반으로 요약을 생성하고, DB에 저장
    def build_memory(self):
        date = yesterday()
        memory_results = mongo_memory_collection.find({"date": date})

        if len(list(memory_results)) > 0:
            return

        chats_results = self.restore_chat(date)

        if len(list(chats_results)) == 0:
            return

        summaries = self.summarize(chats_results)

        self.delete_by_date(date)
        self.save_to_memory(summaries, date)

    # 새로운 대화의 메시지 리스트를 주제별 요약으로 변환
    def summarize(self, messages):
        altered_messages = [
            {self.user if message['role'] == 'user' else self.assistant: message["content"]}
            for message in messages
        ]
        try:
            context = [
                {"role": "system", "content": SUMMARIZING_TEMPLATE},
                {
                    "role": "user",
                    "content": json.dumps(altered_messages, ensure_ascii=False),
                },
            ]
            response = client.responses.create(
                model=model.basic,
                input=context,
                temperature=0,
                text={
                    "format": {
                        "type": "json_object"
                    }
                }
            )

            content = response.output_text
            return json.loads(content)["data"]

        except Exception as e:
            print(f"summarize error : {e}")
            return []

    # 특정 날짜의 기억을 벡터 DB와 MongoDB에서 모두 삭제
    def delete_by_date(self, date):
        search_results = mongo_memory_collection.find({"date": date})
        ids = [str(v['_id']) for v in search_results]
        if len(ids) == 0:
            return

        # Pinecone 삭제
        pinecone_index.delete(ids=ids)
        # MongoDB 삭제
        mongo_memory_collection.delete_many({"date": date})

    # 요약 데이터를 MongoDB 및 Pinecone에 저장
    def save_to_memory(self, summaries, date):
        next_id = self.next_memory_id()
        for summary in summaries:
            # 요약 내용을 벡터로 변환
            vector = (
                client.embeddings.create(
                    input=summary["요약"],
                    model=embedding_model
                ).data[0].embedding
            )
            # Pinecone metadata
            metadata = {"date": date, "keyword": summary["주제"]}
            # Pinecone 저장
            pinecone_index.upsert([(str(next_id), vector, metadata)])

            # MongoDB 저장
            query = {"_id": next_id}  # 조회조건
            newvalues = {
                "$set": {
                    "date": date,
                    "keyword": summary["주제"],
                    "summary": summary["요약"],
                }
            }
            mongo_memory_collection.update_one(query, newvalues, upsert=True)
            next_id += 1

    # 메모리에 저장할 다음 ID 생성
    def next_memory_id(self):
        result = mongo_memory_collection.find_one(sort=[("_id", -1)])
        return 1 if result is None else result["_id"] + 1