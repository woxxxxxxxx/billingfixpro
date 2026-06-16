import glob

count = 0
for f in glob.glob('C:/Users/Administrator/billingfixpro/tools/*.html'):
    t = open(f, encoding='utf-8').read()
    new = t.replace('src="/logo.svg"', 'src="/logo.svg?v=2"')
    if new != t:
        open(f, 'w', encoding='utf-8').write(new)
        count += 1

print(f'done: {count} files updated')
