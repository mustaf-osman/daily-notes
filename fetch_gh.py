import json, urllib.request, sys, html, re

# Try to scrape GitHub trending via the page
url = "https://github.com/trending"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
resp = urllib.request.urlopen(req)
html_content = resp.read().decode('utf-8')

# Find repo articles
# Look for h2 elements with repo names
pattern = r'<h2[^>]*class="[^"]*h3[^"]*"[^>]*>.*?href="/([^"]+)"[^>]*>([^<]+)</a>'
matches = re.findall(pattern, html_content, re.DOTALL)

for i, (repopath, name) in enumerate(matches[:10]):
    print(f"{repopath.strip()}|||https://github.com/{repopath.strip()}|||{name.strip()}")

if not matches:
    # Alternative: look for article tags with repos
    lines = html_content.split('\n')
    for i, line in enumerate(lines):
        if 'data-hpc' in line and 'class="Box"' in line:
            print(f"DEBUG: found Box at line {i}")
            # Print surrounding context
            for j in range(max(0,i-1), min(len(lines), i+30)):
                print(f"  {j}: {lines[j]}")
