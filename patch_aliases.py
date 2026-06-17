import glob, re

# 10 个 receipt 页：补 generateReceipt + printDoc 别名
RECEIPT_PAGES = [
    'business-receipt.html', 'cash-receipt.html', 'donation-receipt.html',
    'expense-receipt.html', 'hotel-receipt.html', 'payment-receipt.html',
    'refund-receipt.html', 'rent-receipt.html', 'sales-receipt.html',
    'taxi-receipt.html',
]

# 4 个 letter/notice 页：补 generate 别名
LETTER_PAGES = [
    'collection-letter.html', 'final-notice.html',
    'overdue-invoice-notice.html', 'payment-reminder.html',
]

# receipt-generator：只需 printDoc
PRINTDOC_ONLY = ['receipt-generator.html']

# net30/net60：需要完整 generateDoc + generateInvoice
NET_PAGES = ['net30-invoice.html', 'net60-invoice.html']

RECEIPT_ALIAS = """
function generateReceipt(){generateDoc();}
function printDoc(){window.print();}"""

LETTER_ALIAS = """
function generate(){generateDoc();}
function printDoc(){window.print();}"""

PRINTDOC_ALIAS = """
function printDoc(){window.print();}"""

# 完整 generateDoc 供 net30/net60（与其他发票页逻辑一致）
NET_GENDOC = """
function generateInvoice(){generateDoc();}
function generateDoc(){
  const from_=(document.getElementById('from')?.value||'').replace(/\\n/g,'<br>');
  const to_=(document.getElementById('to')?.value||'').replace(/\\n/g,'<br>');
  const num_=document.getElementById('invoiceNum')?.value||'001';
  const date_=document.getElementById('invoiceDate')?.value||'';
  const due_=document.getElementById('dueDate')?.value||'';
  const taxRate=parseFloat(document.getElementById('taxRate')?.value)||0;
  const discPct=(parseFloat(document.getElementById('discount')?.value)||0)/100;
  const notes=document.getElementById('notes')?.value||'';
  let linesHTML='',linesTxt='',sub=0;
  document.querySelectorAll('#lineItems tr').forEach(tr=>{
    const inputs=tr.querySelectorAll('input');if(inputs.length<3)return;
    const d=inputs[0].value||'Service';
    const q=parseFloat(inputs[1].value)||0;
    const r=parseFloat(inputs[2].value)||0;
    const tot=q*r; sub+=tot;
    linesHTML+=`<tr style="border-bottom:1px solid #f1f5f9"><td style="padding:10px 14px">${d}</td><td style="padding:10px 14px;text-align:right">${q}</td><td style="padding:10px 14px;text-align:right">$${r.toFixed(2)}</td><td style="padding:10px 14px;text-align:right;font-weight:600">$${tot.toFixed(2)}</td></tr>`;
    linesTxt+=`  ${d}  x${q}  $${r.toFixed(2)}  $${tot.toFixed(2)}\\n`;
  });
  const discAmt=sub*discPct;
  const taxAmt=(sub-discAmt)*taxRate/100;
  const total=sub-discAmt+taxAmt;
  document.getElementById('preview').innerHTML=generateInvoiceHTML(from_,to_,num_,date_,due_,linesHTML,sub,discAmt,taxAmt,total,notes,taxRate,typeof extra!=='undefined'?extra:'');
  document.getElementById('preview-txt').textContent=linesTxt;
  document.getElementById('output').style.display='block';
}
function printDoc(){window.print();}
function copyText(){
  navigator.clipboard.writeText(document.getElementById('preview-txt')?.textContent||document.getElementById('preview')?.innerText||'').then(()=>{
    const btn=document.getElementById('copyBtn');
    if(btn){const orig=btn.textContent;btn.textContent='✓ Copied!';btn.style.background='#059669';
    setTimeout(()=>{btn.textContent=orig;btn.style.background='';},2000);}
  });
}"""

BASE = 'C:/Users/Administrator/billingfixpro/tools/'
fixed = 0

def inject(f, alias):
    txt = open(f, encoding='utf-8').read()
    if alias.strip().split('\n')[0].strip() in txt:
        return False  # 已存在
    txt = txt.replace('</script>', alias + '\n</script>', 1)
    open(f, 'w', encoding='utf-8').write(txt)
    return True

for name in RECEIPT_PAGES:
    if inject(BASE + name, RECEIPT_ALIAS):
        print(f'receipt alias: {name}'); fixed += 1

for name in LETTER_PAGES:
    if inject(BASE + name, LETTER_ALIAS):
        print(f'letter alias: {name}'); fixed += 1

for name in PRINTDOC_ONLY:
    if inject(BASE + name, PRINTDOC_ALIAS):
        print(f'printdoc alias: {name}'); fixed += 1

for name in NET_PAGES:
    if inject(BASE + name, NET_GENDOC):
        print(f'full generateDoc: {name}'); fixed += 1

print(f'\ntotal fixed: {fixed}')
