import glob, re

favicon_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 48" width="64" height="48">
  <defs><linearGradient id="g" x1="0" y1="0" x2="64" y2="48" gradientUnits="userSpaceOnUse"><stop offset="0%" stop-color="#0891b2"/><stop offset="100%" stop-color="#06b6d4"/></linearGradient></defs>
  <line x1="6" y1="10" x2="58" y2="10" stroke="url(#g)" stroke-width="7" stroke-linecap="round"/>
  <line x1="6" y1="24" x2="46" y2="24" stroke="url(#g)" stroke-width="7" stroke-linecap="round"/>
  <line x1="6" y1="38" x2="30" y2="38" stroke="url(#g)" stroke-width="7" stroke-linecap="round"/>
  <polyline points="34,44 38,48 48,36" fill="none" stroke="url(#g)" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>'''

logo_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 280 52" width="280" height="52">
  <defs><linearGradient id="g" x1="0" y1="0" x2="56" y2="52" gradientUnits="userSpaceOnUse"><stop offset="0%" stop-color="#0891b2"/><stop offset="100%" stop-color="#06b6d4"/></linearGradient></defs>
  <line x1="4" y1="14" x2="52" y2="14" stroke="url(#g)" stroke-width="6" stroke-linecap="round"/>
  <line x1="4" y1="26" x2="42" y2="26" stroke="url(#g)" stroke-width="6" stroke-linecap="round"/>
  <line x1="4" y1="38" x2="26" y2="38" stroke="url(#g)" stroke-width="6" stroke-linecap="round"/>
  <polyline points="30,44 34,48 44,36" fill="none" stroke="url(#g)" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/>
  <text x="66" y="26" font-family="-apple-system,BlinkMacSystemFont,\'Inter\',\'Segoe UI\',sans-serif" font-size="19" font-weight="700" fill="#0c4a6e" letter-spacing="-0.4" dominant-baseline="central">Billing<tspan fill="#0891b2">Fix</tspan><tspan fill="#64748b" font-weight="500">Pro</tspan></text>
</svg>'''

open('C:/Users/Administrator/billingfixpro/logo.svg', 'w', encoding='utf-8').write(logo_svg)
open('C:/Users/Administrator/billingfixpro/favicon.svg', 'w', encoding='utf-8').write(favicon_svg)
print('SVG written')

trust_bar = '''<div class="trust-bar">
  <div class="trust-inner">
    <span>✓ 100% Free</span>
    <span>✓ No Signup Required</span>
    <span>✓ No Watermark</span>
    <span>✓ Download as PDF</span>
    <span>✓ 100+ Tools</span>
  </div>
</div>'''

trust_css = '''
.trust-bar{background:#ecfeff;border-bottom:1px solid #a5f3fc;padding:10px 20px}
.trust-inner{max-width:1100px;margin:0 auto;display:flex;gap:28px;justify-content:center;flex-wrap:wrap}
.trust-inner span{font-size:13px;font-weight:600;color:#0891b2;white-space:nowrap}
'''

f = 'C:/Users/Administrator/billingfixpro/index.html'
txt = open(f, encoding='utf-8').read()

# 1. 文字 logo → img
txt = re.sub(r'<a href="/" class="logo">Billing<span>Fix</span>Pro</a>',
    '<a href="/" class="logo"><img src="/logo.svg" alt="BillingFixPro" height="38"></a>', txt)

# 2. Nav CTA
txt = txt.replace('<a href="/about.html" class="nav-cta">About</a>',
    '<a href="/tools/invoice-generator.html" class="nav-cta">Create Invoice</a>')

# 3. Canonical 大小写修复
txt = txt.replace('https://BillingFixPro.com/', 'https://billingfixpro.com/')

# 4. Hero 标题
txt = txt.replace('<h1>Free Invoice &amp; Billing Tools for Freelancers</h1>',
    '<h1>Free Invoice &amp; Billing Tools — 100+ Templates</h1>')

# 5. 信任栏 CSS
txt = txt.replace('</style>', trust_css + '</style>', 1)

# 6. 信任栏插入 hero 后
txt = re.sub(r'(</div>\s*\n)(.*?<div class="cat-tabs")',
    r'\1' + trust_bar + r'\n\2', txt, count=1, flags=re.DOTALL)

# 7. favicon svg-only
txt = re.sub(r'<link rel="icon"[^>]*favicon\.ico[^>]*>', '', txt)
txt = re.sub(r'<link rel="icon"[^>]*favicon\.png[^>]*>', '', txt)

open(f, 'w', encoding='utf-8').write(txt)
print('index.html done')

# 工具页
count = 0
for fp in glob.glob('C:/Users/Administrator/billingfixpro/**/*.html', recursive=True):
    if fp.replace('\\', '/').endswith('index.html'):
        continue
    t = open(fp, encoding='utf-8').read()
    orig = t
    t = re.sub(r'<a href="/" class="logo">Billing<span>Fix</span>Pro</a>',
        '<a href="/" class="logo"><img src="/logo.svg" alt="BillingFixPro" height="38"></a>', t)
    t = t.replace('https://BillingFixPro.com/', 'https://billingfixpro.com/')
    t = re.sub(r'<link rel="icon"[^>]*favicon\.ico[^>]*>', '', t)
    if t != orig:
        open(fp, 'w', encoding='utf-8').write(t)
        count += 1

print(f'tool pages updated: {count}')
print('all done')
