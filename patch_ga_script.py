with open('tools/payment-history.html', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''<script async src="https://www.googletagmanager.com/gtag/js?id=G-TPVMTCEC3E">
function generateInvoiceHTML(from_,to_,num_,date_,due_,linesHTML,sub,discAmt,taxAmt,total,notes,taxRate,extra){'''

new = '''<script async src="https://www.googletagmanager.com/gtag/js?id=G-TPVMTCEC3E">
</script>
<script>
function generateInvoiceHTML(from_,to_,num_,date_,due_,linesHTML,sub,discAmt,taxAmt,total,notes,taxRate,extra){'''

if old in content:
    content = content.replace(old, new)
    with open('tools/payment-history.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('fixed payment-history.html')
else:
    print('pattern not found - checking actual content around generateInvoiceHTML:')
    idx = content.find('function generateInvoiceHTML')
    print(repr(content[idx-80:idx+40]))
