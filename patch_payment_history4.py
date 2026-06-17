with open('tools/payment-history.html', 'r', encoding='utf-8') as f:
    content = f.read()

script_start = content.rfind('<script>')
script_end = content.rfind('</script>') + len('</script>')

new_script = r"""<script>
const METHODS=['Bank Transfer','Credit Card','Cash','Check','ACH','PayPal','Wire Transfer','Other'];
const STATUSES=['Paid','Pending','Overdue','Refunded','Partial'];
const STATUS_COLORS={'Paid':'#059669','Pending':'#d97706','Overdue':'#dc2626','Refunded':'#7c3aed','Partial':'#0891b2'};

function addRow(){
  const tb=document.getElementById('lineItems');
  if(!tb)return;
  const tr=document.createElement('tr');
  const today=new Date().toISOString().split('T')[0];
  const mOpts=METHODS.map(m=>'<option>'+m+'</option>').join('');
  const sOpts=STATUSES.map(s=>'<option>'+s+'</option>').join('');
  tr.innerHTML='<td style="padding:6px"><input type="date" value="'+today+'" oninput="calcTotals()" style="padding:5px;border:1px solid #e2e8f0;border-radius:6px;font-size:13px;width:130px"></td>'
    +'<td style="padding:6px"><input type="text" placeholder="Monthly subscription" style="width:100%;padding:5px;border:1px solid #e2e8f0;border-radius:6px;font-size:13px"></td>'
    +'<td style="padding:6px"><input type="text" placeholder="REF-001" style="width:90px;padding:5px;border:1px solid #e2e8f0;border-radius:6px;font-size:13px"></td>'
    +'<td style="padding:6px"><select oninput="calcTotals()" style="padding:5px;border:1px solid #e2e8f0;border-radius:6px;font-size:13px">'+mOpts+'</select></td>'
    +'<td style="padding:6px"><input type="number" value="0" min="0" step="0.01" oninput="calcTotals()" style="width:90px;padding:5px;border:1px solid #e2e8f0;border-radius:6px;font-size:13px;text-align:right"></td>'
    +'<td style="padding:6px;text-align:center"><select oninput="calcTotals()" style="padding:5px;border:1px solid #e2e8f0;border-radius:6px;font-size:13px">'+sOpts+'</select></td>'
    +'<td style="padding:6px"><button onclick="this.closest(\'tr\').remove();calcTotals()" style="background:#fee2e2;color:#dc2626;border:none;border-radius:4px;padding:4px 8px;cursor:pointer">&#10005;</button></td>';
  tb.appendChild(tr);
  calcTotals();
}

function calcTotals(){
  var totalPaid=0,totalPending=0;
  document.querySelectorAll('#lineItems tr').forEach(function(tr){
    var amtInput=tr.querySelector('input[type=number]');
    var selects=tr.querySelectorAll('select');
    if(!amtInput)return;
    var amt=parseFloat(amtInput.value)||0;
    var status=selects[1]?selects[1].value:'Paid';
    if(status==='Paid')totalPaid+=amt;
    else if(status==='Pending'||status==='Partial')totalPending+=amt;
  });
  var el=function(id){return document.getElementById(id);};
  if(el('totalPaid'))el('totalPaid').textContent='$'+totalPaid.toFixed(2);
  if(el('totalPending'))el('totalPending').textContent='$'+totalPending.toFixed(2);
  if(el('totalAmt'))el('totalAmt').textContent='$'+(totalPaid+totalPending).toFixed(2);
}

function printDoc(){
  var o=document.getElementById('output');
  if(!o||o.style.display==='none'||o.style.display===''){
    alert('Please click Generate Payment History first, then print.');
    return;
  }
  window.print();
}

function copyText(){
  var txt=document.getElementById('preview-txt');
  if(!txt)return;
  navigator.clipboard.writeText(txt.textContent||'').then(function(){
    var btn=document.getElementById('copyBtn');
    if(btn){var orig=btn.textContent;btn.textContent='Copied!';btn.style.background='#059669';
    setTimeout(function(){btn.textContent=orig;btn.style.background='';},2000);}
  });
}

document.addEventListener('DOMContentLoaded',function(){
  addRow();addRow();addRow();calcTotals();
  document.querySelectorAll('.faq-item h3').forEach(function(q){
    q.addEventListener('click',function(){this.parentElement.classList.toggle('open');});
  });
});
window.addEventListener('scroll',function(){
  var b=document.getElementById('btt');if(b)b.classList.toggle('show',window.scrollY>300);
});

function generateDoc(){
  var holder=document.getElementById('from')?document.getElementById('from').value||'Account Holder':'Account Holder';
  var preparedBy=document.getElementById('to')?document.getElementById('to').value||'Billing Department':'Billing Department';
  var acct=document.getElementById('invNum')?document.getElementById('invNum').value||'ACCT-001':'ACCT-001';
  var stmtDate=document.getElementById('invDate')?document.getElementById('invDate').value||new Date().toISOString().split('T')[0]:new Date().toISOString().split('T')[0];
  var periodStart=document.getElementById('periodStart')?document.getElementById('periodStart').value||'':'';
  var periodEnd=document.getElementById('periodEnd')?document.getElementById('periodEnd').value||'':'';
  var notes=document.getElementById('notes')?document.getElementById('notes').value||'':'';
  var totalPaid=0,totalPending=0,rowsHTML='',rowsTxt='';

  document.querySelectorAll('#lineItems tr').forEach(function(tr,i){
    var allInputs=tr.querySelectorAll('input');
    var selects=tr.querySelectorAll('select');
    if(allInputs.length<3)return;
    var date=allInputs[0]?allInputs[0].value||stmtDate:stmtDate;
    var desc=allInputs[1]?allInputs[1].value||'Payment':'Payment';
    var ref=allInputs[2]?allInputs[2].value||'-':'-';
    var amtInput=tr.querySelector('input[type=number]');
    var amt=amtInput?parseFloat(amtInput.value)||0:0;
    var method=selects[0]?selects[0].value||'Bank Transfer':'Bank Transfer';
    var status=selects[1]?selects[1].value||'Paid':'Paid';
    var color=STATUS_COLORS[status]||'#475569';
    var bg=i%2===0?'#fff':'#f8fafc';
    if(status==='Paid')totalPaid+=amt;
    else if(status==='Pending'||status==='Partial')totalPending+=amt;
    rowsHTML+='<tr style="background:'+bg+';border-bottom:1px solid #f1f5f9">'
      +'<td style="padding:10px 12px;font-size:13px;color:#475569">'+date+'</td>'
      +'<td style="padding:10px 12px;font-size:13px">'+desc+'</td>'
      +'<td style="padding:10px 12px;font-size:13px;color:#64748b">'+ref+'</td>'
      +'<td style="padding:10px 12px;font-size:13px;color:#64748b">'+method+'</td>'
      +'<td style="padding:10px 12px;font-size:13px;text-align:right;font-weight:600">$'+amt.toFixed(2)+'</td>'
      +'<td style="padding:10px 12px;text-align:center"><span style="background:'+color+'18;color:'+color+';padding:3px 10px;border-radius:20px;font-size:12px;font-weight:600">'+status+'</span></td>'
      +'</tr>';
    rowsTxt+=date+'  '+desc+'  '+ref+'  '+method+'  $'+amt.toFixed(2)+'  '+status+'\n';
  });

  var grandTotal=totalPaid+totalPending;
  var periodStr=periodStart&&periodEnd?periodStart+' - '+periodEnd:(periodStart||periodEnd||'--');

  var html='<div style="font-family:Helvetica Neue,Arial,sans-serif;max-width:720px;padding:40px;background:#fff;border-radius:12px;box-shadow:0 4px 24px rgba(0,0,0,0.08)">'
    +'<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:28px;padding-bottom:20px;border-bottom:3px solid #0891b2">'
    +'<div><div style="font-size:22px;font-weight:800;color:#0891b2">Payment History</div>'
    +'<div style="font-size:13px;color:#64748b;margin-top:4px">Account #'+acct+'</div>'
    +'<div style="font-size:13px;color:#64748b">Statement Date: '+stmtDate+'</div>'
    +'<div style="font-size:13px;color:#64748b">Period: '+periodStr+'</div></div>'
    +'<div style="text-align:right;font-size:13px;color:#475569">'
    +'<div style="font-weight:700;color:#0f172a;margin-bottom:2px">Prepared By</div><div>'+preparedBy+'</div>'
    +'<div style="margin-top:8px;font-weight:700;color:#0f172a">Account Holder</div><div>'+holder+'</div></div></div>'
    +'<table style="width:100%;border-collapse:collapse;margin-bottom:24px;font-size:13px">'
    +'<thead><tr style="background:#0891b2">'
    +'<th style="color:#fff;padding:10px 12px;text-align:left;border-radius:6px 0 0 0">Date</th>'
    +'<th style="color:#fff;padding:10px 12px;text-align:left">Description</th>'
    +'<th style="color:#fff;padding:10px 12px;text-align:left">Reference</th>'
    +'<th style="color:#fff;padding:10px 12px;text-align:left">Method</th>'
    +'<th style="color:#fff;padding:10px 12px;text-align:right">Amount</th>'
    +'<th style="color:#fff;padding:10px 12px;text-align:center;border-radius:0 6px 0 0">Status</th>'
    +'</tr></thead><tbody>'+rowsHTML+'</tbody></table>'
    +'<div style="display:flex;justify-content:flex-end;margin-bottom:20px">'
    +'<div style="min-width:260px;font-size:13px">'
    +'<div style="display:flex;justify-content:space-between;padding:6px 0;color:#475569"><span>Total Paid</span><strong style="color:#059669">$'+totalPaid.toFixed(2)+'</strong></div>'
    +'<div style="display:flex;justify-content:space-between;padding:6px 0;color:#475569"><span>Total Pending</span><strong style="color:#d97706">$'+totalPending.toFixed(2)+'</strong></div>'
    +'<div style="display:flex;justify-content:space-between;padding:10px 0;margin-top:6px;border-top:2px solid #0891b2;font-size:15px;font-weight:800;color:#0891b2"><span>Grand Total</span><span>$'+grandTotal.toFixed(2)+'</span></div>'
    +'</div></div>'
    +(notes?'<div style="padding:14px 18px;background:#f0f9ff;border-left:3px solid #0891b2;border-radius:0 8px 8px 0;font-size:12px;color:#475569"><strong>Remarks:</strong> '+notes+'</div>':'')
    +'</div>';

  document.getElementById('preview').innerHTML=html;
  document.getElementById('preview-txt').textContent='PAYMENT HISTORY\nAccount: '+acct+'  Holder: '+holder+'\nPeriod: '+periodStr+'\n'+rowsTxt+'\nTotal Paid: $'+totalPaid.toFixed(2)+'  Pending: $'+totalPending.toFixed(2)+'  Grand Total: $'+grandTotal.toFixed(2);
  document.getElementById('output').style.display='block';
  document.getElementById('output').scrollIntoView({behavior:'smooth'});
}
</script>"""

content = content[:script_start] + new_script + content[script_end:]

with open('tools/payment-history.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("done, script block length:", len(new_script))
