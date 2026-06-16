"""
BillingFixPro 差异化脚本
23 files across 4 duplicate groups
"""
import os, re
os.chdir(r"C:\Users\Administrator\billingfixpro\tools")

def replace_script(c, new_body):
    parts = c.rsplit('<script>', 1)
    end = parts[1].rsplit('</script>', 1)
    return parts[0] + '<script>\n' + new_body + '\n</script>' + end[1]

def replace_form(c, old_form, new_form):
    if old_form in c:
        return c.replace(old_form, new_form, 1)
    return None

def save(fname, content):
    with open(fname, 'w', encoding='utf-8') as f:
        f.write(content)

def load(fname):
    with open(fname, 'r', encoding='utf-8') as f:
        return f.read()

changed = 0

# ═══════════════════════════════════════════════════════════
# GROUP 1: TAX CALCULATORS (4 tools)
# Original all share: amount + rate + mode → pre/tax/total
# ═══════════════════════════════════════════════════════════

# ── 1a. vat-calculator.html ────────────────────────────────
VAT_OLD_FORM = """<div class="form-card">
  <h2>Calculate Tax</h2>
  <div class="form-grid">
    <div class="field"><label>Amount ($)</label><input id="amount" type="number" value="1000" step="0.01"></div>
    <div class="field"><label>Tax Rate (%)</label><input id="rate" type="number" value="8.875" step="0.001"></div>
    <div class="field full"><label>Calculation Mode</label><select id="mode"><option value="add">Add Tax to amount</option><option value="remove">Extract Tax from total</option></select></div>
  </div>
  <button class="btn-primary" onclick="calc()">Calculate Tax</button>
</div>"""

VAT_NEW_FORM = """<div class="form-card">
  <h2>VAT Calculator</h2>
  <div class="form-grid">
    <div class="field"><label>Amount</label><input id="amount" type="number" value="1000" step="0.01"></div>
    <div class="field"><label>Currency</label><select id="currency"><option value="EUR">EUR €</option><option value="GBP">GBP £</option><option value="USD">USD $</option></select></div>
    <div class="field"><label>VAT Rate</label><select id="vatPreset" onchange="applyPreset()"><option value="20">UK Standard 20%</option><option value="5">UK Reduced 5%</option><option value="0">UK Zero 0%</option><option value="21">EU Standard 21%</option><option value="19">Germany 19%</option><option value="20">France 20%</option><option value="23">Ireland 23%</option><option value="25">Denmark 25%</option><option value="custom">Custom</option></select></div>
    <div class="field"><label>Custom VAT Rate (%)</label><input id="rate" type="number" value="20" step="0.1"></div>
    <div class="field"><label>Calculation Mode</label><select id="mode"><option value="add">Add VAT to net amount</option><option value="remove">Extract VAT from gross</option></select></div>
    <div class="field"><label>VAT Registration Number (optional)</label><input id="vatNum" type="text" placeholder="GB123456789"></div>
  </div>
  <button class="btn-primary" onclick="calc()">Calculate VAT</button>
</div>"""

VAT_SCRIPT = """
const symbols={EUR:'€',GBP:'£',USD:'$'};
function applyPreset(){
  const v=document.getElementById('vatPreset').value;
  if(v!=='custom') document.getElementById('rate').value=v;
}
function calc(){
  const amt=parseFloat(document.getElementById('amount').value)||0;
  const rate=(parseFloat(document.getElementById('rate').value)||0)/100;
  const mode=document.getElementById('mode').value;
  const cur=document.getElementById('currency').value;
  const sym=symbols[cur]||'$';
  let pre,tax,total;
  if(mode==='add'){pre=amt;tax=amt*rate;total=amt+tax;}
  else{total=amt;pre=amt/(1+rate);tax=total-pre;}
  const vatNum=document.getElementById('vatNum').value;
  document.getElementById('result').style.display='block';
  document.getElementById('preAmt').textContent=sym+pre.toFixed(2)+' (net)';
  document.getElementById('taxAmt').textContent=sym+tax.toFixed(2)+' VAT @ '+(rate*100).toFixed(1)+'%';
  document.getElementById('totalAmt').textContent=sym+total.toFixed(2)+' (gross)';
  const note=document.getElementById('vatNote');
  if(note){
    const rcMsg=vatNum?'Reverse charge may apply if B2B cross-border — check Art. 196 EU VAT Directive.':'Enter a VAT number if issuing a B2B cross-border invoice.';
    note.textContent=rcMsg;
  }
}
"""

c = load('vat-calculator.html')
orig = c
c = replace_form(c, VAT_OLD_FORM, VAT_NEW_FORM)
if c:
    # Add note div after result card if not present
    if 'vatNote' not in c:
        c = c.replace(
            '<div id="result" class="preview-card" style="display:none">',
            '<div id="result" class="preview-card" style="display:none">'
        )
        c = c.replace(
            '<div style="font-size:13px;color:var(--text2)">Total Amount</div></div>\n  </div>\n</div>',
            '<div style="font-size:13px;color:var(--text2)">Total Amount</div></div>\n  </div>\n  <p id="vatNote" style="margin-top:12px;font-size:13px;color:#475569;padding:10px;background:#f8fafc;border-radius:6px"></p>\n</div>'
        )
    c = replace_script(c, VAT_SCRIPT)
    save('vat-calculator.html', c)
    changed += 1
    print('vat-calculator.html: DONE')
else:
    print('vat-calculator.html: FORM NO MATCH')

# ── 1b. gst-calculator.html ────────────────────────────────
GST_NEW_FORM = """<div class="form-card">
  <h2>GST Calculator</h2>
  <div class="form-grid">
    <div class="field"><label>Amount</label><input id="amount" type="number" value="1000" step="0.01"></div>
    <div class="field"><label>Country / Region</label><select id="country" onchange="setGST()">
      <option value="AU">Australia (10% GST)</option>
      <option value="NZ">New Zealand (15% GST)</option>
      <option value="CA_ON">Canada — Ontario (13% HST)</option>
      <option value="CA_BC">Canada — BC (5% GST + 7% PST)</option>
      <option value="CA_AB">Canada — Alberta (5% GST only)</option>
      <option value="CA_QC">Canada — Quebec (5% GST + 9.975% QST)</option>
      <option value="IN_18">India (18% GST)</option>
      <option value="IN_12">India (12% GST)</option>
      <option value="IN_5">India (5% GST)</option>
      <option value="SG">Singapore (9% GST)</option>
      <option value="custom">Custom rate</option>
    </select></div>
    <div class="field"><label>GST/Tax Rate (%) — auto-filled</label><input id="rate" type="number" value="10" step="0.001"></div>
    <div class="field"><label>Calculation Mode</label><select id="mode"><option value="add">Add GST to amount</option><option value="remove">Extract GST from total</option></select></div>
    <div class="field"><label>ABN / Tax Registration No. (optional)</label><input id="abn" type="text" placeholder="e.g. 12 345 678 901"></div>
  </div>
  <button class="btn-primary" onclick="calc()">Calculate GST</button>
</div>"""

GST_SCRIPT = """
const GST_RATES={AU:10,NZ:15,CA_ON:13,CA_BC:12,CA_AB:5,CA_QC:14.975,IN_18:18,IN_12:12,IN_5:5,SG:9};
const GST_LABELS={AU:'GST (Australia)',NZ:'GST (New Zealand)',CA_ON:'HST (Ontario)',CA_BC:'GST+PST (BC)',CA_AB:'GST (Alberta)',CA_QC:'GST+QST (Quebec)',IN_18:'GST 18% (India)',IN_12:'GST 12% (India)',IN_5:'GST 5% (India)',SG:'GST (Singapore)'};
function setGST(){
  const c=document.getElementById('country').value;
  if(GST_RATES[c]!==undefined) document.getElementById('rate').value=GST_RATES[c];
}
function calc(){
  const amt=parseFloat(document.getElementById('amount').value)||0;
  const rate=(parseFloat(document.getElementById('rate').value)||0)/100;
  const mode=document.getElementById('mode').value;
  const country=document.getElementById('country').value;
  const label=GST_LABELS[country]||'GST';
  let pre,tax,total;
  if(mode==='add'){pre=amt;tax=amt*rate;total=amt+tax;}
  else{total=amt;pre=amt/(1+rate);tax=total-pre;}
  document.getElementById('result').style.display='block';
  document.getElementById('preAmt').textContent='$'+pre.toFixed(2);
  document.getElementById('taxAmt').textContent='$'+tax.toFixed(2)+' ('+label+')';
  document.getElementById('totalAmt').textContent='$'+total.toFixed(2);
}
"""

c = load('gst-calculator.html')
c2 = replace_form(c, VAT_OLD_FORM, GST_NEW_FORM)
if c2:
    c2 = replace_script(c2, GST_SCRIPT)
    save('gst-calculator.html', c2)
    changed += 1
    print('gst-calculator.html: DONE')
else:
    print('gst-calculator.html: FORM NO MATCH - trying direct script replace')
    c2 = replace_script(c, GST_SCRIPT)
    save('gst-calculator.html', c2)
    changed += 1
    print('gst-calculator.html: SCRIPT ONLY')

# ── 1c. sales-tax-calculator.html ─────────────────────────
SALES_NEW_FORM = """<div class="form-card">
  <h2>US Sales Tax Calculator</h2>
  <div class="form-grid">
    <div class="field"><label>Pre-Tax Amount ($)</label><input id="amount" type="number" value="1000" step="0.01"></div>
    <div class="field"><label>State</label><select id="state" onchange="setStateRate()">
      <option value="0">— No state tax —</option>
      <option value="4">Alabama (4%)</option>
      <option value="0">Alaska (0%)</option>
      <option value="5.6">Arizona (5.6%)</option>
      <option value="6.5">Arkansas (6.5%)</option>
      <option value="7.25">California (7.25%)</option>
      <option value="2.9">Colorado (2.9%)</option>
      <option value="6.35">Connecticut (6.35%)</option>
      <option value="0">Delaware (0%)</option>
      <option value="6">Florida (6%)</option>
      <option value="4">Georgia (4%)</option>
      <option value="4">Hawaii (4%)</option>
      <option value="6">Idaho (6%)</option>
      <option value="6.25">Illinois (6.25%)</option>
      <option value="7">Indiana (7%)</option>
      <option value="6">Iowa (6%)</option>
      <option value="6.5">Kansas (6.5%)</option>
      <option value="6">Kentucky (6%)</option>
      <option value="4.45">Louisiana (4.45%)</option>
      <option value="5.5">Maine (5.5%)</option>
      <option value="6">Maryland (6%)</option>
      <option value="6.25">Massachusetts (6.25%)</option>
      <option value="6">Michigan (6%)</option>
      <option value="6.875">Minnesota (6.875%)</option>
      <option value="7">Mississippi (7%)</option>
      <option value="4.225">Missouri (4.225%)</option>
      <option value="0">Montana (0%)</option>
      <option value="5.5">Nebraska (5.5%)</option>
      <option value="6.85">Nevada (6.85%)</option>
      <option value="0">New Hampshire (0%)</option>
      <option value="6.625">New Jersey (6.625%)</option>
      <option value="5">New Mexico (5%)</option>
      <option value="4">New York (4%)</option>
      <option value="4.75">North Carolina (4.75%)</option>
      <option value="5">North Dakota (5%)</option>
      <option value="5.75">Ohio (5.75%)</option>
      <option value="4.5">Oklahoma (4.5%)</option>
      <option value="0">Oregon (0%)</option>
      <option value="6">Pennsylvania (6%)</option>
      <option value="7">Rhode Island (7%)</option>
      <option value="6">South Carolina (6%)</option>
      <option value="4.5">South Dakota (4.5%)</option>
      <option value="7">Tennessee (7%)</option>
      <option value="6.25">Texas (6.25%)</option>
      <option value="6.1">Utah (6.1%)</option>
      <option value="6">Vermont (6%)</option>
      <option value="5.3">Virginia (5.3%)</option>
      <option value="6.5">Washington (6.5%)</option>
      <option value="6">West Virginia (6%)</option>
      <option value="5">Wisconsin (5%)</option>
      <option value="4">Wyoming (4%)</option>
    </select></div>
    <div class="field"><label>State Rate (%) — auto-filled</label><input id="stateRate" type="number" value="0" step="0.001"></div>
    <div class="field"><label>County / City Rate (%) — add on top</label><input id="localRate" type="number" value="0" step="0.001" placeholder="e.g. 2.0"></div>
    <div class="field"><label>Calculation Mode</label><select id="mode"><option value="add">Add tax to pre-tax amount</option><option value="remove">Extract tax from total</option></select></div>
  </div>
  <button class="btn-primary" onclick="calc()">Calculate Sales Tax</button>
</div>"""

SALES_RESULT = """<div id="result" class="preview-card" style="display:none">
  <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;text-align:center">
    <div><div style="font-size:1.8rem;font-weight:800;color:var(--text2)" id="preAmt">-</div><div style="font-size:13px;color:var(--text2)">Pre-Tax Amount</div></div>
    <div><div style="font-size:1.8rem;font-weight:800;color:#dc2626" id="taxAmt">-</div><div style="font-size:13px;color:var(--text2)">Tax Amount</div></div>
    <div><div style="font-size:1.8rem;font-weight:800;color:var(--primary)" id="totalAmt">-</div><div style="font-size:13px;color:var(--text2)">Total Amount</div></div>
  </div>
  <p id="taxBreak" style="margin-top:14px;font-size:13px;color:#475569;padding:10px;background:#f8fafc;border-radius:6px;line-height:1.8"></p>
</div>"""

SALES_SCRIPT = """
function setStateRate(){
  const v=document.getElementById('state').value;
  document.getElementById('stateRate').value=v;
}
function calc(){
  const amt=parseFloat(document.getElementById('amount').value)||0;
  const sr=(parseFloat(document.getElementById('stateRate').value)||0)/100;
  const lr=(parseFloat(document.getElementById('localRate').value)||0)/100;
  const rate=sr+lr;
  const mode=document.getElementById('mode').value;
  let pre,tax,total;
  if(mode==='add'){pre=amt;tax=amt*rate;total=amt+tax;}
  else{total=amt;pre=amt/(1+rate);tax=total-pre;}
  const stateTax=pre*sr; const localTax=pre*lr;
  document.getElementById('result').style.display='block';
  document.getElementById('preAmt').textContent='$'+pre.toFixed(2);
  document.getElementById('taxAmt').textContent='$'+tax.toFixed(2);
  document.getElementById('totalAmt').textContent='$'+total.toFixed(2);
  const br=document.getElementById('taxBreak');
  if(br) br.innerHTML='State tax: $'+stateTax.toFixed(2)+' ('+((sr*100).toFixed(3))+'%)<br>Local tax: $'+localTax.toFixed(2)+' ('+((lr*100).toFixed(3))+'%)<br>Combined rate: '+((rate*100).toFixed(3))+'%';
}
"""

c = load('sales-tax-calculator.html')
old_result = '<div id="result" class="preview-card" style="display:none">\n  <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;text-align:center">'
c2 = replace_form(c, VAT_OLD_FORM, SALES_NEW_FORM)
if c2:
    # Replace result section too
    old_res_end = '</div>\n</div>'
    # Find and replace the result card
    c2 = re.sub(
        r'<div id="result" class="preview-card" style="display:none">.*?</div>\s*</div>',
        SALES_RESULT,
        c2, count=1, flags=re.DOTALL
    )
    c2 = replace_script(c2, SALES_SCRIPT)
    save('sales-tax-calculator.html', c2)
    changed += 1
    print('sales-tax-calculator.html: DONE')
else:
    print('sales-tax-calculator.html: FORM NO MATCH')

# ── 1d. tax-calculator.html — keep generic but add inclusive/exclusive toggle + breakdown ──
TAX_SCRIPT = """
function calc(){
  const amt=parseFloat(document.getElementById('amount').value)||0;
  const rate=(parseFloat(document.getElementById('rate').value)||0)/100;
  const mode=document.getElementById('mode').value;
  let pre,tax,total;
  if(mode==='add'){pre=amt;tax=amt*rate;total=amt+tax;}
  else{total=amt;pre=amt/(1+rate);tax=total-pre;}
  const effectiveRate=(pre>0?tax/pre*100:0).toFixed(3);
  const inclusiveRate=(total>0?tax/total*100:0).toFixed(3);
  document.getElementById('result').style.display='block';
  document.getElementById('preAmt').textContent='$'+pre.toFixed(2);
  document.getElementById('taxAmt').textContent='$'+tax.toFixed(2)+' ('+effectiveRate+'% of net)';
  document.getElementById('totalAmt').textContent='$'+total.toFixed(2)+' (tax is '+inclusiveRate+'% inclusive)';
}
"""
# tax-calculator.html - add inclusive rate info to script only (form is already different enough from vat)
c = load('tax-calculator.html')
c2 = replace_script(c, TAX_SCRIPT)
save('tax-calculator.html', c2)
changed += 1
print('tax-calculator.html: DONE (script enhanced)')


# ═══════════════════════════════════════════════════════════
# GROUP 2: ESTIMATE / QUOTE TOOLS (10 tools)
# All share generateQuote() with basic line items + taxRate
# ═══════════════════════════════════════════════════════════

ESTIMATE_OLD_SCRIPT_MARKER = 'function generateQuote(){'

# Common helper
COMMON_QUOTE_HEADER = '''function addRow(){
  const tb=document.getElementById('lineItems');
  const tr=document.createElement('tr');
  tr.innerHTML=`<td><input type="text" placeholder="Description" style="width:100%;padding:6px;border:1px solid #e2e8f0;border-radius:6px;font-size:13px"></td>
    <td><input type="number" value="1" min="0" oninput="calcTotals()" style="width:60px;padding:6px;border:1px solid #e2e8f0;border-radius:6px;font-size:13px"></td>
    <td><input type="number" value="0" min="0" step="0.01" oninput="calcTotals()" style="width:90px;padding:6px;border:1px solid #e2e8f0;border-radius:6px;font-size:13px"></td>
    <td id="rt" style="text-align:right;padding:6px;font-size:13px">$0.00</td>
    <td><button onclick="this.closest('tr').remove();calcTotals()" style="background:#fee2e2;color:#dc2626;border:none;border-radius:4px;padding:4px 8px;cursor:pointer">✕</button></td>`;
  tb.appendChild(tr);calcTotals();
}
function calcTotals(){
  let sub=0;
  document.querySelectorAll('#lineItems tr').forEach(tr=>{
    const inputs=tr.querySelectorAll('input');if(inputs.length<3)return;
    const tot=(parseFloat(inputs[1].value)||0)*(parseFloat(inputs[2].value)||0);
    const td=tr.querySelector('#rt')||tr.cells[3];if(td)td.textContent='$'+tot.toFixed(2);
    sub+=tot;
  });
  const disc=(parseFloat((document.getElementById('discount')||{value:0}).value)||0)/100;
  const discAmt=sub*disc;
  const tax=(parseFloat(document.getElementById('taxRate').value)||0)/100;
  const taxAmt=(sub-discAmt)*tax;
  const total=sub-discAmt+taxAmt;
  document.getElementById('subtotal').textContent='$'+sub.toFixed(2);
  if(document.getElementById('discountAmt'))document.getElementById('discountAmt').textContent='-$'+discAmt.toFixed(2);
  document.getElementById('taxAmt').textContent='$'+taxAmt.toFixed(2);
  document.getElementById('totalAmt').textContent='$'+total.toFixed(2);
}
function copyText(){navigator.clipboard.writeText(document.getElementById('preview').textContent);}
'''

ESTIMATE_SPECS = {

'cleaning-estimate.html': {
'extra_form': '''<div class="field"><label>Service Type</label><select id="serviceType"><option value="standard">Standard Clean</option><option value="deep">Deep Clean (+30%)</option><option value="moveout">Move-Out Clean (+50%)</option><option value="postcon">Post-Construction (+75%)</option></select></div>
<div class="field"><label>Property Size (sq ft)</label><input id="sqft" type="number" value="1200" step="100" min="0"></div>
<div class="field"><label>Number of Rooms</label><input id="rooms" type="number" value="4" step="1" min="1"></div>
<div class="field"><label>Supplies Cost ($)</label><input id="supplies" type="number" value="0" step="5" min="0"></div>''',
'script_extra': '''
function generateQuote(){
  const from=document.getElementById('from').value||'Your Business';
  const to=document.getElementById('to').value||'Client';
  const qNum=document.getElementById('qNum').value||'EST-001';
  const date=document.getElementById('qDate').value||new Date().toISOString().split('T')[0];
  const valid=document.getElementById('valid').value||'30';
  const stype=document.getElementById('serviceType');
  const serviceLabel=stype?stype.options[stype.selectedIndex].text:'Standard Clean';
  const mult={'standard':1,'deep':1.3,'moveout':1.5,'postcon':1.75};
  const smult=mult[stype?stype.value:'standard']||1;
  const sqft=parseFloat(document.getElementById('sqft').value)||0;
  const rooms=parseFloat(document.getElementById('rooms').value)||0;
  const supplies=parseFloat(document.getElementById('supplies').value)||0;
  let lines='';let sub=0;
  document.querySelectorAll('#lineItems tr').forEach(tr=>{
    const inputs=tr.querySelectorAll('input');if(inputs.length<3)return;
    const desc=inputs[0].value||'Item';const qty=parseFloat(inputs[1].value)||0;const rate=parseFloat(inputs[2].value)||0;
    const adj=qty*rate*smult;lines+=(desc+' ('+serviceLabel+')').padEnd(32)+' $'+adj.toFixed(2)+'\n';sub+=adj;
  });
  if(supplies>0){lines+='Supplies & Materials'.padEnd(32)+' $'+supplies.toFixed(2)+'\n';sub+=supplies;}
  const tax=(parseFloat(document.getElementById('taxRate').value)||0)/100;
  const taxAmt=sub*tax;const total=sub+taxAmt;
  document.getElementById('output').style.display='block';
  document.getElementById('preview').textContent=
`CLEANING SERVICE ESTIMATE
${'='.repeat(50)}
From: ${from}
To:   ${to}
Est. #: ${qNum}   Date: ${date}   Valid: ${valid} days
Service: ${serviceLabel}   Area: ${sqft} sq ft   Rooms: ${rooms}
${'─'.repeat(50)}
${lines}${'─'.repeat(50)}
Subtotal: $${sub.toFixed(2)}
Tax:      $${taxAmt.toFixed(2)}
${'─'.repeat(50)}
TOTAL:    $${total.toFixed(2)}
${'='.repeat(50)}`;
}
'''
},

'construction-estimate.html': {
'extra_form': '''<div class="field"><label>Labor Hours</label><input id="laborHours" type="number" value="40" step="1" min="0"></div>
<div class="field"><label>Labor Rate ($/hr)</label><input id="laborRate" type="number" value="75" step="5" min="0"></div>
<div class="field"><label>Materials Budget ($)</label><input id="materials" type="number" value="0" step="100" min="0"></div>
<div class="field"><label>Permit / Inspection Fees ($)</label><input id="permits" type="number" value="0" step="50" min="0"></div>
<div class="field"><label>Contingency (%)</label><input id="contingency" type="number" value="10" step="1" min="0"></div>
<div class="field"><label>Markup (%)</label><input id="markup" type="number" value="15" step="1" min="0"></div>''',
'script_extra': '''
function generateQuote(){
  const from=document.getElementById('from').value||'Your Business';
  const to=document.getElementById('to').value||'Client';
  const qNum=document.getElementById('qNum').value||'EST-001';
  const date=document.getElementById('qDate').value||new Date().toISOString().split('T')[0];
  const valid=document.getElementById('valid').value||'30';
  const lh=parseFloat(document.getElementById('laborHours').value)||0;
  const lr=parseFloat(document.getElementById('laborRate').value)||0;
  const mats=parseFloat(document.getElementById('materials').value)||0;
  const permits=parseFloat(document.getElementById('permits').value)||0;
  const cont=(parseFloat(document.getElementById('contingency').value)||0)/100;
  const markup=(parseFloat(document.getElementById('markup').value)||0)/100;
  let linesSub=0; let linesText='';
  document.querySelectorAll('#lineItems tr').forEach(tr=>{
    const inputs=tr.querySelectorAll('input');if(inputs.length<3)return;
    const desc=inputs[0].value||'Item';const qty=parseFloat(inputs[1].value)||0;const rate=parseFloat(inputs[2].value)||0;
    const tot=qty*rate;linesText+=desc.padEnd(30)+' $'+tot.toFixed(2)+'\n';linesSub+=tot;
  });
  const labor=lh*lr;
  const baseCost=linesSub+labor+mats+permits;
  const contAmt=baseCost*cont;
  const markupAmt=(baseCost+contAmt)*markup;
  const sub=baseCost+contAmt+markupAmt;
  const tax=(parseFloat(document.getElementById('taxRate').value)||0)/100;
  const taxAmt=sub*tax;const total=sub+taxAmt;
  document.getElementById('output').style.display='block';
  document.getElementById('preview').textContent=
`CONSTRUCTION ESTIMATE
${'='.repeat(50)}
From: ${from}    To: ${to}
Est. #: ${qNum}   Date: ${date}   Valid: ${valid} days
${'─'.repeat(50)}
SCOPE OF WORK:
${linesText}LABOR: ${lh} hrs @ $${lr}/hr          $${labor.toFixed(2)}
MATERIALS:                        $${mats.toFixed(2)}
PERMITS / INSPECTIONS:            $${permits.toFixed(2)}
${'─'.repeat(50)}
Base Cost:                        $${baseCost.toFixed(2)}
Contingency (${(cont*100).toFixed(0)}%):              $${contAmt.toFixed(2)}
Markup (${(markup*100).toFixed(0)}%):                  $${markupAmt.toFixed(2)}
Tax:                              $${taxAmt.toFixed(2)}
${'─'.repeat(50)}
TOTAL ESTIMATE:                   $${total.toFixed(2)}
${'='.repeat(50)}`;
}
'''
},

'repair-estimate.html': {
'extra_form': '''<div class="field"><label>Diagnostic / Inspection Fee ($)</label><input id="diagFee" type="number" value="0" step="10" min="0"></div>
<div class="field"><label>Parts / Components ($)</label><input id="parts" type="number" value="0" step="10" min="0"></div>
<div class="field"><label>Labor Hours</label><input id="laborHours" type="number" value="2" step="0.5" min="0"></div>
<div class="field"><label>Labor Rate ($/hr)</label><input id="laborRate" type="number" value="85" step="5" min="0"></div>
<div class="field"><label>Warranty Period</label><select id="warranty"><option value="none">No Warranty</option><option value="30">30 Days</option><option value="90">90 Days</option><option value="180">6 Months</option><option value="365">1 Year</option></select></div>''',
'script_extra': '''
function generateQuote(){
  const from=document.getElementById('from').value||'Your Business';
  const to=document.getElementById('to').value||'Client';
  const qNum=document.getElementById('qNum').value||'REP-001';
  const date=document.getElementById('qDate').value||new Date().toISOString().split('T')[0];
  const valid=document.getElementById('valid').value||'30';
  const diag=parseFloat(document.getElementById('diagFee').value)||0;
  const parts=parseFloat(document.getElementById('parts').value)||0;
  const lh=parseFloat(document.getElementById('laborHours').value)||0;
  const lr=parseFloat(document.getElementById('laborRate').value)||0;
  const wEl=document.getElementById('warranty');
  const warranty=wEl?wEl.options[wEl.selectedIndex].text:'None';
  let linesSub=0;let linesText='';
  document.querySelectorAll('#lineItems tr').forEach(tr=>{
    const inputs=tr.querySelectorAll('input');if(inputs.length<3)return;
    const desc=inputs[0].value||'Item';const qty=parseFloat(inputs[1].value)||0;const rate=parseFloat(inputs[2].value)||0;
    const tot=qty*rate;linesText+=desc.padEnd(30)+' $'+tot.toFixed(2)+'\n';linesSub+=tot;
  });
  const labor=lh*lr;
  const sub=linesSub+diag+parts+labor;
  const tax=(parseFloat(document.getElementById('taxRate').value)||0)/100;
  const taxAmt=sub*tax;const total=sub+taxAmt;
  document.getElementById('output').style.display='block';
  document.getElementById('preview').textContent=
`REPAIR ESTIMATE
${'='.repeat(50)}
From: ${from}    To: ${to}
Est. #: ${qNum}   Date: ${date}   Valid: ${valid} days
${'─'.repeat(50)}
DESCRIPTION OF REPAIR:
${linesText}
Diagnostic / Inspection Fee:      $${diag.toFixed(2)}
Parts & Components:               $${parts.toFixed(2)}
Labor: ${lh} hrs @ $${lr}/hr       $${labor.toFixed(2)}
${'─'.repeat(50)}
Subtotal:                         $${sub.toFixed(2)}
Tax:                              $${taxAmt.toFixed(2)}
TOTAL:                            $${total.toFixed(2)}
${'─'.repeat(50)}
Warranty: ${warranty}
Note: Estimate valid for ${valid} days. Final cost may vary if additional faults are discovered during repair.
${'='.repeat(50)}`;
}
'''
},

'job-estimate.html': {
'extra_form': '''<div class="field"><label>Job Category</label><select id="jobCat"><option value="service">Service</option><option value="install">Installation</option><option value="maintenance">Maintenance</option><option value="consulting">Consulting</option><option value="delivery">Delivery</option></select></div>
<div class="field"><label>Estimated Hours</label><input id="estHours" type="number" value="8" step="0.5" min="0"></div>
<div class="field"><label>Hourly Rate ($)</label><input id="hourlyRate" type="number" value="65" step="5" min="0"></div>
<div class="field"><label>Overhead (%)</label><input id="overhead" type="number" value="20" step="1" min="0"></div>
<div class="field"><label>Profit Margin (%)</label><input id="profitMargin" type="number" value="15" step="1" min="0"></div>''',
'script_extra': '''
function generateQuote(){
  const from=document.getElementById('from').value||'Your Business';
  const to=document.getElementById('to').value||'Client';
  const qNum=document.getElementById('qNum').value||'JOB-001';
  const date=document.getElementById('qDate').value||new Date().toISOString().split('T')[0];
  const valid=document.getElementById('valid').value||'30';
  const catEl=document.getElementById('jobCat');
  const cat=catEl?catEl.options[catEl.selectedIndex].text:'Service';
  const hrs=parseFloat(document.getElementById('estHours').value)||0;
  const hr=parseFloat(document.getElementById('hourlyRate').value)||0;
  const ovhPct=(parseFloat(document.getElementById('overhead').value)||0)/100;
  const profPct=(parseFloat(document.getElementById('profitMargin').value)||0)/100;
  let linesSub=0;let linesText='';
  document.querySelectorAll('#lineItems tr').forEach(tr=>{
    const inputs=tr.querySelectorAll('input');if(inputs.length<3)return;
    const desc=inputs[0].value||'Item';const qty=parseFloat(inputs[1].value)||0;const rate=parseFloat(inputs[2].value)||0;
    const tot=qty*rate;linesText+=desc.padEnd(30)+' $'+tot.toFixed(2)+'\n';linesSub+=tot;
  });
  const labor=hrs*hr;
  const dirCost=linesSub+labor;
  const ovhAmt=dirCost*ovhPct;
  const profAmt=(dirCost+ovhAmt)*profPct;
  const sub=dirCost+ovhAmt+profAmt;
  const tax=(parseFloat(document.getElementById('taxRate').value)||0)/100;
  const taxAmt=sub*tax;const total=sub+taxAmt;
  document.getElementById('output').style.display='block';
  document.getElementById('preview').textContent=
`JOB ESTIMATE — ${cat.toUpperCase()}
${'='.repeat(50)}
From: ${from}    To: ${to}
Est. #: ${qNum}   Date: ${date}   Valid: ${valid} days
${'─'.repeat(50)}
SCOPE:
${linesText}Labor: ${hrs} hrs @ $${hr}/hr            $${labor.toFixed(2)}
Overhead (${(ovhPct*100).toFixed(0)}%):                $${ovhAmt.toFixed(2)}
Profit Margin (${(profPct*100).toFixed(0)}%):         $${profAmt.toFixed(2)}
Tax:                              $${taxAmt.toFixed(2)}
${'─'.repeat(50)}
TOTAL JOB ESTIMATE:               $${total.toFixed(2)}
${'='.repeat(50)}`;
}
'''
},

'price-quote.html': {
'extra_form': '''<div class="field"><label>Currency</label><select id="currency"><option value="USD">USD $</option><option value="EUR">EUR €</option><option value="GBP">GBP £</option><option value="CAD">CAD $</option></select></div>
<div class="field"><label>Bulk Discount Threshold (units)</label><input id="bulkThresh" type="number" value="10" step="1" min="0" placeholder="Qty to trigger discount"></div>
<div class="field"><label>Bulk Discount (%)</label><input id="bulkDisc" type="number" value="5" step="0.5" min="0"></div>
<div class="field"><label>Additional Discount (%)</label><input id="extraDisc" type="number" value="0" step="0.5" min="0" placeholder="Manual override"></div>''',
'script_extra': '''
const syms={USD:'$',EUR:'€',GBP:'£',CAD:'CA$'};
function generateQuote(){
  const from=document.getElementById('from').value||'Your Business';
  const to=document.getElementById('to').value||'Client';
  const qNum=document.getElementById('qNum').value||'PQ-001';
  const date=document.getElementById('qDate').value||new Date().toISOString().split('T')[0];
  const valid=document.getElementById('valid').value||'30';
  const cur=document.getElementById('currency').value;
  const sym=syms[cur]||'$';
  const bulkT=parseFloat(document.getElementById('bulkThresh').value)||10;
  const bulkD=(parseFloat(document.getElementById('bulkDisc').value)||0)/100;
  const extraD=(parseFloat(document.getElementById('extraDisc').value)||0)/100;
  let sub=0;let linesText='';let bulkApplied=false;
  document.querySelectorAll('#lineItems tr').forEach(tr=>{
    const inputs=tr.querySelectorAll('input');if(inputs.length<3)return;
    const desc=inputs[0].value||'Item';const qty=parseFloat(inputs[1].value)||0;const rate=parseFloat(inputs[2].value)||0;
    const isBulk=qty>=bulkT;if(isBulk)bulkApplied=true;
    const disc=isBulk?bulkD:0;const effRate=rate*(1-disc);
    const tot=qty*effRate;
    linesText+=desc.padEnd(26)+' x'+qty+(isBulk?' *bulk*':'       ')+'  '+sym+effRate.toFixed(2)+'  '+sym+tot.toFixed(2)+'\n';
    sub+=tot;
  });
  const extraAmt=sub*extraD;const discSub=sub-extraAmt;
  const tax=(parseFloat(document.getElementById('taxRate').value)||0)/100;
  const taxAmt=discSub*tax;const total=discSub+taxAmt;
  document.getElementById('output').style.display='block';
  document.getElementById('preview').textContent=
`PRICE QUOTE (${cur})
${'='.repeat(50)}
From: ${from}    To: ${to}
Quote #: ${qNum}   Date: ${date}   Valid: ${valid} days
${'─'.repeat(50)}
DESCRIPTION               QTY          RATE    AMOUNT
${'─'.repeat(50)}
${linesText}${bulkApplied?'* Bulk discount ('+Math.round(bulkD*100)+'%) applied for qty ≥'+bulkThresh+'\n':''}${'─'.repeat(50)}
Subtotal:          ${sym}${sub.toFixed(2)}
Extra Discount:   -${sym}${extraAmt.toFixed(2)}
Tax:               ${sym}${taxAmt.toFixed(2)}
${'─'.repeat(50)}
TOTAL (${cur}):     ${sym}${total.toFixed(2)}
${'='.repeat(50)}`;
}
'''
},

'project-quote.html': {
'extra_form': '''<div class="field"><label>Project Phase</label><select id="phase"><option value="discovery">Discovery / Planning</option><option value="design">Design</option><option value="development">Development / Build</option><option value="testing">Testing / QA</option><option value="delivery">Delivery / Launch</option><option value="maintenance">Maintenance</option></select></div>
<div class="field"><label>Payment Schedule</label><select id="paySchedule"><option value="50_50">50% upfront, 50% on completion</option><option value="3rd">3 equal instalments</option><option value="milestone">Per milestone</option><option value="full">100% upfront</option><option value="net30">Net 30 on completion</option></select></div>
<div class="field"><label>Rush Fee (%)</label><input id="rushFee" type="number" value="0" step="5" min="0" placeholder="0 = standard timeline"></div>''',
'script_extra': '''
function generateQuote(){
  const from=document.getElementById('from').value||'Your Business';
  const to=document.getElementById('to').value||'Client';
  const qNum=document.getElementById('qNum').value||'PRJ-001';
  const date=document.getElementById('qDate').value||new Date().toISOString().split('T')[0];
  const valid=document.getElementById('valid').value||'30';
  const phEl=document.getElementById('phase');
  const phase=phEl?phEl.options[phEl.selectedIndex].text:'Project';
  const psEl=document.getElementById('paySchedule');
  const ps=psEl?psEl.options[psEl.selectedIndex].text:'On completion';
  const rush=(parseFloat(document.getElementById('rushFee').value)||0)/100;
  let sub=0;let linesText='';
  document.querySelectorAll('#lineItems tr').forEach(tr=>{
    const inputs=tr.querySelectorAll('input');if(inputs.length<3)return;
    const desc=inputs[0].value||'Item';const qty=parseFloat(inputs[1].value)||0;const rate=parseFloat(inputs[2].value)||0;
    const tot=qty*rate;linesText+=desc.padEnd(30)+' $'+tot.toFixed(2)+'\n';sub+=tot;
  });
  const rushAmt=sub*rush;
  const subtotal=sub+rushAmt;
  const tax=(parseFloat(document.getElementById('taxRate').value)||0)/100;
  const taxAmt=subtotal*tax;const total=subtotal+taxAmt;
  const dep50=total*0.5;const dep33=total/3;
  const pmNote=ps.includes('50%')?'Deposit due: $'+dep50.toFixed(2)+' | Balance: $'+dep50.toFixed(2):ps.includes('3')?'Instalment 1: $'+dep33.toFixed(2)+' | x3':'See agreed schedule';
  document.getElementById('output').style.display='block';
  document.getElementById('preview').textContent=
`PROJECT QUOTE — ${phase.toUpperCase()}
${'='.repeat(50)}
From: ${from}    To: ${to}
Quote #: ${qNum}   Date: ${date}   Valid: ${valid} days
${'─'.repeat(50)}
DELIVERABLES:
${linesText}${rush>0?'Rush Fee ('+Math.round(rush*100)+'%):              $'+rushAmt.toFixed(2)+'\n':''}Tax:                              $${taxAmt.toFixed(2)}
${'─'.repeat(50)}
PROJECT TOTAL:                    $${total.toFixed(2)}
Payment: ${ps}
${pmNote}
${'='.repeat(50)}`;
}
'''
},

'sales-quote.html': {
'extra_form': '''<div class="field"><label>Shipping & Handling ($)</label><input id="shipping" type="number" value="0" step="5" min="0"></div>
<div class="field"><label>Payment Terms</label><select id="payTerms"><option value="immediate">Payment on Order</option><option value="net15">Net 15</option><option value="net30">Net 30</option><option value="net60">Net 60</option><option value="cod">Cash on Delivery</option></select></div>
<div class="field"><label>Purchase Order # (optional)</label><input id="poNum" type="text" placeholder="PO-12345"></div>
<div class="field"><label>Early Payment Discount (%)</label><input id="earlyDisc" type="number" value="0" step="0.5" min="0" placeholder="e.g. 2% if paid in 10 days"></div>''',
'script_extra': '''
function generateQuote(){
  const from=document.getElementById('from').value||'Your Business';
  const to=document.getElementById('to').value||'Client';
  const qNum=document.getElementById('qNum').value||'SQ-001';
  const date=document.getElementById('qDate').value||new Date().toISOString().split('T')[0];
  const valid=document.getElementById('valid').value||'30';
  const shipping=parseFloat(document.getElementById('shipping').value)||0;
  const ptEl=document.getElementById('payTerms');
  const pt=ptEl?ptEl.options[ptEl.selectedIndex].text:'Net 30';
  const po=document.getElementById('poNum').value;
  const earlyD=(parseFloat(document.getElementById('earlyDisc').value)||0);
  let sub=0;let linesText='';
  document.querySelectorAll('#lineItems tr').forEach(tr=>{
    const inputs=tr.querySelectorAll('input');if(inputs.length<3)return;
    const desc=inputs[0].value||'Product';const qty=parseFloat(inputs[1].value)||0;const rate=parseFloat(inputs[2].value)||0;
    const tot=qty*rate;linesText+=desc.padEnd(28)+' x'+qty+'  $'+rate.toFixed(2)+'  $'+tot.toFixed(2)+'\n';sub+=tot;
  });
  const tax=(parseFloat(document.getElementById('taxRate').value)||0)/100;
  const taxAmt=sub*tax;const total=sub+taxAmt+shipping;
  const earlyTotal=earlyD>0?total*(1-earlyD/100):0;
  document.getElementById('output').style.display='block';
  document.getElementById('preview').textContent=
`SALES QUOTE
${'='.repeat(50)}
From: ${from}    To: ${to}
Quote #: ${qNum}   Date: ${date}   Valid: ${valid} days${po?'\nPO Reference: '+po:''}
${'─'.repeat(50)}
PRODUCT / DESCRIPTION        QTY   UNIT PRICE  TOTAL
${'─'.repeat(50)}
${linesText}${'─'.repeat(50)}
Subtotal:         $${sub.toFixed(2)}
Tax:              $${taxAmt.toFixed(2)}
Shipping:         $${shipping.toFixed(2)}
${'─'.repeat(50)}
TOTAL DUE:        $${total.toFixed(2)}
Payment Terms:    ${pt}${earlyD>0?'\nEarly Payment:    $'+earlyTotal.toFixed(2)+' if paid within 10 days ('+earlyD+'% discount)':''}
${'='.repeat(50)}`;
}
'''
},

'service-quote.html': {
'extra_form': '''<div class="field"><label>Pricing Model</label><select id="priceModel" onchange="toggleModel()"><option value="hourly">Hourly Rate</option><option value="flat">Flat Rate / Fixed Fee</option><option value="retainer">Monthly Retainer</option></select></div>
<div class="field"><label>Hourly Rate ($) or Monthly Fee ($)</label><input id="baseRate" type="number" value="100" step="10" min="0"></div>
<div class="field"><label>Estimated Hours (if hourly)</label><input id="estHours" type="number" value="10" step="0.5" min="0"></div>
<div class="field"><label>Recurring Billing</label><select id="recurring"><option value="once">One-time</option><option value="monthly">Monthly</option><option value="quarterly">Quarterly</option><option value="annual">Annual</option></select></div>''',
'script_extra': '''
function generateQuote(){
  const from=document.getElementById('from').value||'Your Business';
  const to=document.getElementById('to').value||'Client';
  const qNum=document.getElementById('qNum').value||'SVC-001';
  const date=document.getElementById('qDate').value||new Date().toISOString().split('T')[0];
  const valid=document.getElementById('valid').value||'30';
  const pmEl=document.getElementById('priceModel');
  const model=pmEl?pmEl.value:'hourly';
  const modelLabel=pmEl?pmEl.options[pmEl.selectedIndex].text:'Hourly Rate';
  const baseRate=parseFloat(document.getElementById('baseRate').value)||0;
  const hrs=parseFloat(document.getElementById('estHours').value)||0;
  const recEl=document.getElementById('recurring');
  const rec=recEl?recEl.options[recEl.selectedIndex].text:'One-time';
  let serviceCost=0;
  if(model==='hourly')serviceCost=baseRate*hrs;
  else serviceCost=baseRate;
  let linesSub=0;let linesText='';
  document.querySelectorAll('#lineItems tr').forEach(tr=>{
    const inputs=tr.querySelectorAll('input');if(inputs.length<3)return;
    const desc=inputs[0].value||'Service';const qty=parseFloat(inputs[1].value)||0;const rate=parseFloat(inputs[2].value)||0;
    const tot=qty*rate;linesText+=desc.padEnd(30)+' $'+tot.toFixed(2)+'\n';linesSub+=tot;
  });
  const sub=serviceCost+linesSub;
  const tax=(parseFloat(document.getElementById('taxRate').value)||0)/100;
  const taxAmt=sub*tax;const total=sub+taxAmt;
  const serviceDesc=model==='hourly'?hrs+' hrs @ $'+baseRate+'/hr = $'+serviceCost.toFixed(2):modelLabel+': $'+serviceCost.toFixed(2);
  document.getElementById('output').style.display='block';
  document.getElementById('preview').textContent=
`SERVICE QUOTE
${'='.repeat(50)}
From: ${from}    To: ${to}
Quote #: ${qNum}   Date: ${date}   Valid: ${valid} days
Pricing: ${modelLabel}   Billing: ${rec}
${'─'.repeat(50)}
SERVICE FEES:
${serviceDesc}
${linesText}${'─'.repeat(50)}
Subtotal:  $${sub.toFixed(2)}
Tax:       $${taxAmt.toFixed(2)}
TOTAL:     $${total.toFixed(2)} (${rec})
${'='.repeat(50)}`;
}
'''
},

'quote-generator.html': {
'extra_form': '''<div class="field"><label>Discount Type</label><select id="discType"><option value="pct">Percentage (%)</option><option value="fixed">Fixed Amount ($)</option></select></div>
<div class="field"><label>Discount Value</label><input id="discValue" type="number" value="0" step="0.01" min="0"></div>
<div class="field"><label>Currency</label><select id="qCur"><option value="USD">USD $</option><option value="EUR">EUR €</option><option value="GBP">GBP £</option><option value="AUD">AUD $</option><option value="CAD">CAD $</option></select></div>''',
'script_extra': '''
const qSyms={USD:'$',EUR:'€',GBP:'£',AUD:'A$',CAD:'CA$'};
function generateQuote(){
  const from=document.getElementById('from').value||'Your Business';
  const to=document.getElementById('to').value||'Client';
  const qNum=document.getElementById('qNum').value||'Q-001';
  const date=document.getElementById('qDate').value||new Date().toISOString().split('T')[0];
  const valid=document.getElementById('valid').value||'30';
  const cur=document.getElementById('qCur').value;
  const sym=qSyms[cur]||'$';
  const dtype=document.getElementById('discType').value;
  const dval=parseFloat(document.getElementById('discValue').value)||0;
  let sub=0;let linesText='';
  document.querySelectorAll('#lineItems tr').forEach(tr=>{
    const inputs=tr.querySelectorAll('input');if(inputs.length<3)return;
    const desc=inputs[0].value||'Item';const qty=parseFloat(inputs[1].value)||0;const rate=parseFloat(inputs[2].value)||0;
    const tot=qty*rate;linesText+=desc.padEnd(28)+' x'+qty+'  '+sym+rate.toFixed(2)+'  '+sym+tot.toFixed(2)+'\n';sub+=tot;
  });
  const discAmt=dtype==='pct'?sub*dval/100:Math.min(dval,sub);
  const discSub=sub-discAmt;
  const tax=(parseFloat(document.getElementById('taxRate').value)||0)/100;
  const taxAmt=discSub*tax;const total=discSub+taxAmt;
  document.getElementById('output').style.display='block';
  document.getElementById('preview').textContent=
`QUOTE (${cur})
${'='.repeat(50)}
From: ${from}    To: ${to}
Quote #: ${qNum}   Date: ${date}   Valid: ${valid} days
${'─'.repeat(50)}
${linesText}${'─'.repeat(50)}
Subtotal:                   ${sym}${sub.toFixed(2)}
Discount${dtype==='pct'?' ('+dval+'%)':''}:         -${sym}${discAmt.toFixed(2)}
Tax:                        ${sym}${taxAmt.toFixed(2)}
${'─'.repeat(50)}
TOTAL (${cur}):              ${sym}${total.toFixed(2)}
${'='.repeat(50)}`;
}
'''
},

'estimate-generator.html': {
'extra_form': '''<div class="field"><label>Discount (%)</label><input id="estDisc" type="number" value="0" step="0.5" min="0"></div>
<div class="field"><label>Estimate Type</label><select id="estType"><option value="estimate">Estimate</option><option value="quote">Quote</option><option value="proposal">Proposal</option><option value="bid">Bid</option></select></div>''',
'script_extra': '''
function generateQuote(){
  const from=document.getElementById('from').value||'Your Business';
  const to=document.getElementById('to').value||'Client';
  const qNum=document.getElementById('qNum').value||'EST-001';
  const date=document.getElementById('qDate').value||new Date().toISOString().split('T')[0];
  const valid=document.getElementById('valid').value||'30';
  const disc=(parseFloat(document.getElementById('estDisc').value)||0)/100;
  const typeEl=document.getElementById('estType');
  const docType=typeEl?typeEl.options[typeEl.selectedIndex].text.toUpperCase():'ESTIMATE';
  let sub=0;let linesText='';
  document.querySelectorAll('#lineItems tr').forEach(tr=>{
    const inputs=tr.querySelectorAll('input');if(inputs.length<3)return;
    const desc=inputs[0].value||'Item';const qty=parseFloat(inputs[1].value)||0;const rate=parseFloat(inputs[2].value)||0;
    const tot=qty*rate;linesText+=desc.padEnd(28)+' x'+qty+'  $'+rate.toFixed(2)+'  $'+tot.toFixed(2)+'\n';sub+=tot;
  });
  const discAmt=sub*disc;const discSub=sub-discAmt;
  const tax=(parseFloat(document.getElementById('taxRate').value)||0)/100;
  const taxAmt=discSub*tax;const total=discSub+taxAmt;
  document.getElementById('output').style.display='block';
  document.getElementById('preview').textContent=
`${docType}
${'='.repeat(50)}
From: ${from}    To: ${to}
#: ${qNum}   Date: ${date}   Valid: ${valid} days
${'─'.repeat(50)}
${linesText}${'─'.repeat(50)}
Subtotal:    $${sub.toFixed(2)}
Discount:   -$${discAmt.toFixed(2)}
Tax:         $${taxAmt.toFixed(2)}
${'─'.repeat(50)}
TOTAL:       $${total.toFixed(2)}
${'='.repeat(50)}`;
}
'''
},

}

# The old extra-form insertion point in estimate tools
EST_EXTRA_ANCHOR = '  <div class="field"><label>Valid for (days)</label><input id="valid" type="number" value="30"></div>\n    <div class="field"><label>Tax Rate (%)</label><input id="taxRate" type="number" value="0" step="0.1" oninput="calcTotals()"></div>'

for fname, spec in ESTIMATE_SPECS.items():
    c = load(fname)
    extra_html = spec['extra_form']
    new_anchor = EST_EXTRA_ANCHOR + '\n    ' + extra_html
    if EST_EXTRA_ANCHOR in c:
        c = c.replace(EST_EXTRA_ANCHOR, new_anchor, 1)
    new_script = COMMON_QUOTE_HEADER + spec['script_extra']
    c = replace_script(c, new_script)
    save(fname, c)
    changed += 1
    print(f'{fname}: DONE')


# ═══════════════════════════════════════════════════════════
# GROUP 3: INVOICE UTILITIES (6 tools)
# All share generateInvoice() with basic invoice form
# ═══════════════════════════════════════════════════════════

INV_OLD_SCRIPT_MARKER = 'function generateInvoice(){'

# Common invoice base script
INV_BASE = '''function addRow(){
  const tb=document.getElementById('lineItems');
  const tr=document.createElement('tr');
  tr.innerHTML=`<td><input type="text" placeholder="Item description" style="width:100%;padding:6px;border:1px solid #e2e8f0;border-radius:6px;font-size:13px"></td>
    <td><input type="number" value="1" min="0" oninput="calcTotals()" style="width:60px;padding:6px;border:1px solid #e2e8f0;border-radius:6px;font-size:13px"></td>
    <td><input type="number" value="0" min="0" step="0.01" oninput="calcTotals()" style="width:90px;padding:6px;border:1px solid #e2e8f0;border-radius:6px;font-size:13px"></td>
    <td id="rt" style="text-align:right;padding:6px;font-size:13px">$0.00</td>
    <td><button onclick="this.closest('tr').remove();calcTotals()" style="background:#fee2e2;color:#dc2626;border:none;border-radius:4px;padding:4px 8px;cursor:pointer">✕</button></td>`;
  tb.appendChild(tr);calcTotals();
}
function calcTotals(){
  let sub=0;
  document.querySelectorAll('#lineItems tr').forEach(tr=>{
    const inputs=tr.querySelectorAll('input');if(inputs.length<3)return;
    const qty=parseFloat(inputs[1].value)||0;const rate=parseFloat(inputs[2].value)||0;
    const tot=qty*rate;const td=tr.querySelector('#rt')||tr.cells[3];if(td)td.textContent='$'+tot.toFixed(2);sub+=tot;
  });
  const disc=(parseFloat(document.getElementById('discount').value)||0)/100;
  const tax=(parseFloat(document.getElementById('taxRate').value)||0)/100;
  const discAmt=sub*disc;const taxAmt=(sub-discAmt)*tax;const total=sub-discAmt+taxAmt;
  document.getElementById('subtotal').textContent='$'+sub.toFixed(2);
  document.getElementById('discountAmt').textContent='-$'+discAmt.toFixed(2);
  document.getElementById('taxAmt').textContent='$'+taxAmt.toFixed(2);
  document.getElementById('totalAmt').textContent='$'+total.toFixed(2);
}
function copyText(){navigator.clipboard.writeText(document.getElementById('preview').textContent);}
'''

# invoice-number-generator.html: auto sequential number + prefix/format
INV_NUM_SCRIPT = INV_BASE + '''
function generateInvoice(){
  const from=document.getElementById('from').value||'Your Business';
  const to=document.getElementById('to').value||'Client';
  const invNum=document.getElementById('invNum').value||'INV-001';
  const date=document.getElementById('invDate').value||new Date().toISOString().split('T')[0];
  const due=document.getElementById('dueDate').value||'';
  const prefix=(document.getElementById('invPrefix')||{value:'INV'}).value||'INV';
  const seq=parseInt((document.getElementById('invSeq')||{value:1}).value)||1;
  const year=new Date().getFullYear();
  const autoNum=prefix+'-'+year+'-'+String(seq).padStart(4,'0');
  const useNum=document.getElementById('invNum').value||autoNum;
  let lines='';let sub=0;
  document.querySelectorAll('#lineItems tr').forEach(tr=>{
    const inputs=tr.querySelectorAll('input');if(inputs.length<3)return;
    const desc=inputs[0].value||'Item';const qty=parseFloat(inputs[1].value)||0;const rate=parseFloat(inputs[2].value)||0;
    const tot=qty*rate;lines+=desc.padEnd(30)+' x'+qty+'  $'+rate.toFixed(2)+'  $'+tot.toFixed(2)+'\n';sub+=tot;
  });
  const disc=(parseFloat(document.getElementById('discount').value)||0)/100;
  const tax=(parseFloat(document.getElementById('taxRate').value)||0)/100;
  const discAmt=sub*disc;const taxAmt=(sub-discAmt)*tax;const total=sub-discAmt+taxAmt;
  const out=document.getElementById('output');out.style.display='block';
  document.getElementById('preview').textContent=
`INVOICE
${'='.repeat(50)}
Invoice Number: ${useNum}   (Auto-Generated: ${autoNum})
From: ${from}
To:   ${to}
Date: ${date}   Due: ${due||'On receipt'}
${'─'.repeat(50)}
${lines}${'─'.repeat(50)}
Subtotal:  $${sub.toFixed(2)}
Discount: -$${discAmt.toFixed(2)}
Tax:       $${taxAmt.toFixed(2)}
${'─'.repeat(50)}
TOTAL DUE: $${total.toFixed(2)}
${'='.repeat(50)}
NEXT INVOICE NUMBER: ${prefix}-${year}-${String(seq+1).padStart(4,'0')}`;
}
'''

# invoice-tracker.html: status tracking + aging
INV_TRACKER_SCRIPT = INV_BASE + '''
const INV_LIST=[];
function generateInvoice(){
  const from=document.getElementById('from').value||'Your Business';
  const to=document.getElementById('to').value||'Client';
  const invNum=document.getElementById('invNum').value||'INV-001';
  const date=document.getElementById('invDate').value||new Date().toISOString().split('T')[0];
  const due=document.getElementById('dueDate').value||'';
  const status=(document.getElementById('invStatus')||{value:'unpaid'}).value||'unpaid';
  let sub=0;
  document.querySelectorAll('#lineItems tr').forEach(tr=>{
    const inputs=tr.querySelectorAll('input');if(inputs.length<3)return;
    const qty=parseFloat(inputs[1].value)||0;const rate=parseFloat(inputs[2].value)||0;sub+=qty*rate;
  });
  const disc=(parseFloat(document.getElementById('discount').value)||0)/100;
  const tax=(parseFloat(document.getElementById('taxRate').value)||0)/100;
  const discAmt=sub*disc;const taxAmt=(sub-discAmt)*tax;const total=sub-discAmt+taxAmt;
  INV_LIST.push({invNum,to,date,due,total,status});
  const today=new Date();
  let aging30=0,aging60=0,aging90=0,aging90plus=0,totalUnpaid=0;
  INV_LIST.filter(i=>i.status==='unpaid'||i.status==='overdue').forEach(i=>{
    const d=i.due?new Date(i.due):new Date(i.date);
    const days=Math.floor((today-d)/(86400000));
    totalUnpaid+=i.total;
    if(days<=30)aging30+=i.total;
    else if(days<=60)aging60+=i.total;
    else if(days<=90)aging90+=i.total;
    else aging90plus+=i.total;
  });
  const statusLabel={paid:'PAID',unpaid:'UNPAID',overdue:'OVERDUE',partial:'PARTIAL'};
  const out=document.getElementById('output');out.style.display='block';
  document.getElementById('preview').textContent=
`INVOICE TRACKER
${'='.repeat(50)}
Invoice: ${invNum}   Client: ${to}
Date: ${date}   Due: ${due||'On receipt'}   Status: ${(statusLabel[status]||status).toUpperCase()}
Amount: $${total.toFixed(2)}
${'─'.repeat(50)}
ACCOUNTS RECEIVABLE AGING SUMMARY
${'─'.repeat(50)}
0-30 days:        $${aging30.toFixed(2)}
31-60 days:       $${aging60.toFixed(2)}
61-90 days:       $${aging90.toFixed(2)}
90+ days:         $${aging90plus.toFixed(2)}
${'─'.repeat(50)}
Total Unpaid:     $${totalUnpaid.toFixed(2)}
Invoices tracked: ${INV_LIST.length}
${'='.repeat(50)}`;
}
'''

# invoice-to-pdf.html: emphasize PDF-ready layout instructions
INV_PDF_SCRIPT = INV_BASE + '''
function generateInvoice(){
  const from=document.getElementById('from').value||'Your Business';
  const to=document.getElementById('to').value||'Client';
  const invNum=document.getElementById('invNum').value||'INV-001';
  const date=document.getElementById('invDate').value||new Date().toISOString().split('T')[0];
  const due=document.getElementById('dueDate').value||'';
  const notes=document.getElementById('notes').value||'';
  const paperSize=(document.getElementById('paperSize')||{value:'letter'}).value||'letter';
  let lines='';let sub=0;
  document.querySelectorAll('#lineItems tr').forEach(tr=>{
    const inputs=tr.querySelectorAll('input');if(inputs.length<3)return;
    const desc=inputs[0].value||'Item';const qty=parseFloat(inputs[1].value)||0;const rate=parseFloat(inputs[2].value)||0;
    const tot=qty*rate;lines+=desc.padEnd(30)+' x'+qty+'  $'+rate.toFixed(2)+'  $'+tot.toFixed(2)+'\n';sub+=tot;
  });
  const disc=(parseFloat(document.getElementById('discount').value)||0)/100;
  const tax=(parseFloat(document.getElementById('taxRate').value)||0)/100;
  const discAmt=sub*disc;const taxAmt=(sub-discAmt)*tax;const total=sub-discAmt+taxAmt;
  const out=document.getElementById('output');out.style.display='block';
  document.getElementById('preview').textContent=
`INVOICE (PDF-READY — ${paperSize.toUpperCase()})
${'='.repeat(50)}
From: ${from}
To:   ${to}
Invoice #: ${invNum}   Date: ${date}   Due: ${due||'On receipt'}
${'─'.repeat(50)}
DESCRIPTION                  QTY   RATE    AMOUNT
${'─'.repeat(50)}
${lines}${'─'.repeat(50)}
Subtotal:  $${sub.toFixed(2)}
Discount: -$${discAmt.toFixed(2)}
Tax:       $${taxAmt.toFixed(2)}
${'─'.repeat(50)}
TOTAL DUE: $${total.toFixed(2)}
${'─'.repeat(50)}
${notes?'Notes: '+notes+'\n':''}To save as PDF: use Print > Save as PDF
Paper: ${paperSize==='a4'?'A4 (210x297mm)':'US Letter (8.5x11in)'}
${'='.repeat(50)}`;
  setTimeout(()=>window.print(),300);
}
'''

# invoice-template-word.html: tabbed layout + Word-copy-friendly output
INV_WORD_SCRIPT = INV_BASE + '''
function generateInvoice(){
  const from=document.getElementById('from').value||'Your Business';
  const to=document.getElementById('to').value||'Client';
  const invNum=document.getElementById('invNum').value||'INV-001';
  const date=document.getElementById('invDate').value||new Date().toISOString().split('T')[0];
  const due=document.getElementById('dueDate').value||'';
  const notes=document.getElementById('notes').value||'Payment due within 30 days.';
  const acct=(document.getElementById('bankAcct')||{value:''}).value||'';
  const bsb=(document.getElementById('bsb')||{value:''}).value||'';
  let lines='';let sub=0;
  document.querySelectorAll('#lineItems tr').forEach(tr=>{
    const inputs=tr.querySelectorAll('input');if(inputs.length<3)return;
    const desc=inputs[0].value||'Item';const qty=parseFloat(inputs[1].value)||0;const rate=parseFloat(inputs[2].value)||0;
    const tot=qty*rate;
    lines+=desc+'\t'+qty+'\t$'+rate.toFixed(2)+'\t$'+tot.toFixed(2)+'\n';sub+=tot;
  });
  const disc=(parseFloat(document.getElementById('discount').value)||0)/100;
  const tax=(parseFloat(document.getElementById('taxRate').value)||0)/100;
  const discAmt=sub*disc;const taxAmt=(sub-discAmt)*tax;const total=sub-discAmt+taxAmt;
  const out=document.getElementById('output');out.style.display='block';
  document.getElementById('preview').textContent=
`INVOICE

Supplier:\t${from}
Client:\t\t${to}
Invoice #:\t${invNum}
Date:\t\t${date}
Due Date:\t${due||'On receipt'}

DESCRIPTION\tQTY\tRATE\tAMOUNT
${'─'.repeat(50)}
${lines}${'─'.repeat(50)}
Subtotal:\t\t\t$${sub.toFixed(2)}
Discount:\t\t\t-$${discAmt.toFixed(2)}
Tax:\t\t\t$${taxAmt.toFixed(2)}
TOTAL DUE:\t\t$${total.toFixed(2)}

${notes}${acct?'\nBank Account: '+acct+(bsb?'  BSB: '+bsb:''):''}

[Tab-separated format — paste into Word/Excel and use "Convert text to table"]`;
}
'''

# invoice-template-excel.html: CSV + formula hints
INV_EXCEL_SCRIPT = INV_BASE + '''
function generateInvoice(){
  const from=document.getElementById('from').value||'Your Business';
  const to=document.getElementById('to').value||'Client';
  const invNum=document.getElementById('invNum').value||'INV-001';
  const date=document.getElementById('invDate').value||new Date().toISOString().split('T')[0];
  const due=document.getElementById('dueDate').value||'';
  const notes=document.getElementById('notes').value||'';
  const taxRate=parseFloat(document.getElementById('taxRate').value)||0;
  const disc=parseFloat(document.getElementById('discount').value)||0;
  let csvLines='Description,Qty,Unit Price,Line Total\n';
  let rows=[];let sub=0;let rowNum=2;
  document.querySelectorAll('#lineItems tr').forEach(tr=>{
    const inputs=tr.querySelectorAll('input');if(inputs.length<3)return;
    const desc=inputs[0].value||'Item';const qty=parseFloat(inputs[1].value)||0;const rate=parseFloat(inputs[2].value)||0;
    const tot=qty*rate;csvLines+='"'+desc+'",'+qty+','+rate.toFixed(2)+',=B'+rowNum+'*C'+rowNum+'\n';sub+=tot;rowNum++;
  });
  const discAmt=sub*disc/100;const taxAmt=(sub-discAmt)*taxRate/100;const total=sub-discAmt+taxAmt;
  const out=document.getElementById('output');out.style.display='block';
  document.getElementById('preview').textContent=
`INVOICE — EXCEL/CSV EXPORT
Invoice #: ${invNum}   Date: ${date}   Due: ${due||'On receipt'}
From: ${from}   To: ${to}
${'─'.repeat(50)}
CSV FORMAT (import into Excel/Google Sheets):
${'─'.repeat(50)}
${csvLines}
,,,Subtotal,,$${sub.toFixed(2)}
,,,Discount (${disc}%),,-$${discAmt.toFixed(2)}
,,,Tax (${taxRate}%),,$${taxAmt.toFixed(2)}
,,,TOTAL DUE,,$${total.toFixed(2)}
${'─'.repeat(50)}
EXCEL FORMULAS:
Line Total: =B2*C2 (copy down)
Subtotal:   =SUM(D2:D${rowNum-1})
Tax:        =Subtotal*(${taxRate}/100)
Total:      =Subtotal+Tax
${notes?'Notes: '+notes:''}`;
}
'''

# invoice-checklist.html: add checklist/compliance section
INV_CHECK_SCRIPT = INV_BASE + '''
function generateInvoice(){
  const from=document.getElementById('from').value||'Your Business';
  const to=document.getElementById('to').value||'Client';
  const invNum=document.getElementById('invNum').value||'INV-001';
  const date=document.getElementById('invDate').value||new Date().toISOString().split('T')[0];
  const due=document.getElementById('dueDate').value||'';
  const notes=document.getElementById('notes').value||'';
  let lines='';let sub=0;
  document.querySelectorAll('#lineItems tr').forEach(tr=>{
    const inputs=tr.querySelectorAll('input');if(inputs.length<3)return;
    const desc=inputs[0].value||'Item';const qty=parseFloat(inputs[1].value)||0;const rate=parseFloat(inputs[2].value)||0;
    const tot=qty*rate;lines+=desc.padEnd(30)+' x'+qty+'  $'+rate.toFixed(2)+'  $'+tot.toFixed(2)+'\n';sub+=tot;
  });
  const disc=(parseFloat(document.getElementById('discount').value)||0)/100;
  const tax=(parseFloat(document.getElementById('taxRate').value)||0)/100;
  const discAmt=sub*disc;const taxAmt=(sub-discAmt)*tax;const total=sub-discAmt+taxAmt;
  // Checklist
  const checks=[
    [!!from,'Supplier name included'],
    [!!to,'Client name / company included'],
    [!!invNum,'Invoice number assigned'],
    [!!date,'Invoice date present'],
    [!!due,'Due date / payment terms set'],
    [sub>0,'At least one line item with amount'],
    [total>0,'Total amount greater than zero'],
    [!!notes,'Payment instructions / notes added'],
  ];
  const checkStr=checks.map(([ok,label])=>(ok?'[x] ':'[ ] ')+label).join('\n');
  const passCount=checks.filter(c=>c[0]).length;
  const out=document.getElementById('output');out.style.display='block';
  document.getElementById('preview').textContent=
`INVOICE + COMPLIANCE CHECKLIST
${'='.repeat(50)}
Invoice #: ${invNum}   Date: ${date}   Due: ${due||'⚠ NOT SET'}
From: ${from}   To: ${to}
${'─'.repeat(50)}
${lines}${'─'.repeat(50)}
Subtotal:  $${sub.toFixed(2)}
Discount: -$${discAmt.toFixed(2)}
Tax:       $${taxAmt.toFixed(2)}
${'─'.repeat(50)}
TOTAL DUE: $${total.toFixed(2)}
${notes?'\nNotes: '+notes:''}
${'─'.repeat(50)}
PRE-SEND CHECKLIST (${passCount}/${checks.length} items complete):
${'─'.repeat(50)}
${checkStr}
${passCount===checks.length?'✓ Invoice ready to send!':'⚠ Please complete all checklist items before sending.'}
${'='.repeat(50)}`;
}
'''

INV_UTIL_SPECS = {
    'invoice-checklist.html': INV_CHECK_SCRIPT,
    'invoice-number-generator.html': INV_NUM_SCRIPT,
    'invoice-template-excel.html': INV_EXCEL_SCRIPT,
    'invoice-template-word.html': INV_WORD_SCRIPT,
    'invoice-to-pdf.html': INV_PDF_SCRIPT,
    'invoice-tracker.html': INV_TRACKER_SCRIPT,
}

INV_EXTRA_FIELDS = {
    'invoice-number-generator.html': '\n    <div class="field"><label>Invoice Prefix</label><input id="invPrefix" type="text" value="INV" placeholder="INV"></div>\n    <div class="field"><label>Starting Sequence #</label><input id="invSeq" type="number" value="1" step="1" min="1"></div>',
    'invoice-to-pdf.html': '\n    <div class="field"><label>Paper Size</label><select id="paperSize"><option value="letter">US Letter</option><option value="a4">A4</option></select></div>',
    'invoice-template-word.html': '\n    <div class="field"><label>Bank Account # (optional)</label><input id="bankAcct" type="text" placeholder="Account number"></div>\n    <div class="field"><label>BSB / Sort Code (optional)</label><input id="bsb" type="text" placeholder="BSB or sort code"></div>',
    'invoice-tracker.html': '\n    <div class="field"><label>Invoice Status</label><select id="invStatus"><option value="unpaid">Unpaid</option><option value="paid">Paid</option><option value="overdue">Overdue</option><option value="partial">Partially Paid</option></select></div>',
}

INV_ANCHOR = '    <div class="field"><label>Tax Rate (%)</label><input id="taxRate" type="number" value="0" step="0.1" oninput="calcTotals()"></div>\n    <div class="field"><label>Discount (%)</label><input id="discount" type="number" value="0" step="0.1" oninput="calcTotals()"></div>'

for fname, script in INV_UTIL_SPECS.items():
    c = load(fname)
    if fname in INV_EXTRA_FIELDS:
        extra = INV_EXTRA_FIELDS[fname]
        if INV_ANCHOR in c:
            c = c.replace(INV_ANCHOR, INV_ANCHOR + extra, 1)
    c = replace_script(c, script)
    save(fname, c)
    changed += 1
    print(f'{fname}: DONE')


# ═══════════════════════════════════════════════════════════
# GROUP 4: RATE / COST TOOLS (3 tools)
# ═══════════════════════════════════════════════════════════

# invoice-calculator.html: late fees + partial payment
INV_CALC_OLD_FORM = """<div class="form-card">
  <h2>Quote Details</h2>"""

c = load('invoice-calculator.html')
# replace script with unique late-fee calculator
INV_CALC_SCRIPT = '''
function addRow(){
  const tb=document.getElementById('lineItems');
  const tr=document.createElement('tr');
  tr.innerHTML=`<td><input type="text" placeholder="Item description" style="width:100%;padding:6px;border:1px solid #e2e8f0;border-radius:6px;font-size:13px"></td>
    <td><input type="number" value="1" min="0" oninput="calcTotals()" style="width:60px;padding:6px;border:1px solid #e2e8f0;border-radius:6px;font-size:13px"></td>
    <td><input type="number" value="0" min="0" step="0.01" oninput="calcTotals()" style="width:90px;padding:6px;border:1px solid #e2e8f0;border-radius:6px;font-size:13px"></td>
    <td id="rt" style="text-align:right;padding:6px;font-size:13px">$0.00</td>
    <td><button onclick="this.closest('tr').remove();calcTotals()" style="background:#fee2e2;color:#dc2626;border:none;border-radius:4px;padding:4px 8px;cursor:pointer">✕</button></td>`;
  tb.appendChild(tr);calcTotals();
}
function calcTotals(){
  let sub=0;
  document.querySelectorAll('#lineItems tr').forEach(tr=>{
    const inputs=tr.querySelectorAll('input');if(inputs.length<3)return;
    const tot=(parseFloat(inputs[1].value)||0)*(parseFloat(inputs[2].value)||0);
    const td=tr.querySelector('#rt')||tr.cells[3];if(td)td.textContent='$'+tot.toFixed(2);sub+=tot;
  });
  const tax=(parseFloat(document.getElementById('taxRate').value)||0)/100;
  const taxAmt=sub*tax;
  document.getElementById('subtotal').textContent='$'+sub.toFixed(2);
  document.getElementById('taxAmt').textContent='$'+taxAmt.toFixed(2);
  document.getElementById('totalAmt').textContent='$'+(sub+taxAmt).toFixed(2);
}
function generateQuote(){
  const from=document.getElementById('from').value||'Your Business';
  const to=document.getElementById('to').value||'Client';
  const qNum=document.getElementById('qNum').value||'INV-001';
  const date=document.getElementById('qDate').value||new Date().toISOString().split('T')[0];
  const valid=document.getElementById('valid').value||'30';
  const lateFeeRate=(parseFloat((document.getElementById('lateFee')||{value:1.5}).value)||1.5)/100;
  const daysOverdue=parseInt((document.getElementById('daysOverdue')||{value:0}).value)||0;
  const partialPaid=parseFloat((document.getElementById('partialPaid')||{value:0}).value)||0;
  let sub=0;let lines='';
  document.querySelectorAll('#lineItems tr').forEach(tr=>{
    const inputs=tr.querySelectorAll('input');if(inputs.length<3)return;
    const desc=inputs[0].value||'Item';const qty=parseFloat(inputs[1].value)||0;const rate=parseFloat(inputs[2].value)||0;
    const tot=qty*rate;lines+=desc.padEnd(28)+' x'+qty+'  $'+rate.toFixed(2)+'  $'+tot.toFixed(2)+'\n';sub+=tot;
  });
  const tax=(parseFloat(document.getElementById('taxRate').value)||0)/100;
  const taxAmt=sub*tax;const invoiceTotal=sub+taxAmt;
  const balance=Math.max(0,invoiceTotal-partialPaid);
  const monthsOverdue=daysOverdue/30;
  const lateFee=daysOverdue>0?balance*lateFeeRate*monthsOverdue:0;
  const totalOwed=balance+lateFee;
  document.getElementById('output').style.display='block';
  document.getElementById('preview').textContent=
`INVOICE CALCULATOR
${'='.repeat(50)}
From: ${from}    To: ${to}
Invoice #: ${qNum}   Date: ${date}   Net: ${valid} days
${'─'.repeat(50)}
${lines}${'─'.repeat(50)}
Subtotal:              $${sub.toFixed(2)}
Tax:                   $${taxAmt.toFixed(2)}
Invoice Total:         $${invoiceTotal.toFixed(2)}
Partial Payment:      -$${partialPaid.toFixed(2)}
Balance:               $${balance.toFixed(2)}
${daysOverdue>0?'Late Fee ('+((lateFeeRate*100).toFixed(2))+'%/mo x '+daysOverdue+' days): $'+lateFee.toFixed(2):'Late Fee: none (not overdue)'}
${'─'.repeat(50)}
TOTAL OWING:           $${totalOwed.toFixed(2)}
${'='.repeat(50)}`;
}
function copyText(){navigator.clipboard.writeText(document.getElementById('preview').textContent);}
'''

c = replace_script(c, INV_CALC_SCRIPT)
# Insert late fee fields
LATE_FEE_EXTRA = '\n    <div class="field"><label>Days Overdue</label><input id="daysOverdue" type="number" value="0" step="1" min="0"></div>\n    <div class="field"><label>Monthly Late Fee (%)</label><input id="lateFee" type="number" value="1.5" step="0.1" min="0"></div>\n    <div class="field"><label>Partial Payment Already Received ($)</label><input id="partialPaid" type="number" value="0" step="10" min="0"></div>'
anchor = '    <div class="field"><label>Tax Rate (%)</label><input id="taxRate" type="number" value="0" step="0.1" oninput="calcTotals()"></div>'
if anchor in c:
    c = c.replace(anchor, anchor + LATE_FEE_EXTRA, 1)
save('invoice-calculator.html', c)
changed += 1
print('invoice-calculator.html: DONE')

# freelance-rate-calculator.html: target income → min hourly rate
FREELANCE_SCRIPT = '''
function calc(){
  const target=parseFloat(document.getElementById('target').value)||0;
  const billableHours=parseFloat(document.getElementById('billableHours').value)||0;
  const expenses=parseFloat(document.getElementById('expenses').value)||0;
  const selfEmpTaxRate=0.1413; // SE tax on 92.35% net
  const incomeTaxEst=0.22; // estimated combined fed+state
  const totalTaxRate=selfEmpTaxRate+incomeTaxEst;
  const grossNeeded=(target+expenses)/(1-totalTaxRate);
  const minRate=billableHours>0?grossNeeded/billableHours:0;
  const halfDayRate=minRate*4;
  const dayRate=minRate*8;
  const weekRate=minRate*billableHours/52;
  const projectMin=minRate*10; // 10hr min project
  document.getElementById('result').style.display='block';
  document.getElementById('r-hourly').textContent='$'+minRate.toFixed(2)+'/hr';
  document.getElementById('r-daily').textContent='$'+dayRate.toFixed(2)+'/day';
  document.getElementById('r-weekly').textContent='$'+weekRate.toFixed(2)+'/wk';
  document.getElementById('r-project').textContent='$'+projectMin.toFixed(2)+' (10hr min)';
  document.getElementById('r-gross').textContent='$'+Math.round(grossNeeded).toLocaleString('en-US');
  document.getElementById('r-note').innerHTML=
    'Gross revenue needed: <strong>$'+Math.round(grossNeeded).toLocaleString('en-US')+'</strong><br>'+
    'SE tax estimate (15.3% on 92.35%): <strong>$'+Math.round(grossNeeded*selfEmpTaxRate).toLocaleString('en-US')+'</strong><br>'+
    'Income tax estimate (22%): <strong>$'+Math.round(grossNeeded*incomeTaxEst).toLocaleString('en-US')+'</strong><br>'+
    'Annual business expenses: <strong>$'+Math.round(expenses).toLocaleString('en-US')+'</strong><br>'+
    'Billable hours used: <strong>'+billableHours+' hrs/yr</strong> ('+Math.round(billableHours/52*10)/10+' hrs/wk avg)';
}
'''

FREELANCE_OLD_FORM = """<div class="form-card">
  <h2>Quote Details</h2>
  <div class="form-grid">
    <div class="field"><label>Your Business</label><input id="from" type="text" placeholder="Your Business Name"></div>
    <div class="field"><label>Client Name</label><input id="to" type="text" placeholder="Client / Company"></div>
    <div class="field"><label>Quote #</label><input id="qNum" type="text" placeholder="Q-001" value="Q-001"></div>
    <div class="field"><label>Date</label><input id="qDate" type="date"></div>
    <div class="field"><label>Valid for (days)</label><input id="valid" type="number" value="30"></div>
    <div class="field"><label>Tax Rate (%)</label><input id="taxRate" type="number" value="0" step="0.1" oninput="calcTotals()"></div>
  </div>
</div>"""

FREELANCE_NEW_FORM = """<div class="form-card">
  <h2>Freelance Rate Calculator</h2>
  <div class="form-grid">
    <div class="field"><label>Desired Annual Take-Home ($)</label><input id="target" type="number" value="80000" step="1000" min="0"></div>
    <div class="field"><label>Billable Hours per Year</label><input id="billableHours" type="number" value="1200" step="50" min="1" placeholder="e.g. 1200 = 23hrs/wk"></div>
    <div class="field"><label>Annual Business Expenses ($)</label><input id="expenses" type="number" value="5000" step="500" min="0" placeholder="software, equipment, etc."></div>
  </div>
  <button class="btn-primary" onclick="calc()">Calculate Minimum Rate</button>
</div>
<div id="result" class="preview-card" style="display:none">
  <h2>Your Minimum Freelance Rates</h2>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
    <div style="padding:14px;background:#f8fafc;border-radius:8px"><div style="font-size:1.4rem;font-weight:800;color:var(--primary)" id="r-hourly">—</div><div style="font-size:12px;color:#475569">Min Hourly Rate</div></div>
    <div style="padding:14px;background:#f8fafc;border-radius:8px"><div style="font-size:1.4rem;font-weight:800" id="r-daily">—</div><div style="font-size:12px;color:#475569">Day Rate (8hrs)</div></div>
    <div style="padding:14px;background:#f8fafc;border-radius:8px"><div style="font-size:1.4rem;font-weight:800" id="r-weekly">—</div><div style="font-size:12px;color:#475569">Weekly Rate</div></div>
    <div style="padding:14px;background:#f8fafc;border-radius:8px"><div style="font-size:1.4rem;font-weight:800" id="r-project">—</div><div style="font-size:12px;color:#475569">Min Project Fee</div></div>
    <div style="padding:14px;background:#f0fdf4;border-radius:8px;grid-column:1/-1"><div style="font-size:1.2rem;font-weight:800;color:#16a34a" id="r-gross">—</div><div style="font-size:12px;color:#475569">Gross Revenue Needed</div></div>
  </div>
  <p id="r-note" style="margin-top:14px;font-size:13px;color:#475569;line-height:1.8;padding:12px;background:#f8fafc;border-radius:6px"></p>
</div>"""

c = load('freelance-rate-calculator.html')
c2 = replace_form(c, FREELANCE_OLD_FORM, FREELANCE_NEW_FORM)
if c2:
    c2 = replace_script(c2, FREELANCE_SCRIPT)
    save('freelance-rate-calculator.html', c2)
    changed += 1
    print('freelance-rate-calculator.html: DONE')
else:
    print('freelance-rate-calculator.html: form no match, script only')
    c = replace_script(c, FREELANCE_SCRIPT)
    save('freelance-rate-calculator.html', c)
    changed += 1

# project-cost-calculator.html: phase-based with overhead + margin
PC_SCRIPT = '''
function addRow(){
  const tb=document.getElementById('lineItems');
  const tr=document.createElement('tr');
  tr.innerHTML=`<td><input type="text" placeholder="Phase / Task" style="width:100%;padding:6px;border:1px solid #e2e8f0;border-radius:6px;font-size:13px"></td>
    <td><input type="number" value="1" min="0" oninput="calcTotals()" style="width:60px;padding:6px;border:1px solid #e2e8f0;border-radius:6px;font-size:13px"></td>
    <td><input type="number" value="0" min="0" step="0.01" oninput="calcTotals()" style="width:90px;padding:6px;border:1px solid #e2e8f0;border-radius:6px;font-size:13px"></td>
    <td id="rt" style="text-align:right;padding:6px;font-size:13px">$0.00</td>
    <td><button onclick="this.closest('tr').remove();calcTotals()" style="background:#fee2e2;color:#dc2626;border:none;border-radius:4px;padding:4px 8px;cursor:pointer">✕</button></td>`;
  tb.appendChild(tr);calcTotals();
}
function calcTotals(){
  let sub=0;
  document.querySelectorAll('#lineItems tr').forEach(tr=>{
    const inputs=tr.querySelectorAll('input');if(inputs.length<3)return;
    const tot=(parseFloat(inputs[1].value)||0)*(parseFloat(inputs[2].value)||0);
    const td=tr.querySelector('#rt')||tr.cells[3];if(td)td.textContent='$'+tot.toFixed(2);sub+=tot;
  });
  const ovh=(parseFloat(document.getElementById('overhead').value)||0)/100;
  const margin=(parseFloat(document.getElementById('margin').value)||0)/100;
  const tax=(parseFloat(document.getElementById('taxRate').value)||0)/100;
  const ovhAmt=sub*ovh; const base=sub+ovhAmt;
  const marginAmt=base*margin; const pretax=base+marginAmt;
  const taxAmt=pretax*tax; const total=pretax+taxAmt;
  document.getElementById('subtotal').textContent='$'+sub.toFixed(2);
  document.getElementById('taxAmt').textContent='$'+taxAmt.toFixed(2);
  document.getElementById('totalAmt').textContent='$'+total.toFixed(2);
  if(document.getElementById('ovhAmt'))document.getElementById('ovhAmt').textContent='$'+ovhAmt.toFixed(2);
  if(document.getElementById('marginAmt'))document.getElementById('marginAmt').textContent='$'+marginAmt.toFixed(2);
}
function generateQuote(){
  const from=document.getElementById('from').value||'Your Business';
  const to=document.getElementById('to').value||'Client';
  const qNum=document.getElementById('qNum').value||'PC-001';
  const date=document.getElementById('qDate').value||new Date().toISOString().split('T')[0];
  const valid=document.getElementById('valid').value||'30';
  const ovhPct=parseFloat(document.getElementById('overhead').value)||0;
  const marginPct=parseFloat(document.getElementById('margin').value)||0;
  let sub=0;let lines='';
  document.querySelectorAll('#lineItems tr').forEach(tr=>{
    const inputs=tr.querySelectorAll('input');if(inputs.length<3)return;
    const desc=inputs[0].value||'Phase';const qty=parseFloat(inputs[1].value)||0;const rate=parseFloat(inputs[2].value)||0;
    const tot=qty*rate;lines+=('Phase: '+desc).padEnd(30)+' $'+tot.toFixed(2)+'\n';sub+=tot;
  });
  const ovhAmt=sub*ovhPct/100; const base=sub+ovhAmt;
  const marginAmt=base*marginPct/100; const pretax=base+marginAmt;
  const tax=(parseFloat(document.getElementById('taxRate').value)||0)/100;
  const taxAmt=pretax*tax; const total=pretax+taxAmt;
  document.getElementById('output').style.display='block';
  document.getElementById('preview').textContent=
`PROJECT COST ESTIMATE
${'='.repeat(50)}
From: ${from}    To: ${to}
Estimate #: ${qNum}   Date: ${date}   Valid: ${valid} days
${'─'.repeat(50)}
PHASE BREAKDOWN:
${lines}${'─'.repeat(50)}
Direct Costs:                     $${sub.toFixed(2)}
Overhead (${ovhPct}%):                $${ovhAmt.toFixed(2)}
Profit Margin (${marginPct}%):         $${marginAmt.toFixed(2)}
Tax:                              $${taxAmt.toFixed(2)}
${'─'.repeat(50)}
TOTAL PROJECT COST:               $${total.toFixed(2)}
Effective Markup: ${sub>0?((total/sub-1)*100).toFixed(1):0}% above direct costs
${'='.repeat(50)}`;
}
function copyText(){navigator.clipboard.writeText(document.getElementById('preview').textContent);}
'''

PC_EXTRA = '\n    <div class="field"><label>Overhead (%)</label><input id="overhead" type="number" value="20" step="1" min="0" oninput="calcTotals()"></div>\n    <div class="field"><label>Profit Margin (%)</label><input id="margin" type="number" value="15" step="1" min="0" oninput="calcTotals()"></div>'
c = load('project-cost-calculator.html')
anchor_pc = '    <div class="field"><label>Tax Rate (%)</label><input id="taxRate" type="number" value="0" step="0.1" oninput="calcTotals()"></div>\n  </div>'
if anchor_pc in c:
    c = c.replace(anchor_pc, '    <div class="field"><label>Tax Rate (%)</label><input id="taxRate" type="number" value="0" step="0.1" oninput="calcTotals()"></div>' + PC_EXTRA + '\n  </div>', 1)
c = replace_script(c, PC_SCRIPT)
save('project-cost-calculator.html', c)
changed += 1
print('project-cost-calculator.html: DONE')

print(f'\n=== BillingFixPro diff complete: {changed} files changed ===')
