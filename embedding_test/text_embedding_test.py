# text_embedding_test.py
# text-embedding-3-small embedding model test
import os
from dotenv import load_dotenv

from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

message = '신데렐라와 왕자는 사랑에 빠졌습니다.'
result = client.embeddings.create(input=message, model='text-embedding-3-small').model_dump()
print(result)