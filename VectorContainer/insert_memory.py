import os
from dotenv import load_dotenv
from openai import OpenAI

from pinecone import Pinecone
from pymongo import MongoClient
import json

from common import today

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

mongo_cluster = MongoClient(os.getenv("MONGO_CLUSTER_URI"))
mongo_memory_collection = mongo_cluster['chatbot']['memory']

pinecone = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
pinecone_index = pinecone.index('chatbot-memory')

with open('summary_talk_content.json', 'r', encoding='utf-8') as f:
    summaries_list = json.load(f)

mongo_memory_collection.delete_many({})

next_id = 1
documents = []

for list_idx, summaries in enumerate(summaries_list):
    date = f"{today()}{list_idx + 1:02}"

    for summary in summaries:
        # Pinecone Documents API에 저장할 문서
        document = {
            "_id": str(next_id),
            "values": summary['요약'],
            "date": date,
            "keyword": summary["주제"]
        }
        documents.append(document)

        # MongoDB 저장
        query = {"_id": next_id}
        newvalues = {
            "$set": {
                "date": date,
                "keyword": summary['주제'],
                "summary": summary["요약"]
            }
        }
        mongo_memory_collection.update_one(query, newvalues, upsert=True)

        if (next_id) % 5 == 0:
            print(f'id : {next_id}')

        next_id += 1

# Pinecone Documents API로 일괄 저장
upsert_response = pinecone_index.documents.upsert(
    namespace="chatbot-memory",
    documents=documents
)

print(f"Pinecone 저장 완료: {upsert_response.upserted_count}개")