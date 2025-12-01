import requests

# 注册免费 API: https://developer.nytimes.com/
API_KEY = "your_key"
url = f"https://api.nytimes.com/svc/search/v2/articlesearch.json"
params = {
    "q": "AI Chinese talent",
    "api-key": API_KEY
}

response = requests.get(url, params=params)
articles = response.json()['response']['docs']

for article in articles:
    print(article['headline']['main'])
    print(article['web_url'])