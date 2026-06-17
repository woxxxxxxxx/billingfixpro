import re

fixes = {
    'C:/Users/Administrator/billingfixpro/tools/cash-receipt.html':
        ('const tendered', 'tendered'),
    'C:/Users/Administrator/billingfixpro/tools/deposit-invoice.html':
        ('const projTotal', 'projTotal'),
    'C:/Users/Administrator/billingfixpro/tools/payment-plan-agreement.html':
        ('const origAmt', 'origAmt'),
    'C:/Users/Administrator/billingfixpro/tools/progress-billing.html':
        ('const pct', 'pct'),
    'C:/Users/Administrator/billingfixpro/tools/rush-invoice.html':
        ('const rushPct', 'rushPct'),
}

for f, (const_decl, varname) in fixes.items():
    txt = open(f, encoding='utf-8').read()
    # 找到所有 const X= 出现位置
    matches = [(m.start(), m.end()) for m in re.finditer(re.escape(const_decl) + r'\b', txt)]
    if len(matches) >= 2:
        # 把第二次出现的 const X 改成 X（去掉 const）
        second_start = matches[1][0]
        txt = txt[:second_start] + txt[second_start:].replace(const_decl, varname, 1)
        open(f, 'w', encoding='utf-8').write(txt)
        print(f'fixed duplicate const {varname} in {f.split("/")[-1]}')
    else:
        print(f'only {len(matches)} occurrence(s) of {const_decl} in {f.split("/")[-1]} - skip')
