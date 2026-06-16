import re

f = 'C:/Users/Administrator/billingfixpro/index.html'
txt = open(f, encoding='utf-8').read()
txt = re.sub(r'<a href="/tools/invoice-generator\.html">Invoices</a>\s*', '', txt)
txt = re.sub(r'<a href="/tools/quote-generator\.html">Quotes</a>\s*', '', txt)
txt = re.sub(r'<a href="/tools/receipt-generator\.html">Receipts</a>\s*', '', txt)
txt = re.sub(r'<a href="/tools/invoice-calculator\.html">Calculators</a>\s*', '', txt)
open(f, 'w', encoding='utf-8').write(txt)
print('nav cleaned')
