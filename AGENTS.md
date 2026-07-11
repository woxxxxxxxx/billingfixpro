# BillingFixPro

## 基础信息
- 域名：billingfixpro.com
- 主色：#0891b2（青）
- GA ID：G-TPVMTCEC3E
- 工具/内容数量：100 工具
- 部署方式：GitHub Pages（git push origin master）

## 当前进度
- AdSense 状态：正在准备
- 上次审计完成：待开始
- 下一步：内容深化 + AdSense 申请

## 专属配置
- 特殊：payment-history 在批量脚本中必须排除（专属逻辑被覆盖过3次）

## 关键修复历史
- window.open() 新窗口打印方案替代 @media print（Chrome 优先级 bug）
- generateDoc 接 generateInvoiceHTML（payment-history 专属函数）

## 待办
- [ ] 审计全站
- [ ] 内容深化
- [ ] 申请 AdSense
- [ ] 确认 payment-history 页面逻辑完整性


## 2026-06-28 AdSense ????
- Blog ??/??? 16 ????????????? sitemap.xml?
- ??????????/?????????


## 2026-07-01 search-click acceleration
- Added 3 search-intent guide hub pages based on recent Search Console exposure.
- Updated title/meta descriptions for high-impression, low-CTR pages and added a homepage entry block for the new guides.
- Regenerated sitemap.xml with lastmod=2026-07-01. Goal: improve long-tail relevance, internal link strength, and search-result click clarity.

## 2026-07-11 portfolio AdSense preflight
- 2026-07-11 preflight: 16 thin batch blog pages and 4 thin guide pages were removed from the index and AdSense inventory. The 100 functional invoice/template pages remain the primary publisher value. Added Editorial Policy, Contact, and Terms pages.
- Required release check: `node C:\\Users\\Administrator\\pm-worker\\adsense-release-gate.js billingfixpro`. Do not submit or deploy after a failed gate.
