import glob, re, subprocess, tempfile, os

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
            fname = f.split('\\')[-1].split('/')[-1]
            print(f'\n=== {fname} ===')
            print(r.stderr[:400])
        break
