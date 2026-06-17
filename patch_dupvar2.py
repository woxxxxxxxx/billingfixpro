import glob, re, subprocess, tempfile, os

def fix_dup_consts(js):
    seen = set()
    def replacer(m):
        varname = m.group(1)
        if varname in seen:
            return varname + m.group(2)  # 去掉 const
        seen.add(varname)
        return m.group(0)
    return re.sub(r'\bconst (\w+)(=)', replacer, js)

fixed = 0
for f in glob.glob('C:/Users/Administrator/billingfixpro/tools/*.html'):
    txt = open(f, encoding='utf-8', errors='ignore').read()

    # 提取并检查所有 script 块
    def fix_script(m):
        s = m.group(1)
        if 'generateDoc' not in s:
            return m.group(0)
        return '<script>' + fix_dup_consts(s) + '</script>'

    new_txt = re.sub(r'<script>(.*?)</script>', fix_script, txt, flags=re.DOTALL)
    if new_txt != txt:
        open(f, 'w', encoding='utf-8').write(new_txt)
        fixed += 1

print(f'fixed: {fixed} files')
