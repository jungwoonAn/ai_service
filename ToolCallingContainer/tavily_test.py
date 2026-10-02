import os
from dotenv import load_dotenv

from tavily import TavilyClient
from pprint import pprint

load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
response = tavily.search(query='ChatGPT Function calling이란?',
                         search_depth='advanced')

pprint(len(response['results']))