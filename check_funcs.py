import glob, re

broken = []
for f in glob.glob('C:/Users/Administrator/billingfixpro/tools/*.html'):
    txt = open(f, encoding='utf-8', errors='ignore').read()

    onclick_funcs = set(re.findall(r'onclick="(\w+)\(\)"', txt))
    defined_funcs = set(re.findall(r'function (\w+)\s*\(', txt))

    missing = onclick_funcs - defined_funcs
    if missing:
        broken.append((f.split('\\')[-1].split('/')[-1], missing))

print(f'Pages with missing functions: {len(broken)}')
for fname, missing in broken[:20]:
    print(f'  {fname}: missing {missing}')
