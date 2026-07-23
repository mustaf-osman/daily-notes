import re

with open(r'C:\Users\20392\daily-notes\trending_page.txt', 'r', encoding='utf-8') as f:
    html = f.read()

# Find all article Box-row blocks
articles = re.findall(r'<article[^>]*class="Box-row"[^>]*>(.*?)</article>', html, re.DOTALL)
print(f"Found {len(articles)} trending repos")

results = []
for a in articles:
    # Repo name
    name_m = re.search(r'href="/([^"/]+/[^"/]+?)"', a)
    if not name_m:
        continue
    name = name_m.group(1)
    
    # Description
    desc_m = re.search(r'<p[^>]*class="[^"]*col-9[^"]*"[^>]*>(.*?)</p>', a, re.DOTALL)
    if not desc_m:
        desc_m = re.search(r'<p[^>]*>(.*?)</p>', a, re.DOTALL)
    desc = ""
    if desc_m:
        desc = re.sub(r'<[^>]+>', '', desc_m.group(1)).strip()
        desc = desc.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&#39;', "'").replace('&quot;', '"')
    
    # Stars today
    stars_m = re.search(r'([\d,]+)\s*stars today', a)
    stars = stars_m.group(1) if stars_m else "?"
    
    # Language
    lang_m = re.search(r'itemprop="programmingLanguage"[^>]*>([^<]+)<', a)
    lang = lang_m.group(1).strip() if lang_m else ""
    
    results.append((name, desc, stars, lang))
    print(f"{name} | {desc[:100] if desc else 'No description'} | ★{stars} today | {lang}")

print("\n--- SUMMARY ---")
for r in results:
    print(f"- [{r[0]}](https://github.com/{r[0]}) — {r[1][:120] if r[1] else 'No description'} [{r[2]} stars today]")
