import glob, re

fixed = 0
for f in glob.glob('C:/Users/Administrator/billingfixpro/tools/*.html'):
    txt = open(f, encoding='utf-8').read()
    new_txt = txt.replace("}'\\`;", "}'`;")
    new_txt = new_txt.replace(":''\\`;", ":''`;")
    new_txt = re.sub(r"(\$\{[^}]+\})\\\`(;)", r"\1`\2", new_txt)
    if new_txt != txt:
        open(f, 'w', encoding='utf-8').write(new_txt)
        fixed += 1
        print(f'fixed: {f.split("/")[-1]}')

print(f'total fixed: {fixed}')
