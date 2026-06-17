import glob, re

fixed = 0
for f in glob.glob('tools/*.html'):
    txt = open(f, encoding='utf-8', errors='ignore').read()
    # 匹配：<script async src="...GA...">  \n  function ... → 拆开
    new = re.sub(
        r'(<script[^>]+googletagmanager[^>]+>)\n(function\s)',
        r'\1\n</script>\n<script>\n\2',
        txt
    )
    if new != txt:
        open(f, 'w', encoding='utf-8').write(new)
        fixed += 1

print(f'fixed: {fixed} files')
