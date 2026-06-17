import glob, re, os

report = []
def log(section, msg):
    report.append(f"[{section}] {msg}")

html_files = sorted(glob.glob('tools/*.html')) + ['index.html', 'about.html', 'privacy.html']
tool_files = sorted(glob.glob('tools/*.html'))

# ─────────────────────────────────────────────
# 1. JS 函数检查
# ─────────────────────────────────────────────
log('JS', f'Scanning {len(tool_files)} tool files...')

for fpath in tool_files:
    txt = open(fpath, encoding='utf-8', errors='ignore').read()
    fname = os.path.basename(fpath)

    # 1a. 函数定义在 <script async/defer src=...> 标签内
    for m in re.finditer(r'<script[^>]+src=[^>]+>', txt):
        after = txt[m.end():]
        close = after.find('</script>')
        if close == -1: continue
        inner = after[:close].strip()
        if re.search(r'function\s+\w+', inner):
            log('JS:SRC_INLINE', f'{fname} — function defined inside <script src> tag (will be silently ignored by browser)')

    # 1b. onclick 调用的函数是否有定义
    onclick_fns = set(re.findall(r'onclick="(\w+)\(', txt))
    defined_fns = set(re.findall(r'function\s+(\w+)\s*\(', txt))
    for fn in onclick_fns:
        if fn not in defined_fns and fn not in ('void', 'return'):
            log('JS:UNDEF_FN', f'{fname} — onclick calls "{fn}()" but function not defined')

    # 1c. generateDoc 内部检查
    if 'function generateDoc()' in txt:
        gd_start = txt.find('function generateDoc()')
        depth = 0
        i = txt.find('{', gd_start)
        end = i
        while i < len(txt):
            if txt[i] == '{': depth += 1
            elif txt[i] == '}':
                depth -= 1
                if depth == 0: end = i+1; break
            i += 1
        gd_body = txt[gd_start:end]

        # discAmt/taxAmt 使用但未定义
        for var in ['discAmt', 'taxAmt', 'total']:
            uses = len(re.findall(r'\b'+var+r'\b', gd_body))
            decls = len(re.findall(r'\b(?:const|let|var)\s+'+var+r'\b', gd_body))
            if uses > 0 and decls == 0:
                log('JS:UNDEF_VAR', f'{fname} — generateDoc uses "{var}" but never declares it')

        # sub 用 textContent 取值（旧模板错误）
        if "getElementById('subtotal')?.textContent" in gd_body or "getElementById('subtotal').textContent" in gd_body:
            log('JS:OLD_TEMPLATE', f'{fname} — generateDoc reads sub from textContent instead of calculating from line items')

        # linesHTML/linesTxt 使用但未声明
        for var in ['linesHTML', 'linesTxt']:
            if var in gd_body and 'let '+var not in gd_body and 'const '+var not in gd_body and 'var '+var not in gd_body:
                log('JS:UNDEF_VAR', f'{fname} — generateDoc uses "{var}" without declaring it')

    # 1d. generateInvoiceHTML 调用但未定义
    if 'generateInvoiceHTML(' in txt and 'function generateInvoiceHTML(' not in txt:
        log('JS:UNDEF_FN', f'{fname} — calls generateInvoiceHTML() but function not defined in file')

    # 1e. addRow 调用但未defined
    if 'addRow()' in txt and 'function addRow(' not in txt:
        log('JS:UNDEF_FN', f'{fname} — calls addRow() but function not defined')

    # 1f. calcTotals 调用但未defined
    if 'calcTotals()' in txt and 'function calcTotals(' not in txt:
        log('JS:UNDEF_FN', f'{fname} — calls calcTotals() but function not defined')

    # 1g. copyText 调用但未defined
    if 'copyText()' in txt and 'function copyText(' not in txt:
        log('JS:UNDEF_FN', f'{fname} — calls copyText() but function not defined')

    # 1h. printDoc 调用但未defined
    if 'printDoc()' in txt and 'function printDoc(' not in txt:
        log('JS:UNDEF_FN', f'{fname} — calls printDoc() but function not defined')

    # 1i. template literal escape issue: \` or ${var} outside template
    escaped_bt = txt.count('\\`')
    if escaped_bt > 0:
        log('JS:ESCAPE', f'{fname} — {escaped_bt} escaped backticks (\\`) found — may be broken template literals')

    # 1j. string*number pattern (NaN bug)
    nan_hits = re.findall(r"'[^']{0,20}'\s*\*\s*\d", txt)
    if nan_hits:
        log('JS:NAN_MULTIPLY', f'{fname} — string*number produces NaN: {nan_hits[:2]}')

# ─────────────────────────────────────────────
# 2. 工具名与表单内容匹配
# ─────────────────────────────────────────────
TOOL_MISMATCHES = {
    # 文件名关键词 → 不应出现的表单字段
    'receipt': ['Invoice #', 'id="invNum"', 'Due Date', 'id="dueDate"'],
    'letter':  ['id="lineItems"', 'Add Item', 'Tax Rate'],
    'notice':  ['id="lineItems"', 'Add Item'],
    'agreement': [],  # agreements can have line items
}

for fpath in tool_files:
    txt = open(fpath, encoding='utf-8', errors='ignore').read()
    fname = os.path.basename(fpath)
    base = fname.replace('.html','').replace('-',' ')

    # payment-history 类型检测
    if 'payment-history' in fname:
        if 'id="invNum"' in txt and 'Account #' not in txt:
            log('FORM:MISMATCH', f'{fname} — uses invoice field invNum but is a payment history tool')
        if 'generateInvoiceHTML' in txt:
            log('FORM:MISMATCH', f'{fname} — payment history calls generateInvoiceHTML (wrong function)')

    # receipt 页面不应有 Invoice # label (but ok to have invNum id for compat)
    if 'receipt' in fname and not 'invoice' in fname:
        if '<label>Invoice #</label>' in txt or '<label>Invoice Number</label>' in txt:
            log('FORM:MISMATCH', f'{fname} — receipt page shows "Invoice #" label (should say "Receipt #")')

    # calculator 页面不应有 lineItems table
    if any(x in fname for x in ['calculator', 'rate-calc', 'gst-calc', 'vat-calc', 'tax-calc']):
        if 'id="lineItems"' in txt:
            log('FORM:MISMATCH', f'{fname} — calculator page has lineItems table (likely wrong template)')

# ─────────────────────────────────────────────
# 3. SEO 路径错误
# ─────────────────────────────────────────────
BAD_URL_PATTERNS = [
    r'localhost',
    r'127\.0\.0\.1',
    r'C:[/\\]Users',
    r'file://',
    r'http://billingfixpro',   # should be https
]

for fpath in html_files:
    if not os.path.exists(fpath): continue
    txt = open(fpath, encoding='utf-8', errors='ignore').read()
    fname = os.path.basename(fpath)

    # canonical
    canon = re.findall(r'<link[^>]+rel=["\']canonical["\'][^>]*href=["\']([^"\']+)["\']', txt)
    for url in canon:
        for pat in BAD_URL_PATTERNS:
            if re.search(pat, url, re.I):
                log('SEO:CANONICAL', f'{fname} — bad canonical URL: {url}')

    # og:url
    og_urls = re.findall(r'<meta[^>]+property=["\']og:url["\'][^>]*content=["\']([^"\']+)["\']', txt)
    for url in og_urls:
        for pat in BAD_URL_PATTERNS:
            if re.search(pat, url, re.I):
                log('SEO:OG_URL', f'{fname} — bad og:url: {url}')

    # missing canonical
    if fpath.startswith('tools/') and '<link rel="canonical"' not in txt and '<link rel=\'canonical\'' not in txt:
        log('SEO:NO_CANONICAL', f'{fname} — missing canonical tag')

    # og:title missing
    if fpath.startswith('tools/') and 'og:title' not in txt:
        log('SEO:NO_OG', f'{fname} — missing og:title')

# ─────────────────────────────────────────────
# 4. Logo / Favicon
# ─────────────────────────────────────────────
logo_exists = os.path.exists('logo.svg')
favicon_exists = os.path.exists('favicon.svg')
log('ASSET', f'logo.svg exists: {logo_exists}')
log('ASSET', f'favicon.svg exists: {favicon_exists}')

for fpath in html_files:
    if not os.path.exists(fpath): continue
    txt = open(fpath, encoding='utf-8', errors='ignore').read()
    fname = os.path.basename(fpath)

    # logo img present
    has_logo_img = 'logo.svg' in txt
    if not has_logo_img:
        log('ASSET:LOGO', f'{fname} — no logo.svg reference found')

    # favicon present
    has_fav = 'favicon.svg' in txt or 'favicon.ico' in txt
    if not has_fav:
        log('ASSET:FAVICON', f'{fname} — no favicon reference found')

    # old text logo (plain text in <a class="logo">)
    if re.search(r'<a[^>]+class=["\']logo["\'][^>]*>[^<]{3,30}</a>', txt):
        log('ASSET:TEXT_LOGO', f'{fname} — may have text-only logo (no img tag inside .logo anchor)')

    # absolute local path in logo src
    if re.search(r'src=["\'](?:C:|file://)[^"\']*logo', txt, re.I):
        log('ASSET:LOGO_PATH', f'{fname} — logo uses absolute local path')

# ─────────────────────────────────────────────
# 5. @media print CSS
# ─────────────────────────────────────────────
GOOD_PRINT = '#output{display:block'
OLD_PRINTS = [
    'body>*{display:none!important}',
    'preview-card,.form-card{box-shadow',
]

for fpath in tool_files:
    txt = open(fpath, encoding='utf-8', errors='ignore').read()
    fname = os.path.basename(fpath)

    if '@media print' not in txt:
        log('PRINT:MISSING', f'{fname} — no @media print CSS found')
        continue

    print_css = txt[txt.find('@media print'):txt.find('@media print')+500]

    for old in OLD_PRINTS:
        if old in print_css:
            log('PRINT:OLD_CSS', f'{fname} — uses outdated print CSS pattern: "{old[:40]}"')

    if GOOD_PRINT not in print_css:
        log('PRINT:NO_OUTPUT', f'{fname} — print CSS does not explicitly show #output')

    if '.affiliate-section' not in print_css and '.form-card' not in print_css:
        log('PRINT:INCOMPLETE', f'{fname} — print CSS may not hide form-card or affiliate-section')

# ─────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────
from collections import Counter
cats = Counter(r.split(']')[0][1:] for r in report if r.startswith('['))

summary = [
    '='*70,
    'BILLINGFIXPRO AUDIT REPORT',
    '='*70,
    '',
]
for cat, count in sorted(cats.items()):
    summary.append(f'  {cat:<25} {count:>4} issues')
summary += ['', f'  TOTAL ISSUES: {len(report)}', '', '='*70, '']

full = '\n'.join(summary) + '\n'.join(report) + '\n'
with open('audit-report.txt', 'w', encoding='utf-8') as f:
    f.write(full)

print(full[:3000])
print(f'\n... full report saved to audit-report.txt ({len(report)} issues)')
