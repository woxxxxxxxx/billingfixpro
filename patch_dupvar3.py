import re

f = 'C:/Users/Administrator/billingfixpro/tools/payment-plan-agreement.html'
txt = open(f, encoding='utf-8').read()

def fix_all_dups(js):
    seen = set()
    def replacer(m):
        varname = m.group(2)
        if varname in seen:
            return varname + m.group(3)
        seen.add(varname)
        return m.group(0)
    return re.sub(r'\b(const|let) (\w+)(=)', replacer, js)

new_txt = re.sub(r'<script>(.*?)</script>',
    lambda m: '<script>' + fix_all_dups(m.group(1)) + '</script>' if 'generateDoc' in m.group(1) else m.group(0),
    txt, flags=re.DOTALL)

if new_txt != txt:
    open(f, 'w', encoding='utf-8').write(new_txt)
    print('fixed payment-plan-agreement.html')
else:
    print('no change')
