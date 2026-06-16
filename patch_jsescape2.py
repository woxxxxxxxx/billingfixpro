import glob, re

fixed = 0
total = 0

for f in glob.glob('C:/Users/Administrator/billingfixpro/**/*.html', recursive=True):
    if 'index.html' in f:
        continue
    txt = open(f, encoding='utf-8', errors='ignore').read()
    total += 1

    new_txt = re.sub(r'\\\`(;)', r'`\1', txt)

    if new_txt != txt:
        open(f, 'w', encoding='utf-8').write(new_txt)
        fixed += 1

print(f'scanned: {total}, fixed: {fixed}')
