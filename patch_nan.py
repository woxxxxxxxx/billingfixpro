import glob, re

fixed = 0
for f in glob.glob('C:/Users/Administrator/billingfixpro/**/*.html', recursive=True):
    txt = open(f, encoding='utf-8', errors='ignore').read()
    orig = txt

    # 1. 修 NaN：字符串 * 数字 → .repeat(N)
    txt = re.sub(r"'(-+)'\s*\*\s*(\d+)", lambda m: f"'-'.repeat({m.group(2)})", txt)
    txt = re.sub(r"'(=+)'\s*\*\s*(\d+)", lambda m: f"'='.repeat({m.group(2)})", txt)
    txt = re.sub(r"'(\*+)'\s*\*\s*(\d+)", lambda m: f"'*'.repeat({m.group(2)})", txt)
    txt = re.sub(r"'([^'\\])'\s*\*\s*(\d+)", lambda m: f"'{m.group(1)}'.repeat({m.group(2)})", txt)

    # 2. Copy Text 加视觉反馈
    txt = txt.replace(
        "function copyText(){navigator.clipboard.writeText(document.getElementById('preview').textContent);}",
        """function copyText(){
  navigator.clipboard.writeText(document.getElementById('preview').textContent).then(()=>{
    const btn=document.getElementById('copyBtn');
    if(btn){const orig=btn.textContent;btn.textContent='✓ Copied!';btn.style.background='#059669';
    setTimeout(()=>{btn.textContent=orig;btn.style.background='';},2000);}
  });
}"""
    )

    if txt != orig:
        open(f, 'w', encoding='utf-8').write(txt)
        fixed += 1

print(f'fixed: {fixed} files')
