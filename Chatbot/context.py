# context.py
import os
from dotenv import load_dotenv

from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

response = client.responses.create(
    model='gpt-4o-mini',
    input=[
        {'role': 'system', 'content': 'You are a helpful assistant.'},
        {'role': 'user', 'content': 'Who won the world series in 2020?'}
    ]
)

print(f'first answer : {response.output_text}')

response_content = response.output_text

response = client.responses.create(
    model='gpt-4o-mini',
    input=[
        {'role': 'system', 'content': 'You are a helpful assistant.'},
        {'role': 'user', 'content': 'Who won the world series in 2020?'},
        {'role': 'assistant', 'content': response_content},
        {'role': 'user', 'content': 'Where was it player?'},
    ]
)

print(f'\nsecond answer : {response.output_text}')