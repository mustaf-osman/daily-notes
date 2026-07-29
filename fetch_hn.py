import json, urllib.request, sys

# Get top story IDs
resp = urllib.request.urlopen("https://hacker-news.firebaseio.com/v0/topstories.json")
ids = json.loads(resp.read())[:10]

for sid in ids:
    url = f"https://hacker-news.firebaseio.com/v0/item/{sid}.json"
    resp = urllib.request.urlopen(url)
    d = json.loads(resp.read())
    title = d.get('title', '')
    link = d.get('url', f"https://news.ycombinator.com/item?id={d.get('id','')}")
    print(f"{title}|||{link}")
