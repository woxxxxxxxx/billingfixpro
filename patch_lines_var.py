import glob

fixed = 0
for f in glob.glob('C:/Users/Administrator/billingfixpro/tools/*.html'):
    txt = open(f, encoding='utf-8', errors='ignore').read()
    new = txt.replace('${lines}', '${linesTxt}')
    if new != txt:
        open(f, 'w', encoding='utf-8').write(new)
        fixed += 1

print(f'fixed: {fixed} files')
