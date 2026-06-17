import glob

fixed = 0
for f in glob.glob('C:/Users/Administrator/billingfixpro/tools/*.html'):
    txt = open(f, encoding='utf-8', errors='ignore').read()
    orig = txt

    txt = txt.replace(
        "const extra=typeof window._extra!=='undefined'?window._extra:(document.getElementById('extra')?.textContent||'');\n  document.getElementById('preview').innerHTML=generateInvoiceHTML(from_,to_,num_,date_,due_,linesHTML,sub,discAmt,taxAmt,total,notes,taxRate,extra||'');",
        "document.getElementById('preview').innerHTML=generateInvoiceHTML(from_,to_,num_,date_,due_,linesHTML,sub,discAmt,taxAmt,total,notes,taxRate,typeof extra!=='undefined'?extra:'');"
    )

    if txt != orig:
        open(f, 'w', encoding='utf-8').write(txt)
        fixed += 1

print(f'fixed: {fixed} files')
