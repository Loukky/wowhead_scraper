#!/usr/bin/env python3
"""Fetch raw HTML from wowhead and analyze structure for parsing."""
import subprocess
import re
import json

def fetch(url: str) -> str:
    result = subprocess.run(
        ["curl", "-sL", "--max-time", "15", url],
        capture_output=True, text=True, timeout=20
    )
    return result.stdout

def analyze(url: str, label: str):
    print(f"\n{'='*60}")
    print(f"ANALYZING: {label}")
    print(f"{'='*60}")
    print(f"URL: {url}")
    
    html = fetch(url)
    print(f"HTML size: {len(html)} bytes")
    
    # 1. Check for block-block-bg
    count = html.count('block-block-bg')
    print(f"\n1. 'block-block-bg' occurrences: {count}")
    
    # 2. Check for is-btf
    count2 = html.count('is-btf')
    print(f"2. 'is-btf' occurrences: {count2}")
    
    # 3. Find div.text
    m = re.search(r'<div class="text">', html)
    if m:
        print(f"3. div.text found at position {m.start()}")
        # Extract the div.text block
        # Count opening/closing divs to find the matching closing tag
        start = m.start()
        depth = 0
        end = start
        i = start
        in_tag = False
        while i < len(html):
            if html[i:i+4] == '<div':
                depth += 1
                i += 4
            elif html[i:i+6] == '</div>':
                depth -= 1
                if depth == 0:
                    end = i + 6
                    break
                i += 6
            else:
                i += 1
        text_block = html[start:end]
        print(f"   div.text block length: {len(text_block)}")
        
        # Show element structure
        elements = re.findall(r'<(h[12]|div|table|br|script|span|ul|a)[^>]*>', text_block, re.IGNORECASE)
        print(f"   Element sequence: {' → '.join(elements[:30])}…" if len(elements) > 30 else f"   Element sequence: {' → '.join(elements)}")
        
        # Show children with class names
        print("\n   Children of div.text:")
        child_pattern = re.compile(r'<(h[12]|div|table|br|p|span|ul|a|script)([^>]*)>', re.IGNORECASE)
        for idx, c in enumerate(child_pattern.finditer(text_block)):
            tag = c.group(1)
            attrs = c.group(2)
            # class extraction
            cls_m = re.search(r'class="([^"]*)"', attrs)
            cls = cls_m.group(1) if cls_m else ''
            # Get text content roughly
            tag_end = f'</{tag}>' if tag not in ('br',) else ''
            content_m = re.search(re.escape(c.group(0)) + r'(.*?)', re.escape(tag_end), re.DOTALL) if tag_end else None
            # Print just the tag info
            cinfo = f"<{tag}" + (f' class="{cls}"' if cls else '')
            print(f"   [{idx:2d}] {cinfo}")
            if idx > 35:
                print(f"   ... and more ({len(elements) - idx - 1} more)")
                break
    else:
        print("3. No div.text found!")
    
    # 4. Find description/objective related sections
    for search in ["objective", "Objective", "description", "Description", "描述", "block-block-bg", "is-btf", "icon-list"]:
        m = re.search(search, html, re.IGNORECASE)
        if m:
            ctx = html[max(0,m.start()-100):m.end()+100]
            print(f"\n4. '{search}' found at {m.start()}: ...{ctx.strip()}...")
    
    print()

# Test pages
analyze("https://www.wowhead.com/mop-classic/quest=1/", "EN - mop-classic quest=1")
analyze("https://www.wowhead.com/mop-classic/cn/quest=1/", "CN - mop-classic quest=1")

# Also test a wotlk/cn page (which the user said works previously)
analyze("https://www.wowhead.com/wotlk/cn/quest=1/", "CN - wotlk quest=1")
