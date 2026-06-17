import glob, re, subprocess, tempfile, os

errors = []
for f in glob.glob('C:/Users/Administrator/billingfixpro/tools/*.html'):
    txt = open(f, encoding='utf-8', errors='ignore').read()
    scripts = re.findall(r'<script>(.*?)</script>', txt, re.DOTALL)
    for s in scripts:
        if 'generateDoc' not in s:
            continue
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False, encoding='utf-8') as tmp:
            tmp.write(s)
            tname = tmp.name
        r = subprocess.run(['node', '--check', tname], capture_output=True, text=True)
        os.unlink(tname)
        if r.returncode != 0:
            err_line = r.stderr.split('\n')[2] if len(r.stderr.split('\n')) > 2 else r.stderr
            errors.append(f'{f.split("/")[-1]}: {err_line.strip()}')
        break

print(f'Files with errors: {len(errors)}')
patterns = {}
for e in errors:
    key = ':'.join(e.split(':')[1:]).strip()[:80]
    patterns[key] = patterns.get(key, 0) + 1
for k, v in sorted(patterns.items(), key=lambda x: -x[1])[:10]:
    print(f'  [{v}x] {k}')
