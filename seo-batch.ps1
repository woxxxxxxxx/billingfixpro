# BillingFixPro SEO Batch Processor
# Expands seo-section to 300+ words, adds FAQ (5 Q&As), adds 3 extra related links
# Run per batch: pass -Batch 1..5

param([int]$Batch = 0)

$toolsDir = "C:\Users\Administrator\billingfixpro\tools"
$allFiles = @(Get-ChildItem -Path $toolsDir -Filter "*.html" | Sort-Object Name)

# ── FAQ / extra-link CSS ──────────────────────────────────────────────────────
$FAQCss = '.faq-section{background:var(--bg2);border:1px solid var(--border);border-radius:var(--radius);padding:32px;box-shadow:var(--shadow);margin-bottom:24px}.faq-section h2{font-size:1.1rem;font-weight:700;margin-bottom:20px}.faq-item{border-bottom:1px solid var(--border);padding:16px 0}.faq-item:last-child{border-bottom:none;padding-bottom:0}.faq-item h3{font-size:14px;font-weight:700;color:var(--text);margin-bottom:8px}.faq-item p{font-size:14px;color:var(--text2);line-height:1.7}'

# ── Categorise by slug ────────────────────────────────────────────────────────
function Get-Cat([string]$slug) {
    if ($slug -match 'receipt')                                       { return 'receipt' }
    if ($slug -match 'quote|estimate|proposal')                        { return 'quote' }
    if ($slug -match 'calculator|rate')                                { return 'calc' }
    if ($slug -match 'agreement|retainer|purchase.order|work.order|service.order|blanket|change.order') { return 'order' }
    if ($slug -match 'reminder|collection|final.notice|outstanding|overdue') { return 'notice' }
    if ($slug -match 'template|to.pdf|tracker|checklist|number.gen|history|terms.gen|progress|return|statement') { return 'admin' }
    return 'invoice'   # default
}

# ── SEO text generator (~300+ words) ─────────────────────────────────────────
function Get-Seo([string]$name, [string]$slug) {
    $cat = Get-Cat $slug
    switch ($cat) {
        'invoice' { return @"
<h2>About $name</h2>
<p>BillingFixPro's $name is a free, professional-grade online tool built for freelancers, independent contractors, consultants, and small business owners who need to produce accurate, client-ready invoices without expensive software or monthly subscriptions. Whether you are billing a one-time client or managing recurring work, this tool generates polished invoice documents in under a minute — no account creation, no downloads, and no cost whatsoever.</p>
<p>Manually assembling invoices in a word processor or spreadsheet wastes time and introduces calculation errors that can damage client relationships. Our $name eliminates both problems by automating every calculation — subtotals, tax, discounts, and the final amount due — and formatting the result into a clean, professional layout. You control the content; the tool handles the rest.</p>
<p>Key features include support for multiple line items with custom descriptions, quantities, and rates; configurable tax rates; optional discount fields; customizable payment terms and due dates; and instant PDF generation. Whether you charge a flat project fee, bill by the hour, or combine services and materials in a single invoice, the tool adapts seamlessly to your billing model.</p>
<p>The $name is particularly valuable for professionals who invoice clients regularly and need a dependable, consistent solution. Graphic designers, web developers, photographers, copywriters, tradespeople, tutors, marketing consultants, and agencies across every industry rely on fast, professional billing tools to maintain cash flow and project a credible image. A well-formatted invoice reduces disputes, speeds up payment, and reinforces your professional brand.</p>
<p>Getting started takes seconds. Fill in your business name and contact details, add your client's information, enter your line items, set your tax rate if applicable, and click Generate. Your invoice is ready to download as a PDF, print, or copy into another application. BillingFixPro stores none of your data — everything is processed privately in your browser.</p>
<p>BillingFixPro is dedicated to giving every business owner access to professional billing tools regardless of budget. Our $name is part of a full suite of free financial document tools covering quotes, receipts, payment agreements, and more. Bookmark this page and return whenever you need to create a professional invoice — fast, free, and hassle-free every time.</p>
"@ }
        'receipt' { return @"
<h2>About $name</h2>
<p>The $name from BillingFixPro makes it simple to generate accurate, professional receipts for any completed transaction. Whether you are a small business owner confirming payment, a landlord issuing a rent acknowledgment, a freelancer documenting a deposit, or an individual recording a private sale, this free online tool produces a clean, printable receipt document in seconds — no registration, no software, no cost.</p>
<p>Paper receipts are easily lost and handwritten ones look unprofessional. A plain text email receipt lacks structure and credibility. BillingFixPro's $name solves these problems by creating well-formatted, professional-looking receipts that include all the essential information: transaction date, payer and payee details, itemised description, amount paid, payment method, and any applicable taxes.</p>
<p>The tool is designed for speed. Fill in the fields — business name, client name, date, description of goods or services, and amount — click Generate, and you have a professional receipt ready to download, print, or email. The layout is clean and universally readable, suitable for attaching to expense reports, providing to customers, including with shipped goods, or storing in financial records.</p>
<p>Receipts are essential business documents. They provide proof of payment, support expense claims, satisfy tax record-keeping requirements, and build customer trust. Having a reliable $name means you are always prepared to issue professional documentation the moment a transaction is complete — whether in the office, at a client site, or on the go from a mobile device.</p>
<p>The $name is used by retail businesses, service providers, freelancers, landlords, charities collecting donations, event organisers, and countless other professionals who transact regularly and need reliable receipt documentation. All generated documents are formatted to a professional standard appropriate for business use.</p>
<p>BillingFixPro provides this $name along with dozens of other free billing and financial tools — invoices, quotes, calculators, payment agreements, and more. There are no usage limits, no subscription tiers, and no hidden fees. Create as many receipts as your business requires, any time of day, on any device.</p>
"@ }
        'quote' { return @"
<h2>About $name</h2>
<p>BillingFixPro's $name helps businesses and professionals create detailed, client-ready quotes and estimates that win projects and set clear financial expectations from the outset. A well-structured quote is often the first formal document a potential client receives from your business, and making a strong first impression directly influences whether you win the work. Our free tool ensures every quote you send is polished, complete, and professional.</p>
<p>Writing quotes from scratch in a word processor is inconsistent and time-consuming. Our $name standardises the process with a structured form covering all essential information: your business details, client contact information, a description of the proposed work or goods, individual line items with quantities and pricing, applicable taxes or discounts, and a validity period. The tool formats everything into a professional quote document ready to share, print, or attach to an email.</p>
<p>Key advantages include automatic total calculation with full tax and discount support, customisable line items for multi-phase or complex projects, clear itemisation that shows clients exactly what they are paying for, and a professional layout that builds confidence and trust in your business. You can generate unlimited quotes at no cost, with no account required.</p>
<p>Quotes and estimates are used across virtually every industry. General contractors use them to bid on construction and renovation jobs. Designers outline project scope and deliverables. Marketing agencies propose campaign costs. Caterers quote event menus. IT consultants estimate development projects. Whatever your field, responding quickly with a clear, professional quote improves your win rate and reduces back-and-forth with clients.</p>
<p>Once a quote is approved, BillingFixPro also offers a full Invoice Generator to convert the approved scope into a billing document — keeping your financial workflow consistent from proposal to payment. All tools in the suite are free and available without registration, making BillingFixPro the ideal platform for independent professionals and small businesses at every stage of their client relationships.</p>
<p>Save time, win more business, and present a professional image with every quote you send. The $name gives you everything you need to respond to client enquiries confidently and efficiently, any time and from any device.</p>
"@ }
        'calc' { return @"
<h2>About $name</h2>
<p>The $name from BillingFixPro is a free, accurate, and easy-to-use online calculation tool designed for freelancers, business owners, accountants, and financial professionals who need instant, reliable billing-related calculations. Manual calculations are prone to errors — even small mistakes in invoices, tax amounts, or rate estimates can affect cash flow, client relationships, and tax compliance. Our tool eliminates those risks with instant, verified results.</p>
<p>Whether you need to determine the right billing rate, calculate the tax component of an invoice, estimate total project costs, or figure out the cost impact of a discount, the $name gives you accurate answers immediately. The interface is intentionally simple: enter your values, see the calculated result with a full breakdown of how each number was derived. No guesswork, no spreadsheets, no manual formulas required.</p>
<p>Accuracy in financial calculations is fundamental to running a profitable business. Undercharging clients because of a rate calculation error, applying the wrong tax percentage, or underestimating project costs can significantly erode your margins over time. The $name gives you the confidence of verified numbers — so every invoice, quote, or financial estimate you produce is based on correct calculations from the start.</p>
<p>The tool is fully responsive and works on all devices including smartphones, tablets, and desktop computers. This means you can run calculations on-the-spot while meeting clients, preparing proposals, or discussing project scope — without needing to return to the office or open a separate application. Real-time calculation ensures you always have accurate numbers at your fingertips.</p>
<p>Our $name is part of BillingFixPro's comprehensive library of free billing and financial tools, which includes invoice generators, receipt makers, quote builders, payment agreement templates, and additional calculators covering taxes, discounts, rates, and project costs. Every tool in the suite is free, without registration, and without usage limits.</p>
<p>Spend less time with a calculator and more time doing billable work. The $name is here whenever you need quick, accurate financial calculations — free, reliable, and always available.</p>
"@ }
        'order' { return @"
<h2>About $name</h2>
<p>BillingFixPro's $name makes it straightforward to create formal, professional documents that govern purchasing, service delivery, and payment arrangements between businesses and their clients or suppliers. Properly documented agreements protect both parties, establish clear expectations, and provide an essential paper trail for accounting, auditing, and dispute resolution. Our free online tool makes creating these documents fast and easy.</p>
<p>Creating formal business documents from scratch can be daunting, especially without a legal or administrative background. Our $name guides you through the process with a structured form that covers all the essential fields: party information, scope of work or goods, pricing, delivery timelines, payment terms, and any special conditions. The tool generates a professional, complete document ready for review and signature in minutes.</p>
<p>Key features include customisable terms and conditions fields, detailed line-item support for complex orders or service arrangements, automatic total calculation, and instant PDF download. The clean, professional layout is appropriate for formal business use and meets the standard expectations of suppliers, clients, and financial record-keepers.</p>
<p>Whether you are purchasing goods from a supplier, engaging a contractor for project work, establishing a payment plan with a client, or formalising an ongoing service relationship, having the right documentation in place from the start is critical. Formal documents reduce misunderstandings, provide legal clarity, and ensure all parties are aligned on terms before money changes hands or work begins.</p>
<p>The $name is used by small businesses, procurement teams, project managers, freelancers, and finance professionals across every industry. It is particularly valuable for businesses that need professional document templates without the cost of hiring a lawyer or purchasing enterprise software. You get a complete, professional document in minutes at no charge.</p>
<p>BillingFixPro offers this $name as part of a comprehensive suite of free billing and financial tools covering the full document lifecycle — from initial quotes and orders through invoices, receipts, and payment follow-ups. No registration required, no usage limits, and no cost — ever.</p>
"@ }
        'notice' { return @"
<h2>About $name</h2>
<p>The $name from BillingFixPro helps businesses and professionals communicate clearly, professionally, and effectively about outstanding payments, overdue accounts, and billing matters. Whether you are sending a friendly first reminder or a formal final notice, the language and format of your payment communications directly affect your likelihood of collecting payment while preserving the client relationship. Our free tool gives you professional, effective notices every time.</p>
<p>Writing payment notices from scratch is awkward — too casual and clients may ignore the communication; too aggressive and you risk damaging a valuable relationship permanently. Our $name provides professionally worded templates that you can customise with your specific details: the amount owed, the original due date, applicable late fees, and the requested action. The result strikes the right balance of firmness and professionalism.</p>
<p>Key features of our $name include clear, professional language calibrated for business correspondence, customisable fields for amounts, dates, invoice numbers, and account details, and instant PDF generation for sending as an email attachment or printing for postal delivery. The document layout is formal and credible, increasing the likelihood that your communication is taken seriously and acted upon promptly.</p>
<p>Research consistently shows that timely, professional follow-up on overdue invoices significantly increases collection rates. Businesses that send structured payment reminders collect outstanding amounts faster and spend less time in protracted disputes. Our $name enables you to respond quickly to payment delays — before they escalate — with professional, documented communications that create a paper trail if further action becomes necessary.</p>
<p>The $name is used by small business owners, freelancers, property managers, accounting professionals, and finance departments across every sector. It is particularly valuable for businesses that manage a portfolio of clients and need a fast, consistent approach to accounts receivable follow-up that does not require a dedicated collections team.</p>
<p>BillingFixPro provides this $name alongside a full suite of billing tools — invoices, receipts, quotes, payment agreements, and calculators — all completely free and available without registration. Manage your entire billing lifecycle from a single platform at no cost.</p>
"@ }
        default { return @"
<h2>About $name</h2>
<p>BillingFixPro's $name is a free, professional-grade online tool designed to streamline your billing and financial document workflow. Whether you are a freelancer, small business owner, or financial professional, this tool provides everything you need to produce accurate, polished documents quickly and easily — no account required, no software to install, and completely free to use.</p>
<p>Our $name is designed for real-world business needs. The interface is clean and intuitive, allowing you to complete your task efficiently without navigating complex menus or reading lengthy instructions. Enter your information, and the tool takes care of formatting, calculations, and layout — delivering a professional result ready for immediate use.</p>
<p>Quality billing documentation is essential for every business. It creates clear financial records, communicates professionalism to clients and partners, and provides the paper trail required for accounting, tax filing, and audits. Our $name ensures your financial documents meet professional standards every time, regardless of your design or technical background.</p>
<p>Consistency in documentation saves time and reduces errors. Rather than recreating documents from scratch each time, BillingFixPro gives you a reliable, standardised tool that produces consistent output across every use. This makes it easier to maintain organised records, respond quickly to client requests, and keep your billing process running smoothly even during busy periods.</p>
<p>The $name is part of BillingFixPro's extensive library of free billing and financial tools, covering the complete document lifecycle — from initial quotes and purchase orders through invoices, receipts, payment agreements, and follow-up notices. Each tool is designed to integrate seamlessly into a professional billing workflow, giving you everything you need in one place.</p>
<p>We are committed to providing small businesses, freelancers, and independent professionals with the same quality of tools that larger companies access through expensive software — at zero cost. BillingFixPro believes professional billing tools should be accessible to everyone. Use this tool as often as you need, on any device, any time — always free.</p>
"@ }
    }
}

# ── FAQ generator (5 Q&As) ────────────────────────────────────────────────────
function Get-Faq([string]$name, [string]$slug) {
    $cat = Get-Cat $slug
    $qa = switch ($cat) {
        'invoice' { @(
            @("Is the $name completely free to use?",
              "Yes, BillingFixPro's $name is 100% free with no hidden charges, subscription fees, or credit card requirements. You can create and download unlimited invoices at absolutely no cost."),
            @("Do I need to create an account to use the $name?",
              "No account or registration is needed. Simply visit the page, enter your details, and generate your invoice immediately. All processing happens in your browser — your data is never stored on our servers."),
            @("What formats can I download my invoice in?",
              "You can download your invoice as a PDF for professional sharing or archiving, or copy the formatted text to paste into Microsoft Word, Excel, Google Docs, or any other application."),
            @("Does the $name calculate taxes and discounts automatically?",
              "Yes. Enter your tax rate as a percentage and any discount amount, and the tool automatically calculates tax, applies the discount, and displays a complete breakdown including subtotal, tax, discount, and total due."),
            @("Is my invoice data stored or shared with anyone?",
              "No. All data you enter is processed locally in your browser and is never sent to BillingFixPro's servers. Your business and client information remains completely private and secure.")
        )}
        'receipt' { @(
            @("Is the $name free to use?",
              "Yes, completely free. BillingFixPro's $name requires no account, no subscription, and no payment. Generate as many receipts as your business needs at no cost."),
            @("Are receipts created with this tool legally valid?",
              "Receipts generated by our tool include all standard information found in a valid business receipt — transaction details, parties, amounts, and date. Specific legal requirements vary by jurisdiction, so check local regulations for your use case."),
            @("Can I customise the receipt with my business details?",
              "Yes. Enter your business name, address, and contact information in the provided fields. The generated receipt will display your details in a professional layout suitable for customer-facing use."),
            @("Can I print the receipt directly from my browser?",
              "Yes. After generating your receipt, click the Print or Download PDF button to open your browser's print dialogue. You can print to a physical printer or save directly as a PDF file."),
            @("Is my transaction data stored by BillingFixPro?",
              "No. All data you enter is processed in your browser only and is never transmitted to or stored on our servers. Your financial and personal information stays completely private.")
        )}
        'quote' { @(
            @("Is the $name free to use?",
              "Yes, BillingFixPro's $name is 100% free. No plans, no subscriptions, no fees — create as many quotes as you need with no account required."),
            @("Can I convert an approved quote into an invoice?",
              "While the $name creates a standalone document, BillingFixPro also provides a dedicated Invoice Generator. Use the details from your approved quote to quickly create a matching invoice when work is complete or payment is due."),
            @("How long should a quote remain valid?",
              "You can specify a validity date or expiry period in the relevant field. Standard business practice is to set a validity window of 14 to 30 days, after which pricing, availability, and materials costs may change."),
            @("Can I include multiple line items with different prices?",
              "Yes. The $name supports multiple line items, each with a description, quantity, and unit price. The tool automatically calculates individual line totals, applies tax or discounts, and displays the overall total."),
            @("Is my quote data saved or accessible by BillingFixPro?",
              "No. All data entered is processed locally in your browser and is never stored on our servers. Your client details, pricing, and project information remain private and secure.")
        )}
        'calc' { @(
            @("Is the $name free to use?",
              "Yes, completely free. BillingFixPro's $name is available at no cost with no account required and no usage limits. Run as many calculations as you need."),
            @("How accurate are the calculations?",
              "Our $name uses standard financial formulas and delivers results accurate to two decimal places for currency values. Calculations follow industry-standard methods for billing, tax, and financial estimation."),
            @("Can I use this calculator on my mobile phone?",
              "Yes. The $name is fully responsive and works seamlessly on smartphones, tablets, and desktop computers. Access it from any device with a modern web browser, including while on-site with clients."),
            @("Are my calculation results saved?",
              "Results are displayed in real time but are not stored on our servers. If you need to record your results, copy them, screenshot the page, or note them before navigating away."),
            @("What currencies does this calculator support?",
              "The $name works with any currency. Enter your values in your local currency and the calculations apply standard mathematical operations universally — the tool does not convert currencies but handles any numeric input correctly.")
        )}
        'order' { @(
            @("Is the $name free to use?",
              "Yes, BillingFixPro's $name is completely free. No account registration, no subscription, no hidden fees — generate as many documents as your business requires at no cost."),
            @("Are documents created with this tool legally binding?",
              "Documents generated by our tool contain standard business terms and legally relevant information. Enforceability depends on your local jurisdiction and the specific terms included. For high-value or complex agreements, consider having a legal professional review the document."),
            @("Can I customise the terms and conditions?",
              "Yes. The $name includes editable fields for specifying custom terms, payment schedules, delivery conditions, and other relevant details. You have full control over the content included in every document."),
            @("Can I download the document as a PDF?",
              "Yes. After filling in the form and generating the document, click Download or Print to save it as a PDF. PDFs maintain consistent formatting across all devices and are universally accepted for business correspondence."),
            @("Is my document data stored by BillingFixPro?",
              "No. All data you enter is processed in your browser and never stored on BillingFixPro's servers. Your confidential business, client, and financial information remains completely private.")
        )}
        'notice' { @(
            @("Is the $name free to use?",
              "Yes, completely free. BillingFixPro's $name requires no account, no subscription, and no payment. Generate professional payment notices and reminders at no cost, with no usage limits."),
            @("How should I send the notice to my client?",
              "After generating your notice, download it as a PDF and send it as an email attachment, or copy the text into an email body. For formal notices, printing and posting via certified mail creates an additional paper trail for collections purposes."),
            @("Can I adjust the tone of the notice?",
              "Yes. All text fields in the $name are fully editable, allowing you to customise the language to match your preferred tone — from a polite first reminder to a firm formal notice — and your specific situation."),
            @("How many notices can I generate?",
              "There is no limit. Generate as many payment notices as your accounts receivable require. BillingFixPro's tools are unrestricted and completely free, with no daily caps or account requirements."),
            @("Is my client data stored by BillingFixPro?",
              "No. All information you enter is processed locally in your browser and is never stored on our servers. Client names, invoice amounts, account details, and all other entered information remain completely private.")
        )}
        default { @(
            @("Is the $name free to use?",
              "Yes, BillingFixPro's $name is completely free. No account, no subscription, and no fees — access the full functionality with unlimited usage at no cost."),
            @("Do I need to install any software?",
              "No software installation is required. The $name works entirely in your web browser on any device — desktop, laptop, tablet, or smartphone. Simply visit the page and start using it immediately."),
            @("Can I save or download my output?",
              "Yes. You can download your generated document as a PDF, print it directly from your browser, or copy the content for use in other applications. All output options are free and immediately available."),
            @("Is my data secure when using this tool?",
              "All data you enter is processed locally in your browser and is never transmitted to or stored on BillingFixPro's servers. Your business and financial information stays completely private and secure."),
            @("Can I use this tool for multiple clients or projects?",
              "Yes, use the $name as many times as needed, for as many clients or projects as you have. There are no usage limits, and each session starts fresh with no data carried over from previous uses.")
        )}
    }
    $items = ''
    foreach ($pair in $qa) {
        $items += "`n  <div class=`"faq-item`">`n    <h3>Q: $($pair[0])</h3>`n    <p>A: $($pair[1])</p>`n  </div>"
    }
    return "<div class=`"faq-section`">`n  <h2>Frequently Asked Questions</h2>$items`n</div>"
}

# ── Extra related links per category ─────────────────────────────────────────
$ExtraLinks = @{
    'invoice' = @(
        @('/tools/invoice-generator.html','Invoice Generator'),
        @('/tools/simple-invoice.html','Simple Invoice Generator'),
        @('/tools/receipt-generator.html','Receipt Generator'),
        @('/tools/quote-generator.html','Quote Generator'),
        @('/tools/invoice-calculator.html','Invoice Calculator')
    )
    'receipt' = @(
        @('/tools/receipt-generator.html','Receipt Generator'),
        @('/tools/sales-receipt.html','Sales Receipt Generator'),
        @('/tools/invoice-generator.html','Invoice Generator'),
        @('/tools/payment-receipt.html','Payment Receipt'),
        @('/tools/sales-tax-calculator.html','Sales Tax Calculator')
    )
    'quote' = @(
        @('/tools/quote-generator.html','Quote Generator'),
        @('/tools/estimate-generator.html','Estimate Generator'),
        @('/tools/invoice-generator.html','Invoice Generator'),
        @('/tools/project-cost-calculator.html','Project Cost Calculator'),
        @('/tools/price-quote.html','Price Quote Generator')
    )
    'calc' = @(
        @('/tools/invoice-calculator.html','Invoice Calculator'),
        @('/tools/tax-calculator.html','Tax Calculator'),
        @('/tools/sales-tax-calculator.html','Sales Tax Calculator'),
        @('/tools/vat-calculator.html','VAT Calculator'),
        @('/tools/freelance-rate-calculator.html','Freelance Rate Calculator')
    )
    'order' = @(
        @('/tools/purchase-order.html','Purchase Order Generator'),
        @('/tools/work-order.html','Work Order Generator'),
        @('/tools/service-order.html','Service Order Form'),
        @('/tools/payment-agreement.html','Payment Agreement'),
        @('/tools/invoice-generator.html','Invoice Generator')
    )
    'notice' = @(
        @('/tools/payment-reminder.html','Payment Reminder'),
        @('/tools/collection-letter.html','Collection Letter'),
        @('/tools/overdue-invoice-notice.html','Overdue Invoice Notice'),
        @('/tools/invoice-generator.html','Invoice Generator'),
        @('/tools/payment-terms-generator.html','Payment Terms Generator')
    )
    'admin' = @(
        @('/tools/invoice-generator.html','Invoice Generator'),
        @('/tools/invoice-tracker.html','Invoice Tracker'),
        @('/tools/invoice-checklist.html','Invoice Checklist'),
        @('/tools/payment-history.html','Payment History'),
        @('/tools/statement-of-account.html','Statement of Account')
    )
}

function Get-ExtraSection([string]$slug, [string]$currentFile) {
    $cat = Get-Cat $slug
    $pool = $ExtraLinks[$cat]
    if (-not $pool) { $pool = $ExtraLinks['invoice'] }
    # pick 3 links that differ from current file
    $picked = @()
    foreach ($link in $pool) {
        $href = $link[0]
        $name = $link[1]
        $linkSlug = [System.IO.Path]::GetFileNameWithoutExtension($href)
        if ($linkSlug -ne $slug -and $picked.Count -lt 3) {
            $picked += "<a href=`"$href`" class=`"related-card`"><div class=`"related-card-name`">$name</div><div class=`"related-card-desc`">Free online tool</div></a>"
        }
    }
    $cards = $picked -join "`n"
    return @"
<div class="related-section">
  <h2>More Tools You May Like</h2>
  <div class="related-grid">
$cards
  </div>
</div>
"@
}

# ── Process one file ──────────────────────────────────────────────────────────
function Process-File([System.IO.FileInfo]$file) {
    $slug    = $file.BaseName
    $content = [System.IO.File]::ReadAllText($file.FullName, [System.Text.Encoding]::UTF8)

    if ($content.Contains('class="faq-section"')) {
        Write-Host "  SKIP $slug (already has FAQ)"
        return
    }

    # Extract tool name from h1
    $m = [regex]::Match($content, '<h1[^>]*>([^<]+)</h1>')
    $toolName = if ($m.Success) { $m.Groups[1].Value.Trim() } else { ($slug -replace '-',' ') }

    # 1. Inject FAQ CSS before @media print
    if (-not $content.Contains('faq-section{')) {
        $content = $content.Replace('@media print{', "$FAQCss`n@media print{")
    }

    # 2. Replace seo-section content using indexOf (safe with special chars)
    $seoMarker = '<div class="seo-section">'
    $si = $content.IndexOf($seoMarker)
    if ($si -ge 0) {
        $closeStart = $content.IndexOf('</div>', $si + $seoMarker.Length)
        if ($closeStart -ge 0) {
            $newSeo = Get-Seo $toolName $slug
            $content = $content.Substring(0,$si+$seoMarker.Length) + "`n" + $newSeo + "  " + $content.Substring($closeStart)
        }
    }

    # 3. Insert FAQ before related-section
    $relMarker = '<div class="related-section">'
    $ri = $content.IndexOf($relMarker)
    if ($ri -ge 0) {
        $faqHtml = Get-Faq $toolName $slug
        $content = $content.Substring(0,$ri) + $faqHtml + "`n  " + $content.Substring($ri)
    }

    # 4. Insert extra related section before </main>
    $mainClose = $content.LastIndexOf('</main>')
    if ($mainClose -ge 0) {
        $extra = Get-ExtraSection $slug $slug
        $content = $content.Substring(0,$mainClose) + $extra + "`n" + $content.Substring($mainClose)
    }

    [System.IO.File]::WriteAllText($file.FullName, $content, [System.Text.Encoding]::UTF8)
    Write-Host "  OK  $slug"
}

# ── Main: run one batch ───────────────────────────────────────────────────────
$batchMap = @{
    1 = 0..19
    2 = 20..39
    3 = 40..59
    4 = 60..79
    5 = 80..99
}

if ($Batch -lt 1 -or $Batch -gt 5) {
    Write-Error "Usage: .\seo-batch.ps1 -Batch <1-5>"
    exit 1
}

$indices = $batchMap[$Batch]
$startIdx = $indices[0]; $endIdx = $indices[-1]
Write-Host "`n=== Batch $($Batch): files $($startIdx+1) to $($endIdx+1) of $($allFiles.Count) ==="

for ($i = $startIdx; $i -le [Math]::Min($endIdx, $allFiles.Count-1); $i++) {
    Process-File $allFiles[$i]
}

Write-Host "`nBatch $Batch done. Committing..."
Set-Location "C:\Users\Administrator\billingfixpro"
git add tools/
git commit -m "SEO batch $($Batch) ($($startIdx+1)-$($endIdx+1)): expand seo-section 300w + FAQ 5qa + extra links"
git -c http.proxy=http://127.0.0.1:7897 -c http.sslVerify=false push origin master
Write-Host "Batch $($Batch) pushed OK."
