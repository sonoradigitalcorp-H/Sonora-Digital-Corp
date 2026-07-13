#!/usr/bin/env python3
"""Extract files from Open Lovable generated output JSON."""
import json
import os
import re
import sys

input_file = sys.argv[1] if len(sys.argv) > 1 else '/tmp/lovable_result.json'
output_dir = sys.argv[2] if len(sys.argv) > 2 else '/tmp/lovable-app'

with open(input_file) as f:
    data = json.load(f)

# Navigate to content string
result = data.get('result', '')
if isinstance(result, dict):
    content = result.get('content', '')
elif isinstance(result, str):
    # Try to parse the string as JSON
    try:
        result = json.loads(result)
        content = result.get('content', '')
    except (json.JSONDecodeError, AttributeError):
        content = result
else:
    content = str(result)

print(f"Content: {len(content)} chars")
print(f"File tags: {content.count('<file path=')}")

# Extract files using simple string splitting
count = 0
remaining = content
while '<file path="' in remaining:
    # Find the file path
    path_start = remaining.find('<file path="') + len('<file path="')
    path_end = remaining.find('"', path_start)
    path = remaining[path_start:path_end]
    
    # Find content between > and </file>
    content_start = remaining.find('>', path_end) + 1
    content_end = remaining.find('</file>', content_start)
    
    if content_end > content_start:
        file_content = remaining[content_start:content_end].strip()
        
        # Remove markdown code fences
        if file_content.startswith('```'):
            first_nl = file_content.find('\n')
            if first_nl > 0:
                file_content = file_content[first_nl+1:]
        if file_content.endswith('```'):
            file_content = file_content[:-3]
        
        # Save file
        fullpath = os.path.join(output_dir, path.lstrip('/'))
        os.makedirs(os.path.dirname(fullpath), exist_ok=True)
        with open(fullpath, 'w') as f:
            f.write(file_content.strip() + '\n')
        count += 1
        print(f"  [{count}] {path}")
    
    # Move past this block
    remaining = remaining[content_end + len('</file>'):]

print(f"\nSaved {count} files to {output_dir}")
