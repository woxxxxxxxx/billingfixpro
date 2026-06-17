import glob

# 1. 确保所有 print CSS 含 affiliate-section
old_pattern = '.related-section,.download-row'
new_pattern = '.related-section,.affiliate-section,.download-row'

fixed = 0
for fpath in list(glob.glob('tools/*.html')) + ['index.html']:
    try:
        txt = open(fpath, encoding='utf-8', errors='ignore').read()
    except:
        continue
    if '@media print' in txt:
        after = txt.split('@media print')[1]
        if '.affiliate-section' not in after[:400] and old_pattern in txt:
            txt = txt.replace(old_pattern, new_pattern)
            open(fpath, 'w', encoding='utf-8').write(txt)
            fixed += 1

print(f"affiliate-section added to print CSS: {fixed} files")

# 2. 升级 printDoc：未生成时给提示
OLD_PRINTDOC = """function printDoc(){
  var o=document.getElementById('output');
  if(o)o.style.display='block';
  window.print();
}"""

NEW_PRINTDOC = """function printDoc(){
  var o=document.getElementById('output');
  if(!o||o.style.display==='none'||o.style.display===''){
    alert('Please click "Generate" first to create your document, then print.');
    return;
  }
  window.print();
}"""

updated = 0
for fpath in glob.glob('tools/*.html'):
    txt = open(fpath, encoding='utf-8', errors='ignore').read()
    if OLD_PRINTDOC in txt:
        txt = txt.replace(OLD_PRINTDOC, NEW_PRINTDOC)
        open(fpath, 'w', encoding='utf-8').write(txt)
        updated += 1

print(f"printDoc guard updated: {updated} files")

# 验证
remaining = []
for fpath in glob.glob('tools/*.html'):
    txt = open(fpath, encoding='utf-8', errors='ignore').read()
    if '@media print' in txt:
        after = txt.split('@media print')[1][:400]
        if '.affiliate-section' not in after:
            remaining.append(fpath)

if remaining:
    print(f"MISSING affiliate-section in print CSS: {len(remaining)} files")
    for f in remaining[:5]:
        print(' ', f)
else:
    print("ALL print CSS correct")
