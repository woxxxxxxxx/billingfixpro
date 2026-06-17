import glob, re

HTML_GENERATOR = r"""
function generateInvoiceHTML(from_,to_,num_,date_,due_,linesHTML,sub,discAmt,taxAmt,total,notes,taxRate,extra){
  const title=(document.querySelector('h1')||{textContent:'Invoice'}).textContent.replace(' Generator','').replace(' Tool','').replace(' Maker','');
  return `<div style="font-family:'Helvetica Neue',Arial,sans-serif;max-width:680px;padding:40px;background:#fff;border-radius:12px;box-shadow:0 4px 24px rgba(0,0,0,0.08)">
    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:32px;padding-bottom:24px;border-bottom:2px solid #0891b2">
      <div>
        <div style="font-size:26px;font-weight:800;color:#0891b2;letter-spacing:-0.5px">${title}</div>
        <div style="font-size:13px;color:#64748b;margin-top:6px">Invoice #${num_}</div>
        <div style="font-size:13px;color:#64748b">Date: ${date_}${due_?' &nbsp;|&nbsp; Due: '+due_:''}</div>
      </div>
      <div style="text-align:right;font-size:13px;color:#475569">
        <div style="font-weight:700;color:#0f172a;margin-bottom:4px">From</div>
        <div>${from_}</div>
      </div>
    </div>
    <div style="background:#f0f9ff;border-left:3px solid #0891b2;padding:14px 18px;border-radius:0 8px 8px 0;margin-bottom:24px;font-size:13px">
      <div style="font-weight:700;color:#0f172a;margin-bottom:4px">Bill To</div>
      <div style="color:#475569">${to_}</div>
      ${extra?'<div style="color:#64748b;margin-top:6px;font-size:12px">'+extra+'</div>':''}
    </div>
    <table style="width:100%;border-collapse:collapse;margin-bottom:24px;font-size:13px">
      <thead><tr style="background:#0891b2">
        <th style="color:#fff;padding:11px 14px;text-align:left;border-radius:6px 0 0 0">Description</th>
        <th style="color:#fff;padding:11px 14px;text-align:right">Qty</th>
        <th style="color:#fff;padding:11px 14px;text-align:right">Unit Price</th>
        <th style="color:#fff;padding:11px 14px;text-align:right;border-radius:0 6px 0 0">Total</th>
      </tr></thead>
      <tbody>${linesHTML}</tbody>
    </table>
    <div style="display:flex;justify-content:flex-end">
      <div style="min-width:240px;font-size:13px">
        <div style="display:flex;justify-content:space-between;padding:6px 0;color:#475569"><span>Subtotal</span><strong>$${sub.toFixed(2)}</strong></div>
        ${discAmt>0?'<div style="display:flex;justify-content:space-between;padding:6px 0;color:#dc2626"><span>Discount</span><strong>-$'+discAmt.toFixed(2)+'</strong></div>':''}
        ${taxAmt>0?'<div style="display:flex;justify-content:space-between;padding:6px 0;color:#475569"><span>Tax ('+taxRate+'%)</span><strong>$'+taxAmt.toFixed(2)+'</strong></div>':''}
        <div style="display:flex;justify-content:space-between;padding:10px 0;margin-top:6px;border-top:2px solid #0891b2;font-size:16px;font-weight:800;color:#0891b2"><span>Total Due</span><span>$${total.toFixed(2)}</span></div>
      </div>
    </div>
    ${notes?'<div style="margin-top:20px;padding-top:16px;border-top:1px solid #e2e8f0;font-size:12px;color:#64748b"><strong style="color:#475569">Notes:</strong> '+notes+'</div>':''}
  </div>`;
}
"""

HTML_LINES_PATTERN = """
  let linesHTML='',linesTxt='';
  document.querySelectorAll('#lineItems tr').forEach(tr=>{
    const inputs=tr.querySelectorAll('input');if(inputs.length<3)return;
    const d=inputs[0].value||'Service';
    const q=parseFloat(inputs[1].value)||0;
    const r=parseFloat(inputs[2].value)||0;
    const tot=q*r;
    linesHTML+=`<tr style="border-bottom:1px solid #f1f5f9"><td style="padding:10px 14px">${d}</td><td style="padding:10px 14px;text-align:right">${q}</td><td style="padding:10px 14px;text-align:right">$${r.toFixed(2)}</td><td style="padding:10px 14px;text-align:right;font-weight:600">$${tot.toFixed(2)}</td></tr>`;
    linesTxt+=`  ${d}  x${q}  $${r.toFixed(2)}  $${tot.toFixed(2)}\\n`;
  });"""

fixed = 0
for f in glob.glob('C:/Users/Administrator/billingfixpro/tools/*.html'):
    txt = open(f, encoding='utf-8', errors='ignore').read()
    orig = txt

    # 1. <pre id="preview"> → <div id="preview">
    txt = re.sub(r'<pre id="preview"[^>]*>.*?</pre>',
                 '<div id="preview"></div><pre id="preview-txt" style="display:none"></pre>',
                 txt, flags=re.DOTALL)

    # 2. 注入 generateInvoiceHTML 函数
    if 'generateInvoiceHTML' not in txt:
        txt = txt.replace('</script>', HTML_GENERATOR + '\n</script>', 1)

    # 3. 替换 lines 变量构建
    txt = re.sub(
        r"let lines='';.*?document\.querySelectorAll\('#lineItems tr'\)\.forEach\(tr=>\{.*?\}\);",
        HTML_LINES_PATTERN.strip(),
        txt, flags=re.DOTALL, count=1
    )
    txt = re.sub(
        r"let linesText='';.*?document\.querySelectorAll\('#lineItems tr'\)\.forEach\(tr=>\{.*?\}\);",
        HTML_LINES_PATTERN.strip(),
        txt, flags=re.DOTALL, count=1
    )

    # 4. 替换 textContent 设置为 innerHTML
    txt = re.sub(
        r"document\.getElementById\('preview'\)\.textContent\s*=\s*\w+\s*;",
        """const extra=typeof window._extra!=='undefined'?window._extra:(document.getElementById('extra')?.textContent||'');
  document.getElementById('preview').innerHTML=generateInvoiceHTML(from_,to_,num_,date_,due_,linesHTML,sub,discAmt,taxAmt,total,notes,taxRate,extra||'');
  document.getElementById('preview-txt').textContent=linesTxt;""",
        txt, count=1
    )

    # 5. Copy Text 改用 preview-txt
    txt = txt.replace(
        "navigator.clipboard.writeText(document.getElementById('preview').textContent)",
        "navigator.clipboard.writeText(document.getElementById('preview-txt')?.textContent||document.getElementById('preview')?.innerText||'')"
    )

    if txt != orig:
        open(f, 'w', encoding='utf-8').write(txt)
        fixed += 1

print(f'fixed: {fixed} files')
