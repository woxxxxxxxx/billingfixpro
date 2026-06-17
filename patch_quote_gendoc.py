import glob, re

TARGET_FILES = [
    'tools/cleaning-estimate.html','tools/construction-estimate.html',
    'tools/estimate-generator.html','tools/job-estimate.html',
    'tools/price-quote.html','tools/project-quote.html',
    'tools/quote-generator.html','tools/repair-estimate.html',
    'tools/sales-quote.html','tools/service-quote.html'
]

FIXED_GENERATE_QUOTE = '''function generateQuote(){
  const from_=document.getElementById('from')?.value||document.getElementById('business')?.value||'Your Business';
  const to_=document.getElementById('to')?.value||document.getElementById('client')?.value||'Client';
  const num_=document.getElementById('qNum')?.value||document.getElementById('invNum')?.value||document.getElementById('quoteNum')?.value||'Q-001';
  const date_=document.getElementById('qDate')?.value||document.getElementById('invDate')?.value||new Date().toISOString().split('T')[0];
  const due_=document.getElementById('validDays')?.value?'Valid '+document.getElementById('validDays').value+' days':'';
  const notes=document.getElementById('notes')?.value||'';
  const taxRate=parseFloat(document.getElementById('taxRate')?.value)||0;
  const extra=(()=>{
    const ids=['validDays','projectName','projectType','jobType','estimateType','serviceType','siteAddress','location'];
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

fixed = 0
for fpath in TARGET_FILES:
    try:
        txt = open(fpath, encoding='utf-8', errors='ignore').read()
    except:
        print(f"NOT FOUND: {fpath}"); continue
    # 找实际的 generate 主函数（generateQuote / generateDoc / generate）
    fn_name = None
    for candidate in ['function generateQuote()', 'function generateDoc()', 'function generate()']:
        if candidate in txt:
            fn_name = candidate
            break
    if not fn_name:
        print(f"NO generate fn: {fpath}"); continue

    start = txt.find(fn_name)
    depth = 0
    i = txt.find('{', start)
    while i < len(txt):
        if txt[i] == '{': depth += 1
        elif txt[i] == '}':
            depth -= 1
            if depth == 0:
                end = i + 1
                break
        i += 1
    # 替换时保持原函数名
    new_fn = FIXED_GENERATE_QUOTE.replace('function generateQuote()', fn_name.replace('function ', 'function '))
    txt = txt[:start] + new_fn + txt[end:]
    open(fpath, 'w', encoding='utf-8').write(txt)
    fixed += 1
    print(f"fixed: {fpath}")

print(f"\nTotal fixed: {fixed}/10")

# 验证：这10个文件的 generateDoc 现在都调用 generateInvoiceHTML
print("\nVerification:")
for fpath in TARGET_FILES:
    try:
        txt = open(fpath, encoding='utf-8', errors='ignore').read()
        for candidate in ['function generateQuote()', 'function generateDoc()', 'function generate()']:
            if candidate in txt:
                start = txt.find(candidate); break
        else:
            print(f"  {fpath}: NO GENERATE FN"); continue
        depth = 0
        i = txt.find('{', start)
        while i < len(txt):
            if txt[i] == '{': depth += 1
            elif txt[i] == '}':
                depth -= 1
                if depth == 0: end = i+1; break
            i += 1
        body = txt[start:end]
        calls_html = 'generateInvoiceHTML(' in body
        calls_tc = "getElementById('preview').textContent" in body
        print(f"  {fpath.split('/')[-1]}: HTML={calls_html} textContent={calls_tc}")
    except:
        print(f"  {fpath}: ERROR")
