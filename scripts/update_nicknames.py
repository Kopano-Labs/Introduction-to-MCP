import os
import re

count = 0
for root, dirs, files in os.walk('Schematics'):
    for file in files:
        if file.endswith('.md'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            new_content = content
            # Replace KC word boundaries
            new_content = re.sub(r'\bKC\b', 'Kopano Context', new_content)
            # Replace Orch word boundaries, checking it's not part of code imports or similar if possible
            # But since it's the second brain, we'll uniformly replace to align nickname
            new_content = re.sub(r'\bOrch\b', 'Kopano Context', new_content)
            new_content = re.sub(r'\borch\b', 'Kopano Context', new_content)

            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                count += 1

print(f"Updated {count} files")
