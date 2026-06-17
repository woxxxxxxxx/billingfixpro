import glob, re

NEW_PRINT = '@media print{header,footer,.ad-slot,.ad-top,.ad-middle,.ad-bottom,.form-card,.tool-hero,.breadcrumb,.seo-section,.faq-section,.related-section,.affiliate-section,.download-row,#btt{display:none!important}body{background:#fff!important}main{padding:0!important}#output{display:block!important;box-shadow:none!important;border:none!important;padding:0!important}}'

OLD_PRINTS = [
    '@media print{header,footer,.ad-slot,.ad-top,.ad-middle,.ad-bottom,.form-card,.tool-hero,.breadcrumb,.seo-section,.faq-section,.related-section,.download-row,#btt{display:none!important}body{background:#fff!important}main{padding:0!important}#output{display:block!important;box-shadow:none!important;border:none!important;padding:0!important}}',
    '@media print{body>*{display:none!important}main{display:block!important}main>*{display:none!important}#output{display:block!important;margin:0!important;padding:0!important;border:none!important;box-shadow:none!important}.download-row{display:none!important}}',
    '@media print{header,footer,.ad-slot,.download-row,.related-section,.seo-section{display:none!important}.preview-card,.form-card{box-shadow:none!important;border:none!important}}',
]

PRINT_FUNC = '''function printDoc(){
  var o=document.getElementById('output');
  if(o)o.style.display='block';
  window.print();
}
'''

FIXED_GENERATE_DOC = '''function generateDoc(){
  const from_=document.getElementById('from')?.value||'Your Business';
  const to_=document.getElementById('to')?.value||'Client';
  const num_=document.getElementById('invNum')?.value||document.getElementById('qNum')?.value||'001';
  const date_=document.getElementById('invDate')?.value||document.getElementById('qDate')?.value||new Date().toISOString().split('T')[0];
  const due_=document.getElementById('dueDate')?.value||'';
  const notes=document.getElementById('notes')?.value||'';
  const taxRate=parseFloat(document.getElementById('taxRate')?.value)||0;
  const extra=(()=>{
    const ids=['channel','clientAcct','company','servicePeriod','engType','project','period','histPeriod','propertyType','leaseType','eventType','mediaType','agencyName'];
    const vals=ids.map(i=>document.getElementById(i)?.value||'').filter(Boolean);
    return vals.join('  ');
  })();
  let sub=0,linesHTML='',linesTxt='';
  document.querySelectorAll('#lineItems tr').forEach(tr=>{
    const inputs=tr.querySelectorAll('input');if(inputs.length<3)return;
    const d=inputs[0].value||'Service';
    const q=parseFloat(inputs[1].value)||0;
    const r=parseFloat(inputs[2].value)||0;
    const tot=q*r;sub+=tot;
    linesHTML+=`<tr style="border-bottom:1px solid #f1f5f9"><td style="padding:10px 14px">${d}</td><td style="padding:10px 14px;text-align:right">${q}</td><td style="padding:10px 14px;text-align:right">$${r.toFixed(2)}</td><td style="padding:10px 14px;text-align:right;font-weight:600">$${tot.toFixed(2)}</td></tr>`;
    linesTxt+=`  ${d}  x${q}  $${r.toFixed(2)}  $${tot.toFixed(2)}\n`;
  });
  const discPct=(parseFloat(document.getElementById('discount')?.value)||0)/100;
  const discAmt=sub*discPct;
  const taxAmt=(sub-discAmt)*(taxRate/100);
  const total=sub-discAmt+taxAmt;
  document.getElementById('preview').innerHTML=generateInvoiceHTML(from_,to_,num_,date_,due_,linesHTML,sub,discAmt,taxAmt,total,notes,taxRate,extra);
  document.getElementById('preview-txt').textContent=linesTxt;
  document.getElementById('output').style.display='block';
  document.getElementById('output').scrollIntoView({behavior:'smooth'});
}'''

fixed_print=0; fixed_btn=0; fixed_gen=0; fixed_func=0

for fpath in glob.glob('tools/*.html'):
    txt = open(fpath, encoding='utf-8', errors='ignore').read()
    orig = txt

    # 1. 更新 print CSS
    for old in OLD_PRINTS:
        if old in txt:
            txt = txt.replace(old, NEW_PRINT)
            fixed_print += 1
            break

    # 2. 替换 window.print() → printDoc()
    if 'onclick="window.print()"' in txt:
        txt = txt.replace('onclick="window.print()"', 'onclick="printDoc()"')
        fixed_btn += 1

    # 3. 注入 printDoc 函数
    if 'function printDoc()' not in txt and 'function copyText()' in txt:
        txt = txt.replace('function copyText()', PRINT_FUNC + 'function copyText()')
        fixed_func += 1

    # 4. 强制替换 generateDoc（括号深度匹配）
    if 'function generateDoc()' in txt:
        start = txt.find('function generateDoc()')
        depth = 0
        i = txt.find('{', start)
        end = i
        while i < len(txt):
            if txt[i] == '{':
                depth += 1
            elif txt[i] == '}':
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
            i += 1
        txt = txt[:start] + FIXED_GENERATE_DOC + txt[end:]
        fixed_gen += 1

    if txt != orig:
        open(fpath, 'w', encoding='utf-8').write(txt)

print(f"print CSS updated:    {fixed_print}")
print(f"print button updated: {fixed_btn}")
print(f"printDoc() injected:  {fixed_func}")
print(f"generateDoc replaced: {fixed_gen}")

# 验证
problems = []
for fpath in glob.glob('tools/*.html'):
    txt = open(fpath, encoding='utf-8', errors='ignore').read()
    if 'function generateDoc()' in txt:
        if "document.getElementById('subtotal')?.textContent" in txt:
            problems.append(('OLD_PATTERN', fpath))
if problems:
    print("REMAINING ISSUES:")
    for p in problems:
        print(' ', p)
else:
    print("ALL generateDoc CLEAN")
