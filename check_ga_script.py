import glob, re

problems = []
for f in glob.glob('tools/*.html'):
    txt = open(f, encoding='utf-8', errors='ignore').read()
    matches = re.findall(r'<script[^>]+src=[^>]+>[\s\S]{0,200}function\s+\w+', txt)
    if matches:
        problems.append((f, matches[0][:100]))

print(f'Pages with function in src-script: {len(problems)}')
for fname, snippet in problems:
    print(f'  PROBLEM: {fname}')
    print(f'    {snippet[:80]}')
