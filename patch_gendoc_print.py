import glob, re

FIXED_GENERATE_DOC = '''function generateDoc(){
  const from_=document.getElementById('from')?.value||'Your Business';
  const to_=document.getElementById('to')?.value||'Client';
  const num_=document.getElementById('invNum')?.value||document.getElementById('qNum')?.value||'001';
  const date_=document.getElementById('invDate')?.value||document.getElementById('qDate')?.value||new Date().toISOString().split('T')[0];
  const due_=document.getElementById('dueDate')?.value||'';
  const notes=document.getElementById('notes')?.value||'';
  const taxRate=parseFloat(document.getElementById('taxRate')?.value)||0;
  const extra=(()=>{
    const ch=document.getElementById('channel')?.value||document.getElementById('clientAcct')?.value||document.getElementById('company')?.value||'';
    const pr=document.getElementById('period')?.value||document.getElementById('histPeriod')?.value||document.getElementById('project')?.value||'';
    return ch||pr?`${ch?'Channel: '+ch:''} ${pr?'Period: '+pr:''}`.trim():'';
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

OLD_PRINT_V1 = '@media print{body>*{display:none!important}main{display:block!important}main>*{display:none!important}#output{display:block!important;margin:0!important;padding:0!important;border:none!important;box-shadow:none!important}.download-row{display:none!important}}'
OLD_PRINT_V2 = '@media print{header,footer,.ad-slot,.download-row,.related-section,.seo-section{display:none!important}.preview-card,.form-card{box-shadow:none!important;border:none!important}}'
NEW_PRINT = '@media print{header,footer,.ad-slot,.ad-top,.ad-middle,.ad-bottom,.form-card,.tool-hero,.breadcrumb,.seo-section,.faq-section,.related-section,.download-row,#btt{display:none!important}body{background:#fff!important}main{padding:0!important}#output{display:block!important;box-shadow:none!important;border:none!important;padding:0!important}}'

fixed_gen = 0
fixed_print = 0

for fpath in glob.glob('tools/*.html'):
    txt = open(fpath, encoding='utf-8', errors='ignore').read()
    orig = txt

    # 修复 generateDoc：检测旧特征（sub取自textContent）
    if "document.getElementById('subtotal')?.textContent" in txt and 'function generateDoc()' in txt:
        txt = re.sub(r'function generateDoc\(\)\{[\s\S]*?\n\}', FIXED_GENERATE_DOC, txt)
        fixed_gen += 1

    # 修复 print CSS
    if OLD_PRINT_V1 in txt:
        txt = txt.replace(OLD_PRINT_V1, NEW_PRINT)
        fixed_print += 1
    elif OLD_PRINT_V2 in txt:
        txt = txt.replace(OLD_PRINT_V2, NEW_PRINT)
        fixed_print += 1

    if txt != orig:
        open(fpath, 'w', encoding='utf-8').write(txt)

print(f"generateDoc fixed: {fixed_gen} files")
print(f"print CSS fixed:   {fixed_print} files")
