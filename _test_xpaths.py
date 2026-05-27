#!/usr/bin/env python3
"""Test XPath expressions on wowhead pages - using basic HTML parsing."""
import subprocess, re

def fetch(url):
    r = subprocess.run(["curl", "-sL", "--max-time", "15", url],
                       capture_output=True, text=True, timeout=20)
    return r.stdout

def find_in_html(html, tag, attrs=None, strict=False):
    """Check if a specific tag+class exists in the raw HTML."""
    if attrs:
        # Check for exact class match
        for cls in attrs.get("class", "").split():
            if cls and cls in html:
                pattern = f'<{tag}[^>]*class="[^"]*{re.escape(cls)}[^"]*"'
                if re.search(pattern, html, re.IGNORECASE):
                    return True
        return False
    return f"<{tag}" in html

def extract_h1_text(html):
    """Extract text from <h1 class='heading-size-1'>"""
    m = re.search(r'<h1[^>]*class="[^"]*heading-size-1[^"]*"[^>]*>(.*?)</h1>', html, re.DOTALL)
    if m:
        inner = m.group(1)
        # Strip inner HTML tags
        text = re.sub(r'<[^>]+>', '', inner).strip()
        return text[:100]
    return None

pages = [
    ("NPC EN", "https://www.wowhead.com/mop-classic/npc=20000/"),
    ("NPC CN", "https://www.wowhead.com/mop-classic/cn/npc=20000/"),
    ("Item EN", "https://www.wowhead.com/mop-classic/item=32615/"),
    ("Item CN", "https://www.wowhead.com/mop-classic/cn/item=32615/"),
    ("Object EN", "https://www.wowhead.com/mop-classic/object=10/"),
    ("Object CN", "https://www.wowhead.com/mop-classic/cn/object=10/"),
]

# Also test wotlk versions for comparison
pages2 = [
    ("NPC wotlk EN", "https://www.wowhead.com/wotlk/npc=20000/"),
    ("NPC wotlk CN", "https://www.wowhead.com/wotlk/cn/npc=20000/"),
    ("Item wotlk EN", "https://www.wowhead.com/wotlk/item=32615/"),
    ("Item wotlk CN", "https://www.wowhead.com/wotlk/cn/item=32615/"),
]

all_pages = pages + pages2

for label, url in all_pages:
    html = fetch(url)
    print(f"{'='*50}")
    print(f"{label}")
    print(f"{'='*50}")
    print(f"  URL: {url}")
    print(f"  Size: {len(html)} bytes")
    
    # Check h1 with heading-size-1
    h1 = extract_h1_text(html)
    print(f"  h1.heading-size-1: {'OK -> ' + h1 if h1 else 'FAIL - not found!'}")
    
    # Check for block-block-bg
    has_bbb = 'block-block-bg' in html
    print(f"  div.block-block-bg: {'FOUND (bad - could be stale)' if has_bbb else 'NOT PRESENT (new layout)'}")
    
    # Check for div.text
    has_dt = find_in_html(html, 'div', {'class': 'text'})
    print(f"  div.text: {'OK' if has_dt else 'MISSING!'}")
    print()
