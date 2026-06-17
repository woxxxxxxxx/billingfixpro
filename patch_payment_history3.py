with open('tools/payment-history.html', 'r', encoding='utf-8') as f:
    content = f.read()

new_gen = '''function generateDoc(){
  const holder=document.getElementById('from')?.value||'Account Holder';
  const preparedBy=document.getElementById('to')?.value||'Billing Department';
  const acct=document.getElementById('invNum')?.value||'ACCT-001';
  const stmtDate=document.getElementById('invDate')?.value||new Date().toISOString().split('T')[0];
  const periodStart=document.getElementById('periodStart')?.value||'';
  const periodEnd=document.getElementById('periodEnd')?.value||'';
  const notes=document.getElementById('notes')?.value||'';
  let totalPaid=0,totalPending=0,rowsHTML='',rowsTxt='';

  document.querySelectorAll('#lineItems tr').forEach((tr,i)=>{
    const allInputs=tr.querySelectorAll('input');
    const selects=tr.querySelectorAll('select');
    if(allInputs.length<3)return;
    const date=allInputs[0]?.value||stmtDate;
    const desc=allInputs[1]?.value||'Payment';
    const ref=allInputs[2]?.value||'-';
    const amt=parseFloat(tr.querySelector('input[type=number]')?.value)||0;
    const method=selects[0]?.value||'Bank Transfer';
    const status=selects[1]?.value||'Paid';
    const color=STATUS_COLORS[status]||'#475569';
    const bg=i%2===0?'#fff':'#f8fafc';
    if(status==='Paid')totalPaid+=amt;
    else if(status==='Pending'||status==='Partial')totalPending+=amt;
    rowsHTML+=`<tr style="background:${bg};border-bottom:1px solid #f1f5f9">
      <td style="padding:10px 12px;font-size:13px;color:#475569">${date}</td>
      <td style="padding:10px 12px;font-size:13px">${desc}</td>
      <td style="padding:10px 12px;font-size:13px;color:#64748b">${ref}</td>
      <td style="padding:10px 12px;font-size:13px;color:#64748b">${method}</td>
      <td style="padding:10px 12px;font-size:13px;text-align:right;font-weight:600">$${amt.toFixed(2)}</td>
      <td style="padding:10px 12px;text-align:center"><span style="background:${color}18;color:${color};padding:3px 10px;border-radius:20px;font-size:12px;font-weight:600">${status}</span></td>
    </tr>`;
    rowsTxt+=`${date.padEnd(12)}${desc.padEnd(28)}${ref.padEnd(12)}${method.padEnd(16)}$${amt.toFixed(2).padStart(10)}  ${status}\n`;
  });

  const grandTotal=totalPaid+totalPending;
  const periodStr=periodStart&&periodEnd?`${periodStart} – ${periodEnd}`:(periodStart||periodEnd||'—');

  const html=`<div style="font-family:'Helvetica Neue',Arial,sans-serif;max-width:720px;padding:40px;background:#fff;border-radius:12px;box-shadow:0 4px 24px rgba(0,0,0,0.08)">
    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:28px;padding-bottom:20px;border-bottom:3px solid #0891b2">
      <div>
        <div style="font-size:22px;font-weight:800;color:#0891b2;letter-spacing:-.4px">Payment History</div>
        <div style="font-size:13px;color:#64748b;margin-top:4px">Account #${acct}</div>
        <div style="font-size:13px;color:#64748b">Statement Date: ${stmtDate}</div>
        <div style="font-size:13px;color:#64748b">Period: ${periodStr}</div>
      </div>
      <div style="text-align:right;font-size:13px;color:#475569">
        <div style="font-weight:700;color:#0f172a;margin-bottom:2px">Prepared By</div>
        <div>${preparedBy}</div>
        <div style="margin-top:8px;font-weight:700;color:#0f172a">Account Holder</div>
        <div>${holder}</div>
      </div>
    </div>
    <table style="width:100%;border-collapse:collapse;margin-bottom:24px;font-size:13px">
      <thead><tr style="background:#0891b2">
        <th style="color:#fff;padding:10px 12px;text-align:left;border-radius:6px 0 0 0">Date</th>
        <th style="color:#fff;padding:10px 12px;text-align:left">Description</th>
        <th style="color:#fff;padding:10px 12px;text-align:left">Reference</th>
        <th style="color:#fff;padding:10px 12px;text-align:left">Method</th>
        <th style="color:#fff;padding:10px 12px;text-align:right">Amount</th>
        <th style="color:#fff;padding:10px 12px;text-align:center;border-radius:0 6px 0 0">Status</th>
      </tr></thead>
      <tbody>${rowsHTML}</tbody>
    </table>
    <div style="display:flex;justify-content:flex-end;margin-bottom:20px">
      <div style="min-width:260px;font-size:13px">
        <div style="display:flex;justify-content:space-between;padding:6px 0;color:#475569"><span>Total Paid</span><strong style="color:#059669">$${totalPaid.toFixed(2)}</strong></div>
        <div style="display:flex;justify-content:space-between;padding:6px 0;color:#475569"><span>Total Pending</span><strong style="color:#d97706">$${totalPending.toFixed(2)}</strong></div>
        <div style="display:flex;justify-content:space-between;padding:10px 0;margin-top:6px;border-top:2px solid #0891b2;font-size:15px;font-weight:800;color:#0891b2"><span>Grand Total</span><span>$${grandTotal.toFixed(2)}</span></div>
      </div>
    </div>
    ${notes?`<div style="padding:14px 18px;background:#f0f9ff;border-left:3px solid #0891b2;border-radius:0 8px 8px 0;font-size:12px;color:#475569"><strong>Remarks:</strong> ${notes}</div>`:''}
  </div>`;

  document.getElementById('preview').innerHTML=html;
  document.getElementById('preview-txt').textContent='PAYMENT HISTORY\nAccount: '+acct+'  |  Holder: '+holder+'\nPeriod: '+periodStr+'  |  Statement Date: '+stmtDate+'\n'+'─'.repeat(80)+'\n'+rowsTxt+'─'.repeat(80)+'\nTotal Paid: $'+totalPaid.toFixed(2)+'    Pending: $'+totalPending.toFixed(2)+'    Grand Total: $'+grandTotal.toFixed(2);
  document.getElementById('output').style.display='block';
  document.getElementById('output').scrollIntoView({behavior:'smooth'});
}'''

# 括号深度匹配精确替换
start = content.find('function generateDoc()')
if start == -1:
    print("ERROR: generateDoc not found")
    exit()

depth = 0
i = content.find('{', start)
end = i
while i < len(content):
    if content[i] == '{':
        depth += 1
    elif content[i] == '}':
        depth -= 1
        if depth == 0:
            end = i + 1
            break
    i += 1

content = content[:start] + new_gen + content[end:]

with open('tools/payment-history.html', 'w', encoding='utf-8') as f:
    f.write(content)

# 验证
with open('tools/payment-history.html', 'r', encoding='utf-8') as f:
    c2 = f.read()
print("STATUS_COLORS ref:", 'STATUS_COLORS' in c2)
print("periodStart ref:", 'periodStart' in c2)
print("generateInvoiceHTML ref:", 'generateInvoiceHTML' in c2.split('function generateDoc()')[1][:2000])
print("done")
