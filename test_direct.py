import requests

query = "machine learning"
url = "https://en.wikipedia.org/w/api.php"
params = {
    "action": "opensearch",
    "search": query,
    "limit": 3,
    "format": "json"
}

headers = {
    "User-Agent": "KnowledgeRAG/1.0 (https://github.com/skepee-PROTOTYPE/knowledge-rag; educational project)"
}

print(f"Searching for: {query}")
response = requests.get(url, params=params, headers=headers, timeout=10)
print(f"Status: {response.status_code}")
data = response.json()
print(f"Data: {data}")
titles = data[1] if len(data) > 1 else []
print(f"Titles: {titles}")
