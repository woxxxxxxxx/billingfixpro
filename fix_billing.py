"""
BillingFixPro 差异化修复脚本
策略：对每个工具注入专属字段 + 唯一 generateDoc() 逻辑
"""
import os, re, glob
os.chdir(r"C:\Users\Administrator\billingfixpro")

# ─── 通用替换锚点 ──────────────────────────────────────────────────────────
# 1. 在 generate 按钮前插入专属字段
GEN_INV_BTN   = '<button class="btn-primary" onclick="generateInvoice()">Generate Invoice</button>'
GEN_QUOTE_BTN = '<button class="btn-primary" onclick="generateQuote()">Generate Quote</button>'

# 2. 替换整个 <script>...</script> 块 (最后一个，即主逻辑)
SCRIPT_RE = re.compile(r'(<script>)(.*?)(</script>\s*$)', re.DOTALL)

# ─── 共享 JS 基础函数（保留在每个文件） ──────────────────────────────────────
BASE_JS = """
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
    const qty=parseFloat(inputs[1].value)||0,rate=parseFloat(inputs[2].value)||0;
    const tot=qty*rate;
    const td=tr.cells[3];if(td)td.textContent='$'+tot.toFixed(2);sub+=tot;
  });
  const discPct=(parseFloat(document.getElementById('discount')?.value)||0)/100;
  const taxPct=(parseFloat(document.getElementById('taxRate')?.value)||0)/100;
  const discAmt=sub*discPct;const taxAmt=(sub-discAmt)*taxPct;const total=sub-discAmt+taxAmt;
  const el=id=>document.getElementById(id);
  if(el('subtotal'))el('subtotal').textContent='$'+sub.toFixed(2);
  if(el('discountAmt'))el('discountAmt').textContent='-$'+discAmt.toFixed(2);
  if(el('taxAmt'))el('taxAmt').textContent='$'+taxAmt.toFixed(2);
  if(el('totalAmt'))el('totalAmt').textContent='$'+total.toFixed(2);
  EXTRA_CALC
}
function copyText(){navigator.clipboard.writeText(document.getElementById('preview').textContent);}
document.addEventListener('DOMContentLoaded',function(){addRow();addRow();calcTotals();});
window.addEventListener('scroll',function(){var b=document.getElementById('btt');if(b)b.classList.toggle('show',window.scrollY>300);});
document.querySelectorAll('.faq-item h3').forEach(function(q){q.addEventListener('click',function(){this.parentElement.classList.toggle('open');});});
"""

def fmtlines(lines):
    return "\n".join("  "+l for l in lines)

# ─── 各工具组定义 ─────────────────────────────────────────────────────────────
# 格式: { filename_stem: (extra_form_fields, extra_calc_js, generate_fn) }

def std_gen(doc_title, currency="$", extra_header="", extra_body="", extra_footer="", doc_label="INVOICE"):
    """Generate a unique generateInvoice() / generateQuote() for each doc type."""
    return f"""
function generateInvoice(){{generateDoc();}}
function generateQuote(){{generateDoc();}}
function generateDoc(){{
  const from_=document.getElementById('from')?.value||'Your Business';
  const to_=document.getElementById('to')?.value||'Client';
  const num_=document.getElementById('invNum')?.value||document.getElementById('qNum')?.value||'001';
  const date_=document.getElementById('invDate')?.value||document.getElementById('qDate')?.value||new Date().toISOString().split('T')[0];
  const due_=document.getElementById('dueDate')?.value||'';
  const sub=document.getElementById('subtotal')?.textContent||'$0.00';
  const tax=document.getElementById('taxAmt')?.textContent||'$0.00';
  const disc=document.getElementById('discountAmt')?.textContent||'-$0.00';
  const total=document.getElementById('totalAmt')?.textContent||'$0.00';
  const notes=document.getElementById('notes')?.value||'';
  {extra_header}
  let lines='';
  document.querySelectorAll('#lineItems tr').forEach(tr=>{{
    const inputs=tr.querySelectorAll('input');if(inputs.length<3)return;
    const d=inputs[0].value||'Service';const q=parseFloat(inputs[1].value)||0;const r=parseFloat(inputs[2].value)||0;
    lines+=`  ${{d.padEnd(30)}} x${{q}}  {currency}${{r.toFixed(2)}}  {currency}${{(q*r).toFixed(2)}}\\n`;
  }});
  const txt=`{doc_title}
${'='*56}
{doc_label} #: ${{num_}}    Date: ${{date_}}${{due_?'   Due: '+due_:''}}
${{'-'*56}}
From: ${{from_}}
To:   ${{to_}}
{extra_body}${{'-'*56}}
DESCRIPTION                        QTY  UNIT     TOTAL
${{'-'*56}}
${{lines}}${{'-'*56}}
  Subtotal:  ${{sub}}
  Discount:  ${{disc}}
  Tax:       ${{tax}}
${'='*56}
  TOTAL DUE: ${{total}}
${'='*56}
{extra_footer}${{notes?'Notes: '+notes+'\\n':''}}`;
  document.getElementById('preview').textContent=txt;
  document.getElementById('output').style.display='block';
  document.getElementById('output').scrollIntoView({{behavior:'smooth'}});
}}
"""

# ─── GROUP A: Country invoices ──────────────────────────────────────────────
EU_EXTRA_FIELDS = """
    <div class="field"><label>Your VAT Number</label><input id="vatFrom" type="text" placeholder="DE123456789"></div>
    <div class="field"><label>Client VAT Number</label><input id="vatTo" type="text" placeholder="FR987654321"></div>
    <div class="field"><label>Currency</label><select id="currency"><option value="EUR">EUR €</option><option value="GBP">GBP £</option><option value="USD">USD $</option><option value="CHF">CHF</option></select></div>
    <div class="field"><label>VAT Rate (%)</label><input id="vatRate" type="number" value="20" step="0.5" oninput="calcTotals()"></div>
    <div class="field full"><label>Reverse Charge</label><select id="reverseCharge"><option value="no">No — VAT applied normally</option><option value="yes">Yes — Reverse Charge (B2B cross-border)</option></select></div>"""

EU_CALC_EXTRA = """
  const vatPct=(parseFloat(document.getElementById('vatRate')?.value)||0)/100;
  const rc=document.getElementById('reverseCharge')?.value==='yes';
  const cur=document.getElementById('currency')?.value||'EUR';
  const vatAmt=rc?0:sub*vatPct;
  const vatEl=document.getElementById('vatBreakdown');
  if(vatEl)vatEl.textContent=rc?cur+' 0.00 (Reverse Charge)':cur+' '+vatAmt.toFixed(2)+' @ '+(vatPct*100).toFixed(0)+'%';"""

EU_GEN = """
function generateInvoice(){generateDoc();}
function generateDoc(){
  const from_=document.getElementById('from')?.value||'Your Business';
  const to_=document.getElementById('to')?.value||'Client';
  const num_=document.getElementById('invNum')?.value||'INV-001';
  const date_=document.getElementById('invDate')?.value||new Date().toISOString().split('T')[0];
  const due_=document.getElementById('dueDate')?.value||'';
  const vatFrom=document.getElementById('vatFrom')?.value||'';
  const vatTo=document.getElementById('vatTo')?.value||'';
  const cur=document.getElementById('currency')?.value||'EUR';
  const vatRate=parseFloat(document.getElementById('vatRate')?.value)||20;
  const rc=document.getElementById('reverseCharge')?.value==='yes';
  let sub=0;
  document.querySelectorAll('#lineItems tr').forEach(tr=>{
    const inputs=tr.querySelectorAll('input');if(inputs.length<3)return;
    sub+=(parseFloat(inputs[1].value)||0)*(parseFloat(inputs[2].value)||0);
  });
  const discPct=(parseFloat(document.getElementById('discount')?.value)||0)/100;
  const discAmt=sub*discPct;const netSub=sub-discAmt;
  const vatAmt=rc?0:netSub*vatRate/100;const total=netSub+vatAmt;
  const notes=document.getElementById('notes')?.value||'';
  let lines='';
  document.querySelectorAll('#lineItems tr').forEach(tr=>{
    const inputs=tr.querySelectorAll('input');if(inputs.length<3)return;
    const d=inputs[0].value||'Service';const q=parseFloat(inputs[1].value)||0;const r=parseFloat(inputs[2].value)||0;
    lines+=`  ${d.padEnd(30)} x${q}  ${cur} ${r.toFixed(2).padStart(8)}  ${cur} ${(q*r).toFixed(2).padStart(10)}\n`;
  });
  const rcNote=rc?'\\n** REVERSE CHARGE — VAT to be accounted for by the recipient **':''
  const txt=`EU VAT INVOICE
${'='.repeat(60)}
Invoice #: ${num_}   Date: ${date_}${due_?'   Due: '+due_:''}
${'-'.repeat(60)}
Supplier:  ${from_}${vatFrom?' | VAT: '+vatFrom:''}
Customer:  ${to_}${vatTo?' | VAT: '+vatTo:''}
Currency:  ${cur}
${'-'.repeat(60)}
DESCRIPTION                        QTY    UNIT PRICE     TOTAL
${'-'.repeat(60)}
${lines}${'-'.repeat(60)}
  Net Subtotal:          ${cur} ${netSub.toFixed(2)}
  Discount:             -${cur} ${discAmt.toFixed(2)}
  VAT ${vatRate}%:${rc?' (Reverse Charge)':''}          ${cur} ${vatAmt.toFixed(2)}
${'='.repeat(60)}
  TOTAL DUE (${cur}):    ${cur} ${total.toFixed(2)}
${'='.repeat(60)}${rcNote}
${rc?'Pursuant to EU VAT Directive Art. 196 — the VAT liability\\nis transferred to the customer (reverse charge).':''}
${notes?'Notes: '+notes:''}`;
  document.getElementById('preview').textContent=txt;
  document.getElementById('output').style.display='block';
  document.getElementById('output').scrollIntoView({behavior:'smooth'});
}"""

def country_gen(country, currency_sym, currency_code, tax_name, tax_rate, extra_note=""):
    return f"""
function generateInvoice(){{generateDoc();}}
function generateDoc(){{
  const from_=document.getElementById('from')?.value||'Your Business';
  const to_=document.getElementById('to')?.value||'Client';
  const num_=document.getElementById('invNum')?.value||'INV-001';
  const date_=document.getElementById('invDate')?.value||new Date().toISOString().split('T')[0];
  const due_=document.getElementById('dueDate')?.value||'';
  const taxNum=document.getElementById('taxNum')?.value||'';
  const taxRate=parseFloat(document.getElementById('taxRate')?.value)||{tax_rate};
  let sub=0;
  document.querySelectorAll('#lineItems tr').forEach(tr=>{{
    const inputs=tr.querySelectorAll('input');if(inputs.length<3)return;
    sub+=(parseFloat(inputs[1].value)||0)*(parseFloat(inputs[2].value)||0);
  }});
  const discPct=(parseFloat(document.getElementById('discount')?.value)||0)/100;
  const discAmt=sub*discPct;const netSub=sub-discAmt;
  const taxAmt=netSub*taxRate/100;const total=netSub+taxAmt;
  const notes=document.getElementById('notes')?.value||'';
  let lines='';
  document.querySelectorAll('#lineItems tr').forEach(tr=>{{
    const inputs=tr.querySelectorAll('input');if(inputs.length<3)return;
    const d=inputs[0].value||'Service';const q=parseFloat(inputs[1].value)||0;const r=parseFloat(inputs[2].value)||0;
    lines+=`  ${{d.padEnd(30)}} x${{q}}  {currency_sym}${{r.toFixed(2)}}  {currency_sym}${{(q*r).toFixed(2)}}\\n`;
  }});
  const txt=`{country.upper()} INVOICE
${'='*56}
Invoice #: ${{num_}}    Date: ${{date_}}${{due_?'   Due: '+due_:''}}
${{'-'*56}}
From: ${{from_}}${{taxNum?' | {tax_name}: '+taxNum:''}}
To:   ${{to_}}
Currency: {currency_code}
${{'-'*56}}
DESCRIPTION                        QTY     UNIT     TOTAL
${{'-'*56}}
${{lines}}${{'-'*56}}
  Net Amount:  {currency_sym}${{netSub.toFixed(2)}}
  Discount:   -{currency_sym}${{discAmt.toFixed(2)}}
  {tax_name} (${{taxRate}}%): {currency_sym}${{taxAmt.toFixed(2)}}
${'='*56}
  TOTAL DUE ({currency_code}):  {currency_sym}${{total.toFixed(2)}}
${'='*56}
{extra_note}
${{notes?'Notes: '+notes:''}}\`;
  document.getElementById('preview').textContent=txt;
  document.getElementById('output').style.display='block';
  document.getElementById('output').scrollIntoView({{behavior:'smooth'}});
}}"""

UK_FIELDS = '<div class="field"><label>Your VAT Reg. No.</label><input id="taxNum" type="text" placeholder="GB123456789"></div>'
CA_FIELDS  = '<div class="field"><label>Your GST/HST Number</label><input id="taxNum" type="text" placeholder="123456789 RT0001"></div><div class="field"><label>Province</label><select id="province" oninput="setProvTax()"><option value="13">Ontario (HST 13%)</option><option value="5">Alberta (GST 5%)</option><option value="15">Nova Scotia (HST 15%)</option><option value="12">British Columbia (GST+PST 12%)</option><option value="14.975">Quebec (GST+QST ~15%)</option></select></div>'
AU_FIELDS  = '<div class="field"><label>Your ABN</label><input id="taxNum" type="text" placeholder="12 345 678 901"></div>'
IN_FIELDS  = '<div class="field"><label>Your GSTIN</label><input id="taxNum" type="text" placeholder="22AAAAA0000A1Z5"></div><div class="field"><label>HSN / SAC Code</label><input id="hsnCode" type="text" placeholder="998314"></div>'

# ─── GROUP B: Specialty trade invoices ───────────────────────────────────────
# Each gets 1-2 unique extra fields + unique doc header in generateInvoice

TRADE_SPECS = {
# (extra_fields_html_snippet, unique_header_label, extra_output_section)
"cleaning-invoice": (
    '<div class="field"><label>Service Frequency</label><select id="freq"><option value="one-time">One-Time</option><option value="weekly">Weekly</option><option value="biweekly">Bi-Weekly</option><option value="monthly">Monthly</option></select></div>'
    '<div class="field"><label>Property Size (sq ft)</label><input id="sqft" type="number" value="1500" step="100" min="0"></div>',
    "CLEANING SERVICES INVOICE",
    "  Service Frequency: ${document.getElementById('freq')?.value||''}\\n  Property: ${document.getElementById('sqft')?.value||''} sq ft\\n"
),
"plumbing-invoice": (
    '<div class="field"><label>Emergency Call-Out Fee ($)</label><input id="callout" type="number" value="0" step="5" min="0" oninput="calcTotals()"></div>'
    '<div class="field"><label>License / Permit #</label><input id="permitNum" type="text" placeholder="PLB-2026-XXXXX"></div>',
    "PLUMBING SERVICES INVOICE",
    "  Emergency Call-Out: $${parseFloat(document.getElementById('callout')?.value||0).toFixed(2)}\\n  Permit #: ${document.getElementById('permitNum')?.value||'N/A'}\\n"
),
"electrical-invoice": (
    '<div class="field"><label>Electrical Permit # </label><input id="permitNum" type="text" placeholder="EL-2026-XXXXX"></div>'
    '<div class="field"><label>Materials Markup (%)</label><input id="markup" type="number" value="15" step="1" min="0"></div>',
    "ELECTRICAL SERVICES INVOICE",
    "  Permit #: ${document.getElementById('permitNum')?.value||'N/A'}\\n  Materials Markup: ${document.getElementById('markup')?.value||0}%\\n"
),
"landscaping-invoice": (
    '<div class="field"><label>Season</label><select id="season"><option>Spring</option><option>Summer</option><option>Fall</option><option>Winter</option></select></div>'
    '<div class="field"><label>Property Size (acres)</label><input id="acres" type="number" value="0.25" step="0.25" min="0"></div>',
    "LANDSCAPING SERVICES INVOICE",
    "  Season: ${document.getElementById('season')?.value||''}  Property: ${document.getElementById('acres')?.value||''} acres\\n"
),
"consulting-invoice": (
    '<div class="field"><label>Project / Engagement</label><input id="project" type="text" placeholder="Strategic Review Q2 2026"></div>'
    '<div class="field"><label>Billing Method</label><select id="billMethod"><option value="hourly">Hourly</option><option value="fixed">Fixed Fee</option><option value="retainer">Retainer</option></select></div>',
    "CONSULTING INVOICE",
    "  Project: ${document.getElementById('project')?.value||''}\\n  Billing: ${document.getElementById('billMethod')?.value||''}\\n"
),
"freelance-invoice": (
    '<div class="field"><label>Project Name</label><input id="project" type="text" placeholder="Website Redesign"></div>'
    '<div class="field"><label>Contract Reference</label><input id="contractRef" type="text" placeholder="CONTRACT-2026-001"></div>',
    "FREELANCE INVOICE",
    "  Project: ${document.getElementById('project')?.value||''}  Contract: ${document.getElementById('contractRef')?.value||''}\\n"
),
"graphic-design-invoice": (
    '<div class="field"><label>Design Project Type</label><select id="projType"><option>Logo Design</option><option>Brand Identity</option><option>Print Design</option><option>Digital Assets</option><option>Illustration</option><option>UI/UX Design</option></select></div>'
    '<div class="field"><label>Revision Rounds Included</label><input id="revisions" type="number" value="2" min="0" step="1"></div>',
    "GRAPHIC DESIGN INVOICE",
    "  Project Type: ${document.getElementById('projType')?.value||''}  Revisions: ${document.getElementById('revisions')?.value||0} rounds\\n"
),
"web-design-invoice": (
    '<div class="field"><label>Website Type</label><select id="webType"><option>Business Website</option><option>E-Commerce</option><option>Portfolio</option><option>Landing Page</option><option>Web App</option></select></div>'
    '<div class="field"><label>CMS Platform</label><select id="cms"><option>WordPress</option><option>Shopify</option><option>Webflow</option><option>Custom</option><option>Other</option></select></div>',
    "WEB DESIGN INVOICE",
    "  Website: ${document.getElementById('webType')?.value||''}  Platform: ${document.getElementById('cms')?.value||''}\\n"
),
"photography-invoice": (
    '<div class="field"><label>Shoot Type</label><select id="shootType"><option>Portrait</option><option>Commercial</option><option>Event</option><option>Real Estate</option><option>Product</option><option>Wedding</option></select></div>'
    '<div class="field"><label>Edited Images Delivered</label><input id="imgCount" type="number" value="50" step="10" min="0"></div>',
    "PHOTOGRAPHY INVOICE",
    "  Shoot Type: ${document.getElementById('shootType')?.value||''}  Images: ${document.getElementById('imgCount')?.value||0} delivered\\n"
),
"writing-invoice": (
    '<div class="field"><label>Content Type</label><select id="contentType"><option>Blog Posts</option><option>Copywriting</option><option>Technical Writing</option><option>Ghostwriting</option><option>Editing & Proofreading</option></select></div>'
    '<div class="field"><label>Word Count Delivered</label><input id="wordCount" type="number" value="2000" step="500" min="0"></div>',
    "WRITING SERVICES INVOICE",
    "  Content Type: ${document.getElementById('contentType')?.value||''}  Words: ${document.getElementById('wordCount')?.value||0}\\n"
),
"marketing-invoice": (
    '<div class="field"><label>Campaign / Channel</label><select id="channel"><option>Social Media</option><option>SEO / Content</option><option>Email Marketing</option><option>PPC / Ads</option><option>PR</option><option>Full Service</option></select></div>'
    '<div class="field"><label>Reporting Period</label><input id="period" type="text" placeholder="May 2026"></div>',
    "MARKETING SERVICES INVOICE",
    "  Channel: ${document.getElementById('channel')?.value||''}  Period: ${document.getElementById('period')?.value||''}\\n"
),
"legal-services-invoice": (
    '<div class="field"><label>Matter / Case Reference</label><input id="matterRef" type="text" placeholder="Matter #2026-XXXX"></div>'
    '<div class="field"><label>Attorney / Firm License</label><input id="licNum" type="text" placeholder="Bar #XXXXX"></div>',
    "LEGAL SERVICES INVOICE",
    "  Matter: ${document.getElementById('matterRef')?.value||''}  License: ${document.getElementById('licNum')?.value||''}\\n"
),
"tutoring-invoice": (
    '<div class="field"><label>Subject / Course</label><input id="subject" type="text" placeholder="Mathematics / Calculus"></div>'
    '<div class="field"><label>Session Dates</label><input id="sessionDates" type="text" placeholder="Jun 1–15, 2026"></div>',
    "TUTORING SERVICES INVOICE",
    "  Subject: ${document.getElementById('subject')?.value||''}  Sessions: ${document.getElementById('sessionDates')?.value||''}\\n"
),
"IT-services-invoice": (
    '<div class="field"><label>Service Ticket / Ref #</label><input id="ticketNum" type="text" placeholder="TKT-2026-XXXX"></div>'
    '<div class="field"><label>Service Category</label><select id="svcCat"><option>Support & Maintenance</option><option>Network Setup</option><option>Software Development</option><option>Cybersecurity</option><option>Cloud Services</option></select></div>',
    "IT SERVICES INVOICE",
    "  Ticket: ${document.getElementById('ticketNum')?.value||''}  Category: ${document.getElementById('svcCat')?.value||''}\\n"
),
"agency-invoice": (
    '<div class="field"><label>Client PO Number</label><input id="poNum" type="text" placeholder="PO-2026-XXXX"></div>'
    '<div class="field"><label>Account Manager</label><input id="acctMgr" type="text" placeholder="Jane Smith"></div>',
    "AGENCY INVOICE",
    "  PO #: ${document.getElementById('poNum')?.value||'N/A'}  Account Mgr: ${document.getElementById('acctMgr')?.value||''}\\n"
),
"accounting-invoice": (
    '<div class="field"><label>Service Period</label><input id="servicePeriod" type="text" placeholder="Q2 2026 (Apr–Jun)"></div>'
    '<div class="field"><label>Engagement Type</label><select id="engType"><option>Bookkeeping</option><option>Tax Preparation</option><option>Audit</option><option>Payroll Services</option><option>Advisory</option></select></div>',
    "ACCOUNTING SERVICES INVOICE",
    "  Period: ${document.getElementById('servicePeriod')?.value||''}  Engagement: ${document.getElementById('engType')?.value||''}\\n"
),
"catering-invoice": (
    '<div class="field"><label>Event Date</label><input id="eventDate" type="date"></div>'
    '<div class="field"><label>Guest Count</label><input id="guestCount" type="number" value="50" step="5" min="1"></div>',
    "CATERING INVOICE",
    "  Event Date: ${document.getElementById('eventDate')?.value||''}  Guests: ${document.getElementById('guestCount')?.value||''}\\n"
),
"event-planning-invoice": (
    '<div class="field"><label>Event Name</label><input id="eventName" type="text" placeholder="Annual Gala 2026"></div>'
    '<div class="field"><label>Event Date</label><input id="eventDate" type="date"></div>',
    "EVENT PLANNING INVOICE",
    "  Event: ${document.getElementById('eventName')?.value||''}  Date: ${document.getElementById('eventDate')?.value||''}\\n"
),
"startup-invoice": (
    '<div class="field"><label>Milestone / Sprint</label><input id="milestone" type="text" placeholder="MVP v1.0 — Sprint 3"></div>'
    '<div class="field"><label>Equity Arrangement</label><select id="equity"><option value="no">No equity arrangement</option><option value="note">Convertible note in lieu</option><option value="partial">Partial payment + equity</option></select></div>',
    "STARTUP INVOICE",
    "  Milestone: ${document.getElementById('milestone')?.value||''}  Equity: ${document.getElementById('equity')?.value||''}\\n"
),
"small-business-invoice": (
    '<div class="field"><label>Business Registration #</label><input id="bizReg" type="text" placeholder="EIN / Business ID"></div>'
    '<div class="field"><label>Service Category</label><input id="svcCat" type="text" placeholder="Professional Services"></div>',
    "SMALL BUSINESS INVOICE",
    "  Reg #: ${document.getElementById('bizReg')?.value||''}  Category: ${document.getElementById('svcCat')?.value||''}\\n"
),
"sole-trader-invoice": (
    '<div class="field"><label>UTR / Tax Reference</label><input id="utr" type="text" placeholder="Your UTR or Tax ID"></div>'
    '<div class="field"><label>National Insurance No.</label><input id="niNum" type="text" placeholder="AB 12 34 56 C (UK)"></div>',
    "SOLE TRADER INVOICE",
    "  UTR: ${document.getElementById('utr')?.value||''}  NI: ${document.getElementById('niNum')?.value||''}\\n"
),
"self-employed-invoice": (
    '<div class="field"><label>SSN / EIN Last 4</label><input id="taxLast4" type="text" placeholder="XXXX" maxlength="4"></div>'
    '<div class="field"><label>1099 Expected</label><select id="needs1099"><option value="yes">Yes — amount ≥ $600</option><option value="no">No — below threshold</option></select></div>',
    "SELF-EMPLOYED INVOICE",
    "  1099 Required: ${document.getElementById('needs1099')?.value||''}\\n"
),
"contractor-invoice": (
    '<div class="field"><label>Contractor License #</label><input id="licNum" type="text" placeholder="CONTR-XXXX"></div>'
    '<div class="field"><label>Job Site Address</label><input id="jobSite" type="text" placeholder="123 Main St, City, ST"></div>',
    "CONTRACTOR INVOICE",
    "  License #: ${document.getElementById('licNum')?.value||''}  Site: ${document.getElementById('jobSite')?.value||''}\\n"
),
}

# ─── GROUP C: Receipt generators ─────────────────────────────────────────────
RECEIPT_SPECS = {
"payment-receipt": (
    '<div class="field"><label>Payment Method</label><select id="payMethod"><option>Cash</option><option>Check</option><option>Credit Card</option><option>Bank Transfer</option><option>Online Payment</option></select></div>'
    '<div class="field"><label>Reference / Transaction #</label><input id="txnRef" type="text" placeholder="TXN-XXXX"></div>',
    "PAYMENT RECEIPT",
    "  Paid via: ${document.getElementById('payMethod')?.value||''}  Ref: ${document.getElementById('txnRef')?.value||''}\\n"
),
"sales-receipt": (
    '<div class="field"><label>Payment Method</label><select id="payMethod"><option>Cash</option><option>Card</option><option>Check</option></select></div>'
    '<div class="field"><label>Cashier / Served By</label><input id="cashier" type="text" placeholder="Employee Name"></div>',
    "SALES RECEIPT",
    "  Served by: ${document.getElementById('cashier')?.value||''}  Payment: ${document.getElementById('payMethod')?.value||''}\\n"
),
"cash-receipt": (
    '<div class="field"><label>Amount Tendered ($)</label><input id="tendered" type="number" value="0" step="0.01" min="0" oninput="calcChange()"></div>'
    '<div class="field"><label>Change Due ($)</label><input id="changeDue" type="text" value="$0.00" readonly style="background:#f1f5f9"></div>',
    "CASH RECEIPT",
    "  Tendered: $${document.getElementById('tendered')?.value||'0.00'}  Change: ${document.getElementById('changeDue')?.value||'$0.00'}\\n"
),
"expense-receipt": (
    '<div class="field"><label>Expense Category</label><select id="expCat"><option>Travel</option><option>Meals & Entertainment</option><option>Office Supplies</option><option>Equipment</option><option>Software / SaaS</option><option>Other</option></select></div>'
    '<div class="field"><label>Reimbursable?</label><select id="reimbursable"><option value="yes">Yes — Reimbursable</option><option value="no">No — Business Expense</option></select></div>',
    "EXPENSE RECEIPT",
    "  Category: ${document.getElementById('expCat')?.value||''}  Reimbursable: ${document.getElementById('reimbursable')?.value||''}\\n"
),
"hotel-receipt": (
    '<div class="field"><label>Check-In Date</label><input id="checkIn" type="date"></div>'
    '<div class="field"><label>Check-Out Date</label><input id="checkOut" type="date"></div>'
    '<div class="field"><label>Room Number</label><input id="roomNum" type="text" placeholder="Room 302"></div>',
    "HOTEL RECEIPT",
    "  Check-In: ${document.getElementById('checkIn')?.value||''}  Check-Out: ${document.getElementById('checkOut')?.value||''}  Room: ${document.getElementById('roomNum')?.value||''}\\n"
),
"rent-receipt": (
    '<div class="field"><label>Property Address</label><input id="propertyAddr" type="text" placeholder="123 Oak St, Apt 4B"></div>'
    '<div class="field"><label>Rental Period</label><input id="rentalPeriod" type="text" placeholder="June 2026"></div>',
    "RENT RECEIPT",
    "  Property: ${document.getElementById('propertyAddr')?.value||''}  Period: ${document.getElementById('rentalPeriod')?.value||''}\\n"
),
"donation-receipt": (
    '<div class="field"><label>Organization EIN</label><input id="ein" type="text" placeholder="12-3456789"></div>'
    '<div class="field"><label>Tax-Deductible?</label><select id="taxDed"><option value="yes">Yes — 501(c)(3) deductible</option><option value="partial">Partially deductible</option><option value="no">Not deductible</option></select></div>',
    "DONATION RECEIPT",
    "  EIN: ${document.getElementById('ein')?.value||''}  Deductible: ${document.getElementById('taxDed')?.value||''}\\n  *No goods or services were provided in exchange for this gift.*\\n"
),
"refund-receipt": (
    '<div class="field"><label>Original Invoice #</label><input id="origInv" type="text" placeholder="INV-001"></div>'
    '<div class="field"><label>Refund Reason</label><select id="refundReason"><option>Customer Request</option><option>Defective Product</option><option>Service Not Rendered</option><option>Billing Error</option></select></div>',
    "REFUND RECEIPT",
    "  Original Invoice: ${document.getElementById('origInv')?.value||''}  Reason: ${document.getElementById('refundReason')?.value||''}\\n"
),
"taxi-receipt": (
    '<div class="field"><label>Pickup Location</label><input id="pickup" type="text" placeholder="123 Main St"></div>'
    '<div class="field"><label>Drop-off Location</label><input id="dropoff" type="text" placeholder="Airport Terminal 2"></div>'
    '<div class="field"><label>Driver / Vehicle ID</label><input id="driverID" type="text" placeholder="Driver #1234 / ABC-5678"></div>',
    "TAXI / RIDE RECEIPT",
    "  From: ${document.getElementById('pickup')?.value||''}  To: ${document.getElementById('dropoff')?.value||''}\\n  Driver/Vehicle: ${document.getElementById('driverID')?.value||''}\\n"
),
"business-receipt": (
    '<div class="field"><label>Business Type</label><select id="bizType"><option>Retail</option><option>Service</option><option>Food & Beverage</option><option>Professional</option><option>Other</option></select></div>'
    '<div class="field"><label>Transaction ID</label><input id="txnId" type="text" placeholder="TXN-0001"></div>',
    "BUSINESS RECEIPT",
    "  Business Type: ${document.getElementById('bizType')?.value||''}  Tx: ${document.getElementById('txnId')?.value||''}\\n"
),
}

# ─── GROUP D: Specialty financial documents ────────────────────────────────
SPECIALTY_SPECS = {
"milestone-invoice": (
    '<div class="field"><label>Milestone Name</label><input id="milestoneName" type="text" placeholder="Phase 2 Complete"></div>'
    '<div class="field"><label>Milestone % of Total Project</label><input id="milestonePct" type="number" value="25" step="5" min="0" max="100"></div>'
    '<div class="field"><label>Total Project Value ($)</label><input id="projectTotal" type="number" value="0" step="100" min="0"></div>',
    "MILESTONE INVOICE",
    "  Milestone: ${document.getElementById('milestoneName')?.value||''}  (${document.getElementById('milestonePct')?.value||0}% of $${parseFloat(document.getElementById('projectTotal')?.value||0).toFixed(2)} project)\\n"
),
"recurring-invoice": (
    '<div class="field"><label>Billing Cycle</label><select id="cycle"><option>Monthly</option><option>Weekly</option><option>Bi-Weekly</option><option>Quarterly</option><option>Annual</option></select></div>'
    '<div class="field"><label>Subscription Start Date</label><input id="subStart" type="date"></div>'
    '<div class="field"><label>Billing Period</label><input id="billPeriod" type="text" placeholder="June 2026"></div>',
    "RECURRING INVOICE",
    "  Billing Cycle: ${document.getElementById('cycle')?.value||''}  Period: ${document.getElementById('billPeriod')?.value||''}\\n  Subscription Since: ${document.getElementById('subStart')?.value||''}\\n"
),
"retainer-agreement": (
    '<div class="field"><label>Retainer Period</label><input id="retPeriod" type="text" placeholder="June 2026"></div>'
    '<div class="field"><label>Hours Included / Month</label><input id="retHours" type="number" value="10" step="1" min="0"></div>'
    '<div class="field"><label>Overage Rate ($/hr)</label><input id="overageRate" type="number" value="150" step="10" min="0"></div>',
    "RETAINER INVOICE",
    "  Retainer Period: ${document.getElementById('retPeriod')?.value||''}\\n  Includes ${document.getElementById('retHours')?.value||0} hrs. Overage: $${document.getElementById('overageRate')?.value||0}/hr\\n"
),
"progress-billing": (
    '<div class="field"><label>Project Name</label><input id="projName" type="text" placeholder="Office Renovation"></div>'
    '<div class="field"><label>Work Completed (%)</label><input id="completePct" type="number" value="40" step="5" min="0" max="100" oninput="calcProgress()"></div>'
    '<div class="field"><label>Total Contract Value ($)</label><input id="contractVal" type="number" value="50000" step="1000" min="0" oninput="calcProgress()"></div>',
    "PROGRESS BILLING INVOICE",
    "  Project: ${document.getElementById('projName')?.value||''}\\n  ${document.getElementById('completePct')?.value||0}% complete of $${parseFloat(document.getElementById('contractVal')?.value||0).toFixed(2)} contract\\n"
),
"rush-invoice": (
    '<div class="field"><label>Standard Rate ($)</label><input id="stdRate" type="number" value="0" step="10" oninput="calcRush()"></div>'
    '<div class="field"><label>Rush Fee (%)</label><select id="rushPct" oninput="calcRush()"><option value="25">25% Rush Fee</option><option value="50">50% Rush Fee</option><option value="100">100% (Double Time)</option></select></div>'
    '<div class="field"><label>Rush Delivery By</label><input id="rushDue" type="datetime-local"></div>',
    "RUSH / EXPEDITED INVOICE",
    "  Rush Delivery: ${document.getElementById('rushDue')?.value||''}  Rush Premium: ${document.getElementById('rushPct')?.value||25}%\\n"
),
"deposit-invoice": (
    '<div class="field"><label>Total Project Value ($)</label><input id="projectTotal" type="number" value="5000" step="100" min="0" oninput="calcDeposit()"></div>'
    '<div class="field"><label>Deposit Required (%)</label><select id="depositPct" oninput="calcDeposit()"><option value="25">25%</option><option value="33">33%</option><option value="50">50% (Half Down)</option><option value="100">100% (Full Prepay)</option></select></div>',
    "DEPOSIT INVOICE",
    "  Project Total: $${parseFloat(document.getElementById('projectTotal')?.value||0).toFixed(2)}  Deposit: ${document.getElementById('depositPct')?.value||50}%\\n  Balance due on completion.\\n"
),
"net30-invoice": (
    '<div class="field"><label>Early Pay Discount (%)</label><input id="earlyDisc" type="number" value="2" step="0.5" min="0"></div>'
    '<div class="field"><label>Early Pay Cutoff (days)</label><input id="earlyDays" type="number" value="10" step="1" min="1"></div>',
    "NET 30 INVOICE",
    "  Payment Terms: Net 30 Days\\n  Early Pay: ${document.getElementById('earlyDisc')?.value||2}% discount if paid within ${document.getElementById('earlyDays')?.value||10} days\\n"
),
"net60-invoice": (
    '<div class="field"><label>Late Fee Rate (% per month)</label><input id="lateFeeRate" type="number" value="1.5" step="0.5" min="0"></div>'
    '<div class="field"><label>Purchase Order #</label><input id="poNum" type="text" placeholder="PO-2026-XXXX"></div>',
    "NET 60 INVOICE",
    "  Payment Terms: Net 60 Days\\n  PO #: ${document.getElementById('poNum')?.value||'N/A'}  Late Fee: ${document.getElementById('lateFeeRate')?.value||1.5}%/month after due\\n"
),
"credit-memo": (
    '<div class="field"><label>Original Invoice #</label><input id="origInv" type="text" placeholder="INV-001"></div>'
    '<div class="field"><label>Credit Reason</label><select id="creditReason"><option>Overpayment Refund</option><option>Return / Cancellation</option><option>Billing Error Correction</option><option>Goodwill Credit</option></select></div>',
    "CREDIT MEMO",
    "  Applied to Invoice: ${document.getElementById('origInv')?.value||''}\\n  Reason: ${document.getElementById('creditReason')?.value||''}\\n  * This credit memo reduces your outstanding balance. *\\n"
),
"credit-note": (
    '<div class="field"><label>Original Invoice #</label><input id="origInv" type="text" placeholder="INV-001"></div>'
    '<div class="field"><label>Reason for Credit Note</label><input id="cnReason" type="text" placeholder="Returned goods — see RMA #XXXX"></div>',
    "CREDIT NOTE",
    "  Original Invoice: ${document.getElementById('origInv')?.value||''}  Reason: ${document.getElementById('cnReason')?.value||''}\\n"
),
"debit-note": (
    '<div class="field"><label>Original Invoice #</label><input id="origInv" type="text" placeholder="INV-001"></div>'
    '<div class="field"><label>Reason for Debit Note</label><input id="dnReason" type="text" placeholder="Price adjustment — item X"></div>',
    "DEBIT NOTE",
    "  Original Invoice: ${document.getElementById('origInv')?.value||''}  Reason: ${document.getElementById('dnReason')?.value||''}\\n  * Amount represents additional charges due. *\\n"
),
"pro-forma-invoice": (
    '<div class="field"><label>Purpose</label><select id="purpose"><option>Pre-shipment estimate</option><option>Customs declaration</option><option>Letter of credit</option><option>Budgetary approval</option></select></div>'
    '<div class="field"><label>Validity Period</label><input id="validity" type="text" placeholder="Valid 30 days from issue date"></div>',
    "PRO-FORMA INVOICE",
    "  Purpose: ${document.getElementById('purpose')?.value||''}\\n  ${document.getElementById('validity')?.value||'Valid 30 days'}\\n  * This is a pro-forma invoice, not a demand for payment. *\\n"
),
"commercial-invoice": (
    '<div class="field"><label>Country of Origin</label><input id="countryOrigin" type="text" placeholder="United States"></div>'
    '<div class="field"><label>HS / Tariff Code</label><input id="hsCode" type="text" placeholder="8471.30.0100"></div>'
    '<div class="field"><label>Declared Value for Customs ($)</label><input id="customsVal" type="number" value="0" step="10" min="0"></div>',
    "COMMERCIAL INVOICE",
    "  Country of Origin: ${document.getElementById('countryOrigin')?.value||''}  HS Code: ${document.getElementById('hsCode')?.value||''}\\n  Declared Customs Value: $${parseFloat(document.getElementById('customsVal')?.value||0).toFixed(2)}\\n"
),
"tax-invoice": (
    '<div class="field"><label>Tax Registration #</label><input id="taxRegNum" type="text" placeholder="GST/VAT Reg. #"></div>'
    '<div class="field"><label>Tax Invoice Type</label><select id="taxInvType"><option>Standard Tax Invoice</option><option>Simplified Tax Invoice</option><option>Recipient-Created Tax Invoice</option></select></div>',
    "TAX INVOICE",
    "  Tax Reg #: ${document.getElementById('taxRegNum')?.value||''}  Type: ${document.getElementById('taxInvType')?.value||''}\\n  Tax invoice for GST/VAT purposes.\\n"
),
"purchase-order": (
    '<div class="field"><label>PO Number</label><input id="poNum" type="text" placeholder="PO-2026-001" value="PO-2026-001"></div>'
    '<div class="field"><label>Ship To Address</label><input id="shipTo" type="text" placeholder="Warehouse Address"></div>'
    '<div class="field"><label>Required Delivery Date</label><input id="deliveryDate" type="date"></div>',
    "PURCHASE ORDER",
    "  PO #: ${document.getElementById('poNum')?.value||''}  Ship To: ${document.getElementById('shipTo')?.value||''}\\n  Required By: ${document.getElementById('deliveryDate')?.value||''}\\n"
),
"blanket-purchase-order": (
    '<div class="field"><label>BPO Number</label><input id="bpoNum" type="text" placeholder="BPO-2026-001"></div>'
    '<div class="field"><label>Contract Period</label><input id="contractPeriod" type="text" placeholder="Jan–Dec 2026"></div>'
    '<div class="field"><label>Maximum BPO Value ($)</label><input id="maxVal" type="number" value="50000" step="1000" min="0"></div>',
    "BLANKET PURCHASE ORDER",
    "  BPO #: ${document.getElementById('bpoNum')?.value||''}  Period: ${document.getElementById('contractPeriod')?.value||''}\\n  Maximum Value: $${parseFloat(document.getElementById('maxVal')?.value||0).toFixed(2)}\\n  Releases against this BPO are subject to individual delivery orders.\\n"
),
"work-order": (
    '<div class="field"><label>Work Order #</label><input id="woNum" type="text" placeholder="WO-2026-001"></div>'
    '<div class="field"><label>Work Site / Location</label><input id="workSite" type="text" placeholder="Site address or facility name"></div>'
    '<div class="field"><label>Scheduled Start Date</label><input id="startDate" type="date"></div>',
    "WORK ORDER",
    "  WO #: ${document.getElementById('woNum')?.value||''}  Site: ${document.getElementById('workSite')?.value||''}\\n  Scheduled: ${document.getElementById('startDate')?.value||''}\\n"
),
"service-order": (
    '<div class="field"><label>Service Order #</label><input id="soNum" type="text" placeholder="SO-2026-001"></div>'
    '<div class="field"><label>Priority</label><select id="priority"><option value="normal">Normal</option><option value="high">High Priority</option><option value="emergency">Emergency</option></select></div>',
    "SERVICE ORDER",
    "  SO #: ${document.getElementById('soNum')?.value||''}  Priority: ${document.getElementById('priority')?.value||'normal'}\\n"
),
"change-order": (
    '<div class="field"><label>Change Order #</label><input id="coNum" type="text" placeholder="CO-001"></div>'
    '<div class="field"><label>Original Contract / PO #</label><input id="origContract" type="text" placeholder="CONTRACT-001 / PO-001"></div>'
    '<div class="field"><label>Reason for Change</label><input id="coReason" type="text" placeholder="Scope modification — client request"></div>',
    "CHANGE ORDER",
    "  CO #: ${document.getElementById('coNum')?.value||''}  Original: ${document.getElementById('origContract')?.value||''}\\n  Reason: ${document.getElementById('coReason')?.value||''}\\n  * This change order modifies the original agreement. *\\n"
),
"return-merchandise": (
    '<div class="field"><label>RMA / Return #</label><input id="rmaNum" type="text" placeholder="RMA-2026-001"></div>'
    '<div class="field"><label>Original Invoice #</label><input id="origInv" type="text" placeholder="INV-001"></div>'
    '<div class="field"><label>Return Reason</label><select id="returnReason"><option>Defective</option><option>Wrong Item</option><option>Customer Changed Mind</option><option>Warranty Claim</option></select></div>',
    "RETURN MERCHANDISE AUTHORIZATION",
    "  RMA #: ${document.getElementById('rmaNum')?.value||''}  Orig Invoice: ${document.getElementById('origInv')?.value||''}\\n  Reason: ${document.getElementById('returnReason')?.value||''}\\n"
),
}

# ─── GROUP E: Statement/notice documents ──────────────────────────────────────
STATEMENT_SPECS = {
"billing-statement": (
    '<div class="field"><label>Statement Period</label><input id="stmtPeriod" type="text" placeholder="June 2026"></div>'
    '<div class="field"><label>Account Number</label><input id="acctNum" type="text" placeholder="ACCT-XXXX"></div>'
    '<div class="field"><label>Previous Balance ($)</label><input id="prevBal" type="number" value="0" step="0.01" min="0"></div>',
    "BILLING STATEMENT",
    "  Statement Period: ${document.getElementById('stmtPeriod')?.value||''}  Account: ${document.getElementById('acctNum')?.value||''}\\n  Previous Balance: $${parseFloat(document.getElementById('prevBal')?.value||0).toFixed(2)}\\n"
),
"account-summary": (
    '<div class="field"><label>Account Number</label><input id="acctNum" type="text" placeholder="ACCT-XXXX"></div>'
    '<div class="field"><label>Summary Period</label><input id="summaryPeriod" type="text" placeholder="Q2 2026 (Apr–Jun)"></div>'
    '<div class="field"><label>Credit Limit ($)</label><input id="creditLimit" type="number" value="10000" step="500" min="0"></div>',
    "ACCOUNT SUMMARY",
    "  Account: ${document.getElementById('acctNum')?.value||''}  Period: ${document.getElementById('summaryPeriod')?.value||''}\\n  Credit Limit: $${parseFloat(document.getElementById('creditLimit')?.value||0).toFixed(2)}\\n"
),
"statement-of-account": (
    '<div class="field"><label>Customer Account #</label><input id="custAcct" type="text" placeholder="CUST-XXXX"></div>'
    '<div class="field"><label>Opening Balance ($)</label><input id="openBal" type="number" value="0" step="0.01"></div>'
    '<div class="field"><label>Payments Received ($)</label><input id="payments" type="number" value="0" step="0.01" min="0"></div>',
    "STATEMENT OF ACCOUNT",
    "  Customer Acct: ${document.getElementById('custAcct')?.value||''}\\n  Opening Balance: $${parseFloat(document.getElementById('openBal')?.value||0).toFixed(2)}  Payments: $${parseFloat(document.getElementById('payments')?.value||0).toFixed(2)}\\n"
),
"overdue-invoice-notice": (
    '<div class="field"><label>Days Past Due</label><input id="daysOverdue" type="number" value="30" step="1" min="1"></div>'
    '<div class="field"><label>Late Fee Applied ($)</label><input id="lateFeeAmt" type="number" value="0" step="5" min="0"></div>',
    "OVERDUE INVOICE NOTICE",
    "  STATUS: ${document.getElementById('daysOverdue')?.value||30} DAYS PAST DUE\\n  Late Fee Applied: $${parseFloat(document.getElementById('lateFeeAmt')?.value||0).toFixed(2)}\\n  Immediate payment required to avoid collections action.\\n"
),
"collection-letter": (
    '<div class="field"><label>Total Amount in Collections ($)</label><input id="collAmt" type="number" value="0" step="10" min="0"></div>'
    '<div class="field"><label>Final Payment Deadline</label><input id="collDeadline" type="date"></div>',
    "COLLECTION LETTER",
    "  FINAL COLLECTION NOTICE\\n  Amount: $${parseFloat(document.getElementById('collAmt')?.value||0).toFixed(2)}\\n  Deadline: ${document.getElementById('collDeadline')?.value||''}\\n  Failure to respond may result in legal action or credit reporting.\\n"
),
"final-notice": (
    '<div class="field"><label>Amount Due ($)</label><input id="finalAmt" type="number" value="0" step="10" min="0"></div>'
    '<div class="field"><label>Response Required By</label><input id="responseBy" type="date"></div>',
    "FINAL NOTICE",
    "  *** FINAL NOTICE ***\\n  Amount: $${parseFloat(document.getElementById('finalAmt')?.value||0).toFixed(2)}\\n  Respond by: ${document.getElementById('responseBy')?.value||''}\\n  Legal action will be pursued if payment is not received.\\n"
),
"payment-reminder": (
    '<div class="field"><label>Invoice # Being Reminded</label><input id="remInvNum" type="text" placeholder="INV-001"></div>'
    '<div class="field"><label>Reminder Type</label><select id="remType"><option value="friendly">Friendly Reminder (not yet due)</option><option value="due">Due Today</option><option value="overdue">Overdue Notice</option></select></div>',
    "PAYMENT REMINDER",
    "  Regarding Invoice: ${document.getElementById('remInvNum')?.value||''}\\n  Type: ${document.getElementById('remType')?.value||''}\\n"
),
"outstanding-invoices": (
    '<div class="field"><label>Client Account #</label><input id="clientAcct" type="text" placeholder="ACCT-XXXX"></div>'
    '<div class="field"><label>Aging Bucket</label><select id="aging"><option value="current">Current (0–30 days)</option><option value="31-60">31–60 Days</option><option value="61-90">61–90 Days</option><option value="90plus">90+ Days</option></select></div>',
    "OUTSTANDING INVOICES SUMMARY",
    "  Client Acct: ${document.getElementById('clientAcct')?.value||''}  Aging: ${document.getElementById('aging')?.value||''}\\n"
),
"payment-history": (
    '<div class="field"><label>Client Account #</label><input id="clientAcct" type="text" placeholder="ACCT-XXXX"></div>'
    '<div class="field"><label>History Period</label><input id="histPeriod" type="text" placeholder="Jan–Jun 2026"></div>',
    "PAYMENT HISTORY",
    "  Client: ${document.getElementById('clientAcct')?.value||''}  Period: ${document.getElementById('histPeriod')?.value||''}\\n"
),
}

# ─── GROUP F: Calculator tools ─────────────────────────────────────────────────
# These need a completely different form — they calculate, not generate documents
CALC_TOOLS_SIMPLE = {
"discount-calculator": None,  # keep existing logic — already good
"gst-calculator": None,
"sales-tax-calculator": None,
"vat-calculator": None,
"tax-calculator": None,
"late-fee-calculator": None,
"invoice-calculator": None,
"project-cost-calculator": None,
"hourly-rate-calculator": None,
"freelance-rate-calculator": None,
}

# ─── GROUP G: Payment agreements ──────────────────────────────────────────────
AGREEMENT_SPECS = {
"payment-agreement": (
    '<div class="field"><label>Debtor Name</label><input id="debtor" type="text" placeholder="John Smith"></div>'
    '<div class="field"><label>Total Amount Owed ($)</label><input id="totalOwed" type="number" value="5000" step="100" min="0"></div>'
    '<div class="field"><label>Installments</label><input id="installments" type="number" value="6" step="1" min="1"></div>'
    '<div class="field"><label>First Payment Due</label><input id="firstPayment" type="date"></div>',
    "PAYMENT AGREEMENT",
    "  Debtor: ${document.getElementById('debtor')?.value||''}\\n  Total: $${parseFloat(document.getElementById('totalOwed')?.value||0).toFixed(2)} in ${document.getElementById('installments')?.value||1} installments\\n  First Payment: ${document.getElementById('firstPayment')?.value||''}\\n"
),
"payment-plan-agreement": (
    '<div class="field"><label>Original Invoice Amount ($)</label><input id="origAmt" type="number" value="3000" step="100" min="0"></div>'
    '<div class="field"><label>Down Payment ($)</label><input id="downPayment" type="number" value="500" step="50" min="0" oninput="calcPlan()"></div>'
    '<div class="field"><label>Monthly Installments</label><input id="numPayments" type="number" value="5" step="1" min="1" oninput="calcPlan()"></div>'
    '<div class="field"><label>Interest Rate (% p.a.)</label><input id="planInterest" type="number" value="0" step="0.5" min="0" oninput="calcPlan()"></div>'
    '<div class="field"><label>Monthly Payment</label><input id="monthlyPayment" type="text" value="$0.00" readonly style="background:#f1f5f9;font-weight:700;color:var(--primary)"></div>',
    "PAYMENT PLAN AGREEMENT",
    "  Original Amount: $${parseFloat(document.getElementById('origAmt')?.value||0).toFixed(2)}\\n  Down Payment: $${parseFloat(document.getElementById('downPayment')?.value||0).toFixed(2)}\\n  Monthly: ${document.getElementById('monthlyPayment')?.value||''}  × ${document.getElementById('numPayments')?.value||0} months\\n"
),
"payment-terms-generator": (
    '<div class="field"><label>Payment Terms Type</label><select id="termsType"><option value="net30">Net 30</option><option value="net60">Net 60</option><option value="net15">Net 15</option><option value="due_receipt">Due on Receipt</option><option value="2-10-net30">2/10 Net 30</option></select></div>'
    '<div class="field"><label>Late Fee Rate (% per month)</label><input id="lateFeeRate" type="number" value="1.5" step="0.5" min="0"></div>'
    '<div class="field"><label>Dispute Resolution</label><select id="disputes"><option value="written">Written notice within 7 days</option><option value="14days">Written notice within 14 days</option><option value="30days">Written notice within 30 days</option></select></div>',
    "PAYMENT TERMS",
    "  Terms: ${document.getElementById('termsType')?.value||''}\\n  Late Fee: ${document.getElementById('lateFeeRate')?.value||1.5}% per month\\n  Disputes: ${document.getElementById('disputes')?.value||''}\\n"
),
}

# ─── GENERATOR FUNCTION ─────────────────────────────────────────────────────
def make_gen_fn(doc_title, extra_output_js, doc_label=""):
    """Build a unique generateInvoice() that embeds the extra output lines."""
    label = doc_label or doc_title.upper()
    return f"""
function generateInvoice(){{generateDoc();}}
function generateQuote(){{generateDoc();}}
function generateDoc(){{
  const from_=document.getElementById('from')?.value||'Your Business';
  const to_=document.getElementById('to')?.value||'Client';
  const num_=document.getElementById('invNum')?.value||document.getElementById('qNum')?.value||'001';
  const date_=document.getElementById('invDate')?.value||document.getElementById('qDate')?.value||new Date().toISOString().split('T')[0];
  const due_=document.getElementById('dueDate')?.value||'';
  const sub=document.getElementById('subtotal')?.textContent||'$0.00';
  const tax=document.getElementById('taxAmt')?.textContent||'$0.00';
  const disc=document.getElementById('discountAmt')?.textContent||'-$0.00';
  const total=document.getElementById('totalAmt')?.textContent||'$0.00';
  const notes=document.getElementById('notes')?.value||'';
  const extra={extra_output_js};
  let lines='';
  document.querySelectorAll('#lineItems tr').forEach(tr=>{{
    const inputs=tr.querySelectorAll('input');if(inputs.length<3)return;
    const d=inputs[0].value||'Item';const q=parseFloat(inputs[1].value)||0;const r=parseFloat(inputs[2].value)||0;
    lines+=`  ${{d.padEnd(30)}} x${{q}}  $${{r.toFixed(2).padStart(8)}}  $${{(q*r).toFixed(2).padStart(10)}}\\n`;
  }});
  const hdr=`{doc_title}
${'='*56}
{label} #: ${{num_}}   Date: ${{date_}}${{due_?'   Due: '+due_:''}}
${{'-'*56}}
From: ${{from_}}
To:   ${{to_}}
${{extra}}${{'-'*56}}
DESCRIPTION                        QTY    UNIT        TOTAL
${{'-'*56}}
${{lines}}${{'-'*56}}
  Subtotal:  ${{sub}}
  Discount:  ${{disc}}
  Tax:       ${{tax}}
${'='*56}
  TOTAL DUE: ${{total}}
${'='*56}
${{notes?'Notes: '+notes:''}}\`;
  document.getElementById('preview').textContent=hdr;
  document.getElementById('output').style.display='block';
  document.getElementById('output').scrollIntoView({{behavior:'smooth'}});
}}"""

def make_extra_calcs(tool_name):
    """Add specialized calcTotals extras for certain tools."""
    if tool_name == "cash-receipt":
        return """
  const tendered=parseFloat(document.getElementById('tendered')?.value)||0;
  const totalNum=parseFloat(document.getElementById('totalAmt')?.textContent?.replace(/[^0-9.]/g,'')||0);
  const change=Math.max(0,tendered-totalNum);
  const cd=document.getElementById('changeDue');if(cd)cd.value='$'+change.toFixed(2);"""
    if tool_name in ("rush-invoice",):
        return """
  const rushPct=(parseFloat(document.getElementById('rushPct')?.value)||0)/100;
  const stdRate=parseFloat(document.getElementById('stdRate')?.value)||0;
  const rushFee=stdRate*rushPct;
  const rf=document.getElementById('rushFeeDisplay');if(rf)rf.textContent='$'+rushFee.toFixed(2);"""
    if tool_name == "deposit-invoice":
        return """
  const projTotal=parseFloat(document.getElementById('projectTotal')?.value)||0;
  const depPct=(parseFloat(document.getElementById('depositPct')?.value)||50)/100;
  const depAmt=projTotal*depPct;
  const da=document.getElementById('depositDisplay');if(da)da.textContent='$'+depAmt.toFixed(2);"""
    if tool_name == "progress-billing":
        return """
  const pct=(parseFloat(document.getElementById('completePct')?.value)||0)/100;
  const cv=parseFloat(document.getElementById('contractVal')?.value)||0;
  const billable=cv*pct;
  const pb=document.getElementById('progressDisplay');if(pb)pb.textContent='$'+billable.toFixed(2);"""
    if tool_name == "payment-plan-agreement":
        return """
  const origAmt=parseFloat(document.getElementById('origAmt')?.value)||0;
  const down=parseFloat(document.getElementById('downPayment')?.value)||0;
  const n=parseInt(document.getElementById('numPayments')?.value)||1;
  const annRate=(parseFloat(document.getElementById('planInterest')?.value)||0)/100;
  const remaining=origAmt-down;
  let monthly=remaining/n;
  if(annRate>0){const mr=annRate/12;monthly=remaining*mr*Math.pow(1+mr,n)/(Math.pow(1+mr,n)-1);}
  const mp=document.getElementById('monthlyPayment');if(mp)mp.value='$'+monthly.toFixed(2);"""
    return ""

# ─── APPLY CHANGES ─────────────────────────────────────────────────────────────
def insert_extra_fields(content, extra_html):
    """Insert extra fields before the generate button."""
    for btn in [GEN_INV_BTN, GEN_QUOTE_BTN]:
        if btn in content:
            content = content.replace(btn, extra_html + "\n  " + btn, 1)
            return content
    return content

def replace_script(content, new_script_body):
    """Replace the last <script>...</script> block."""
    parts = content.rsplit('<script>', 1)
    if len(parts) != 2:
        return content
    end_parts = parts[1].rsplit('</script>', 1)
    if len(end_parts) != 2:
        return content
    return parts[0] + '<script>\n' + new_script_body + '\n</script>' + end_parts[1]

def build_script(tool_name, gen_fn_body, extra_calc=""):
    calc_extra = make_extra_calcs(tool_name) + extra_calc
    base = BASE_JS.replace("EXTRA_CALC", calc_extra if calc_extra else "")
    return base + "\n" + gen_fn_body

changed = 0
skipped = []

all_tools = {}

# Build tool map
for stem, (extra_fields, doc_title, extra_output_expr) in TRADE_SPECS.items():
    extra_calc_str = make_extra_calcs(stem)
    gen_fn = make_gen_fn(doc_title, extra_output_expr)
    all_tools[stem] = (extra_fields, gen_fn, extra_calc_str)

for stem, (extra_fields, doc_title, extra_output_expr) in RECEIPT_SPECS.items():
    gen_fn = make_gen_fn(doc_title, extra_output_expr, "RECEIPT")
    extra_calc_str = make_extra_calcs(stem)
    all_tools[stem] = (extra_fields, gen_fn, extra_calc_str)

for stem, (extra_fields, doc_title, extra_output_expr) in SPECIALTY_SPECS.items():
    gen_fn = make_gen_fn(doc_title, extra_output_expr)
    extra_calc_str = make_extra_calcs(stem)
    all_tools[stem] = (extra_fields, gen_fn, extra_calc_str)

for stem, (extra_fields, doc_title, extra_output_expr) in STATEMENT_SPECS.items():
    gen_fn = make_gen_fn(doc_title, extra_output_expr)
    extra_calc_str = make_extra_calcs(stem)
    all_tools[stem] = (extra_fields, gen_fn, extra_calc_str)

for stem, (extra_fields, doc_title, extra_output_expr) in AGREEMENT_SPECS.items():
    gen_fn = make_gen_fn(doc_title, extra_output_expr)
    extra_calc_str = make_extra_calcs(stem)
    all_tools[stem] = (extra_fields, gen_fn, extra_calc_str)

# Country invoices
all_tools["eu-invoice"] = (EU_EXTRA_FIELDS, EU_GEN, EU_CALC_EXTRA)
all_tools["uk-invoice"] = (UK_FIELDS,
    country_gen("UK","£","GBP","VAT No.",20,"Payment subject to UK VAT regulations."), "")
all_tools["canada-invoice"] = (CA_FIELDS,
    country_gen("Canada","C$","CAD","GST/HST",13,""), """
  const provRate=(parseFloat(document.getElementById('province')?.value)||13);
  document.getElementById('taxRate').value=provRate;""")
all_tools["australia-invoice"] = (AU_FIELDS,
    country_gen("Australia","A$","AUD","ABN",10,"GST rate 10% per Australian tax law."), "")
all_tools["india-invoice"] = (IN_FIELDS,
    country_gen("India","₹","INR","GSTIN",18,"CGST 9% + SGST 9% (intra-state) or IGST 18% (inter-state)"), "")

# Additional tools not in main groups but still in the 65-duplicate set
EXTRA_TOOLS = {
"invoice-generator":    ('', make_gen_fn("INVOICE", "'  Standard Invoice\\n'"), ""),
"simple-invoice":       ('<div class="field"><label>PO Reference</label><input id="poRef" type="text" placeholder="Optional PO #"></div>',
                         make_gen_fn("SIMPLE INVOICE", "document.getElementById('poRef')?.value?'  PO Ref: '+document.getElementById('poRef').value+'\\n':''"), ""),
"blank-invoice":        ('<div class="field"><label>Custom Invoice Title</label><input id="customTitle" type="text" placeholder="Invoice / Bill / Tax Invoice" value="Invoice"></div>',
                         make_gen_fn("BLANK INVOICE", "'  '+document.getElementById('customTitle')?.value+'\\n'"), ""),
"freelance-rate-calculator": ("", "", ""),  # skip - calculator type, leave as-is
"invoice-calculator":   ("", "", ""),
"project-cost-calculator": ("", "", ""),
"net30-invoice":        SPECIALTY_SPECS.get("net30-invoice", ('','','')),
"net60-invoice":        SPECIALTY_SPECS.get("net60-invoice", ('','','')),
}

# Merge
for stem, v in EXTRA_TOOLS.items():
    if stem not in all_tools and v[0] or v[1]:
        if isinstance(v, tuple) and len(v)==3:
            all_tools[stem] = v

# Additional invoice variants (same base form, unique output labels)
LABEL_VARIANTS = {
"agency-invoice": "AGENCY INVOICE",
"marketing-invoice": "MARKETING INVOICE",
"accounting-invoice": "ACCOUNTING INVOICE",
"consulting-invoice": "CONSULTING INVOICE",
}

# Process files
files = glob.glob("tools/*.html")
for fpath in files:
    stem = os.path.basename(fpath).replace(".html","")
    if stem not in all_tools:
        continue
    extra_fields, gen_fn, extra_calc = all_tools[stem]
    if not gen_fn:  # skip calculator tools
        continue
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
    orig = content
    if extra_fields:
        content = insert_extra_fields(content, extra_fields)
    script_body = build_script(stem, gen_fn, extra_calc)
    content = replace_script(content, script_body)
    if content != orig:
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(content)
        changed += 1
    else:
        skipped.append(stem)

print(f"BillingFixPro: {changed} files changed")
if skipped: print("Skipped:", skipped[:10])

# Verify uniqueness
import hashlib
sigs = {}
for f in glob.glob("tools/*.html"):
    txt = open(f, encoding="utf-8", errors="ignore").read()
    m = re.search(r'function generateDoc\(\)\{(.+?)\}(?=\s*function|\s*window|\s*document\.add)', txt, re.DOTALL)
    if m:
        sig = hashlib.md5(m.group(1).strip()[:200].encode()).hexdigest()[:8]
        sigs.setdefault(sig,[]).append(os.path.basename(f))
dups = {s:fs for s,fs in sigs.items() if len(fs)>3}
print(f"Unique generateDoc signatures: {len(sigs)}, groups >3 files: {len(dups)}")
if dups:
    for s,fs in list(dups.items())[:3]: print(f"  {s}: {len(fs)} files - {fs[:4]}")
