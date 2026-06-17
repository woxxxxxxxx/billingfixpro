import re

with open('tools/payment-history.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix h2 (LF)
content = content.replace(
    '<div class="form-card">\n  <h2>Invoice Details</h2>',
    '<div class="form-card">\n  <h2>Account Information</h2>'
)
print("Invoice Details remaining:", 'Invoice Details' in content)

# Replace entire script block
m = re.search(r'<script>\n+function addRow\(\)\{.*?</script>', content, re.DOTALL)
if not m:
    print("ERROR: script block not found")
    idx = content.find('function addRow')
    print(repr(content[idx-50:idx+100]))
    exit()

print("script block found, len:", len(m.group(0)))

new_script = """<script>
const METHODS=['Bank Transfer','Credit Card','Cash','Check','ACH','PayPal','Wire Transfer','Other'];
const STATUSES=['Paid','Pending','Overdue','Refunded','Partial'];
const STATUS_COLORS={'Paid':'#059669','Pending':'#d97706','Overdue':'#dc2626','Refunded':'#7c3aed','Partial':'#0891b2'};

function addRow(){
  const tb=document.getElementById('lineItems');
  const tr=document.createElement('tr');
  const today=new Date().toISOString().split('T')[0];
  const methodOpts=METHODS.map(m=>`<option>${m}</option>`).join('');
  const statusOpts=STATUSES.map(s=>`<option>${s}</option>`).join('');
  tr.innerHTML=`
    <td style="padding:6px"><input type="date" value="${today}" oninput="calcTotals()" style="padding:5px;border:1px solid #e2e8f0;border-radius:6px;font-size:13px;width:130px"></td>
    <td style="padding:6px"><input type="text" placeholder="Monthly subscription" oninput="calcTotals()" style="width:100%;padding:5px;border:1px solid #e2e8f0;border-radius:6px;font-size:13px"></td>
    <td style="padding:6px"><input type="text" placeholder="REF-001" style="width:90px;padding:5px;border:1px solid #e2e8f0;border-radius:6px;font-size:13px"></td>
    <td style="padding:6px"><select oninput="calcTotals()" style="padding:5px;border:1px solid #e2e8f0;border-radius:6px;font-size:13px">${methodOpts}</select></td>
    <td style="padding:6px"><input type="number" value="0" min="0" step="0.01" oninput="calcTotals()" style="width:90px;padding:5px;border:1px solid #e2e8f0;border-radius:6px;font-size:13px;text-align:right"></td>
    <td style="padding:6px;text-align:center"><select oninput="calcTotals()" style="padding:5px;border:1px solid #e2e8f0;border-radius:6px;font-size:13px">${statusOpts}</select></td>
    <td style="padding:6px"><button onclick="this.closest('tr').remove();calcTotals()" style="background:#fee2e2;color:#dc2626;border:none;border-radius:4px;padding:4px 8px;cursor:pointer">✕</button></td>`;
  tb.appendChild(tr);calcTotals();
}

function calcTotals(){
  let totalPaid=0,totalPending=0;
  document.querySelectorAll('#lineItems tr').forEach(tr=>{
    const amtInputs=tr.querySelectorAll('input[type=number]');
    const selects=tr.querySelectorAll('select');
    if(!amtInputs.length)return;
    const amt=parseFloat(amtInputs[0].value)||0;
    const status=selects[1]?.value||'Paid';
    if(status==='Paid')totalPaid+=amt;
    else if(status==='Pending'||status==='Partial')totalPending+=amt;
  });
  const el=id=>document.getElementById(id);
  if(el('totalPaid'))el('totalPaid').textContent='$'+totalPaid.toFixed(2);
  if(el('totalPending'))el('totalPending').textContent='$'+totalPending.toFixed(2);
  if(el('totalAmt'))el('totalAmt').textContent='$'+(totalPaid+totalPending).toFixed(2);
}

function copyText(){
  navigator.clipboard.writeText(document.getElementById('preview-txt')?.textContent||'').then(()=>{
    const btn=document.getElementById('copyBtn');
    if(btn){const orig=btn.textContent;btn.textContent='✓ Copied!';btn.style.background='#059669';
    setTimeout(()=>{btn.textContent=orig;btn.style.background='';},2000);}
  });
}

document.addEventListener('DOMContentLoaded',function(){
  addRow();addRow();addRow();calcTotals();
  document.querySelectorAll('.faq-item h3').forEach(function(q){q.addEventListener('click',function(){this.parentElement.classList.toggle('open');});});
});
window.addEventListener('scroll',function(){var b=document.getElementById('btt');if(b)b.classList.toggle('show',window.scrollY>300);});

function generateDoc(){
  const holder=document.getElementById('from')?.value||'Account Holder';
  const preparedBy=document.getElementById('to')?.value||'Billing Department';
  const acct=document.getElementById('invNum')?.value||'ACCT-001';
  const stmtDate=document.getElementById('invDate')?.value||new Date().toISOString().split('T')[0];
  const periodStart=document.getElementById('periodStart')?.value||'';
  const periodEnd=document.getElementById('periodEnd')?.value||'';
  const notes=document.getElementById('notes')?.value||'';
  let totalPaid=0,totalPending=0,rowsHTML='',rowsTxt='';

  document.querySelectorAll('#lineItems tr').forEach((tr,i)=>{
    const dateInput=tr.querySelector('input[type=date]');
    const textInputs=tr.querySelectorAll('input[type=text]');
    const amtInput=tr.querySelector('input[type=number]');
    const selects=tr.querySelectorAll('select');
    if(!amtInput)return;
    const date=dateInput?.value||stmtDate;
    const desc=textInputs[0]?.value||'Payment';
    const ref=textInputs[1]?.value||'-';
    const method=selects[0]?.value||'Bank Transfer';
    const amt=parseFloat(amtInput?.value)||0;
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
    rowsTxt+=date.padEnd(12)+desc.padEnd(28)+ref.padEnd(12)+method.padEnd(16)+'$'+amt.toFixed(2).padStart(10)+'  '+status+'\\n';
  });

  const grandTotal=totalPaid+totalPending;
  const periodStr=periodStart&&periodEnd?periodStart+' – '+periodEnd:(periodStart||periodEnd||'—');

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
  document.getElementById('preview-txt').textContent=
    'PAYMENT HISTORY\\nAccount: '+acct+'  |  Holder: '+holder+'  |  Prepared by: '+preparedBy+'\\nPeriod: '+periodStr+'  |  Statement Date: '+stmtDate+'\\n'+'\\u2500'.repeat(80)+'\\nDate'.padEnd(12)+'Description'.padEnd(28)+'Reference'.padEnd(12)+'Method'.padEnd(16)+'Amount'.padStart(10)+'  Status\\n'+'\\u2500'.repeat(80)+'\\n'+rowsTxt+'\\u2500'.repeat(80)+'\\nTotal Paid: $'+totalPaid.toFixed(2)+'    Total Pending: $'+totalPending.toFixed(2)+'    Grand Total: $'+grandTotal.toFixed(2)+(notes?'\\n\\nRemarks: '+notes:'');
  document.getElementById('output').style.display='block';
  document.getElementById('output').scrollIntoView({behavior:'smooth'});
}
</script>"""

content = content.replace(m.group(0), new_script)

with open('tools/payment-history.html', 'w', encoding='utf-8') as f:
    f.write(content)

# Verify
with open('tools/payment-history.html', 'r', encoding='utf-8') as f:
    c2 = f.read()
for field in ['histPeriod', 'clientAcct', 'taxRate', 'id="discount"', 'dueDate', 'Invoice Details', 'Line Items', 'Generate Invoice']:
    if field in c2:
        print(f"STILL PRESENT: {field}")

# Check new fields present
for field in ['periodStart', 'periodEnd', 'Account Information', 'Payment Records', 'totalPaid', 'totalPending', 'METHODS']:
    print(f"  {field}: {'OK' if field in c2 else 'MISSING'}")
print("done")
