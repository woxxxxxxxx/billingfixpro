import re

with open('tools/payment-history.html', 'r', encoding='utf-8') as f:
    content = f.read()

m = re.search(r'function generateDoc\(\)\{.*?\n\}', content, re.DOTALL)
if not m:
    print('generateDoc not found'); exit()

old_func = m.group(0)

new_func = '''function generateDoc(){
  const from_=document.getElementById('from')?.value||'Your Business';
  const to_=document.getElementById('to')?.value||'Client';
  const num_=document.getElementById('invNum')?.value||document.getElementById('qNum')?.value||'001';
  const date_=document.getElementById('invDate')?.value||document.getElementById('qDate')?.value||new Date().toISOString().split('T')[0];
  const due_=document.getElementById('dueDate')?.value||'';
  const notes=document.getElementById('notes')?.value||'';
  const extra=`Client: ${document.getElementById('clientAcct')?.value||''}  Period: ${document.getElementById('histPeriod')?.value||''}`;
  const taxRate=parseFloat(document.getElementById('taxRate')?.value)||0;
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

content = content.replace(old_func, new_func)
with open('tools/payment-history.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('payment-history.html fixed')
