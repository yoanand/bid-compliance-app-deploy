import PyPDF2
import json
from strands import tool,Agent
import re
import pdfplumber
import json

import os

import requests
import os

@tool
def fetch_real_time_news(query: str, num_results: int = 10):
    """
    Fetches real-time news using Google Custom Search API.

    Args:
        query (str): The search query.
        num_results (int): Number of results to fetch.

    Returns:
        list: List of dictionaries with title, link, and snippet.
    """
    api_key = os.getenv("CUSTOM_SEARCH_API_KEY")
    cse_id = os.getenv("CUSTOM_SEARCH_ENGINE_ID")
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "key": api_key,
        "cx": cse_id,
        "num": num_results
    }
    response = requests.get(url, params=params)
    data = response.json()
    results = []
    for item in data.get("items", []):
        results.append({
            "title": item.get("title"),
            "link": item.get("link"),
            "snippet": item.get("snippet")
        })
    return results

# Example usage:
# news_results = fetch_real_time_news("latest geopolitical news which can impact product supply chain", num_results=5)
# print(json.dumps(news_results, indent=2, ensure_ascii=False))


agent = Agent(tools=[fetch_real_time_news])
