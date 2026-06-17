import glob, re

fixed = 0
for f in glob.glob('C:/Users/Administrator/billingfixpro/**/*.html', recursive=True):
    txt = open(f, encoding='utf-8', errors='ignore').read()

    new_txt = re.sub(
        r'(const extra=)(\s+)([^\`\n][^\n]+\\n;)',
        r'\1`\3`',
        txt
    )
    new_txt = re.sub(
        r'(const extra=)( {1,2}[A-Z][^`\n]+\\n;)',
        r'\1`\2`',
        new_txt
    )

    if new_txt != txt:
        open(f, 'w', encoding='utf-8').write(new_txt)
        fixed += 1
        print(f'fixed: {f.split("/")[-1]}')

print(f'\ntotal fixed: {fixed}')
