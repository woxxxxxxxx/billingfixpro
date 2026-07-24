# BillingFixPro

## 基础信息
- 域名：billingfixpro.com
- 主题：发票、收款、付款跟踪与小企业账单流程
- 主色：`#0891b2`
- GA4：`G-TPVMTCEC3E`
- AdSense：`ca-pub-1638874323475457`
- 部署：GitHub Pages，`master` 分支

## 当前审核面
- 2026-07-24 重建为 19 个可收录页面，其中包含 6 篇独立的流程指南。
- 其余批量工具、旧博客和旧搜索指南继续保持 `noindex`，并移除 AdSense。
- 6 篇指南的中位字数约 599，均有独立流程、检查清单、决策表、来源和免责声明。
- 首页只保留一个“Billing workflow library”内容入口，避免多个重复目录稀释核心审核面。
- 观察期：2026-07-24 至 2026-08-07。观察期内不做大规模页面发布。

## 首批已发布指南
- `blog/invoice-best-practices.html`
- `blog/estimate-vs-invoice.html`
- `blog/accounts-receivable-aging.html`
- `blog/late-payment-reminders.html`
- `blog/receipt-management-guide.html`
- `blog/partial-payment-invoices.html`

## 发布规则
- 内容发布脚本：`C:\Users\Administrator\pm-worker\billingfixpro-release-guides.js`
- 收录白名单：`C:\Users\Administrator\pm-worker\adsense-preflight-remediate.js`
- 发布前必须通过：
  - `node C:\Users\Administrator\pm-worker\adsense-release-gate.js billingfixpro`
  - `node C:\Users\Administrator\pm-worker\adsense-semantic-audit.js C:\Users\Administrator\billingfixpro`
- 手机页面不得横向溢出；每个可收录页面只能有一个 H1。
- `payment-history` 有专属逻辑，禁止被旧批量脚本覆盖。

## 下一步
- [ ] 观察 Search Console 抓取与索引变化到 2026-08-07
- [ ] 观察 AdSense 状态，不在观察期重复提交
- [ ] 根据真实搜索词选择第二批内容，不批量放行旧模板页
- [ ] 第二批优先考虑支付跟踪、发票编号和周期账单，但必须先完成独立重写
