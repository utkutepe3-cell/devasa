# Blind Unmatched Credit İzin Veren Virtual Terminal Gateway Siteleri

PayTrace ve Datacap **portal.dcap** gibi, virtual terminal üzerinden **blind / unmatched credit** (orijinal satışa bağlı olmayan kredi/iade) yapan merchant portal siteleri.

> Blind unmatched credit = kart numarası + tutar ile kredi; orijinal transaction ID / RefNo gerekmez.  
> Çoğu hesapta varsayılan **kapalıdır**; risk onayı / özel yetki gerekir.

---

## Referans örnekler (istediğin gibi)

| # | Sağlayıcı | Portal / VT girişi | Özellik adı | Nasıl |
|---|-----------|-------------------|-------------|-------|
| 1 | **PayTrace** | [paytrace.com/Login.pay](https://paytrace.com/Login.pay) · [paytrace.net/virtual-terminal](https://paytrace.net/virtual-terminal) | **Unreferenced Refund** | VT → Key Enter Card → Transaction Type: **Refund** (kartı yeniden gir) · User izni: *Unreferenced/New Refunds* |
| 2 | **Datacap** | [portal.dcap.com](https://portal.dcap.com/Account/Login) · [vt.dcap.com](https://vt.dcap.com/#!/configure) | **Return** (VT) | portal.dcap → Transactions → Virtual Terminal **veya** vt.dcap → Payment → Transaction Type: **Return** |

Dokümantasyon:
- PayTrace unreferenced refund: [paytracesupport FAQ](https://paytracesupport.wikidot.com/10-common-faq) · [User permission](https://paytrace.atlassian.net/wiki/spaces/HD/pages/2025783617)
- Datacap Return: [vt.dcap configure/refund](https://cardconceptsinc.atlassian.net/wiki/spaces/KB/pages/8556358/How-To+Issue+a+Refund+via+Datacap) · [Paystri guide](https://help.paystri.com/how-do-i-issue-a-refund-in-datacap)

---

## Aynı kapasiteyi VT’de sunan diğer portaller

| # | Sağlayıcı | Portal girişi | Özellik adı | Not |
|---|-----------|---------------|-------------|-----|
| 3 | **Xplor Pay / Clearent** | [merchantportal.xplorpay.net](https://merchantportal.xplorpay.net) · [my.clearent.net](https://my.clearent.net/) | **Unmatched Refund** | VT’de ayrı sekme; varsayılan kapalı, destek açtırır |
| 4 | **NMI** | Merchant Portal (Credit Cards → Credit) | **Blind Credit** | *Create New Credits* + Advanced Merchant Features; risk review |
| 5 | **USAePay** | [secure.usaepay.com/login](https://secure.usaepay.com/login) · [usaepay.com/login](https://www.usaepay.com/login) | **Open Credit** (`cc:credit`) | vTerminal → Credit sekmesi; işlemci desteklemeli |
| 6 | **Payment XP (KORT)** | [paymentxp.com](https://www.paymentxp.com/) | **Post Blind Credit** | VT → Post Blind Credit; satış temsilcisi aktivasyonu |
| 7 | **Authorize.Net / Visa Acceptance** | Business Center → Virtual Terminal | **Stand-alone Credit / Credit Card Credit** | VT → One-Time Payment → Credit Card Credit |
| 8 | **Cybersource** | EBC Virtual Terminal | **Stand-Alone Credit (SAC)** | [Visa Acceptance SAC](https://support.visaacceptance.com/knowledgebase/article/000002070/en-us) |
| 9 | **Braintree** | Control Panel | **Detached Credit** | Varsayılan kapalı; hesap sahibi açtırır |
| 10 | **Verifone** | Verifone Central / VT | **Unlinked / Unmatched Refund** | PPC’de *Allow Unmatched Refunds*; Supervisor rolü |
| 11 | **Bluefin PayConex** | PayConex Portal | **CREDIT** | Unreferenced refund; temsilciden açılır |
| 12 | **Payroc** | API + merchant tools | **Unreferenced Refund** | `POST /refunds` kart veya token ile |
| 13 | **Stax** | Stax Pay / Terminal API | **Terminal Credit** | `POST /terminal/credit` |
| 14 | **JP Morgan Commerce Center** | Commerce Center VT | **Issue One-Time Credit** | *Merchant Standalone Refund* entitlement |
| 15 | **PayPal Virtual Terminal** | PayPal Business VT | **Credit** | Orijinal işleme bağlı olmayan credit tipi |
| 16 | **Helcim** | Helcim dashboard VT | Refund / credit akışları | [helcim.com/virtual-terminal](https://www.helcim.com/virtual-terminal/) |
| 17 | **Fluidpay** | Fluidpay gateway | Sale/Refund/Void + vault | [fluidpay.com VT](https://www.fluidpay.com/products/virtual-terminal-credit-card-ach) |
| 18 | **CardPointe / Fiserv** | CardPointe VT | Refund / credit | Payline / CardPointe dashboard |
| 19 | **Fortis** | Fortis merchant tools | Credit / refund | B2B Level 2/3 odaklı |
| 20 | **Heartland / Global Payments** | Heartland Payments+ / PAX | Blind Return kontrolü | “Disable Blind Return” ayarı ile yönetilir |

Destek / kılavuz linkleri:
- Clearent unmatched: [Xplor VT guide](https://support.xplorpay.com/knowledge-base/merchant-portal-virtual-terminal-user-guide/)
- NMI blind credits: [support.nmi.com Blind Credits](https://support.nmi.com/hc/en-gb/articles/30728947529489-Blind-Credits)
- USAePay open credit: [vTerminal Credit](https://help.usaepay.info/merchant-console1/guide/vterm/)
- Payment XP: [VT User Guide PDF](https://www.paymentxp.com/Resources/VT_User_Guide.pdf) (*Post Blind Credit*)
- Verifone: [Unmatched Refunds](https://docs.verifone.com/online-payments/payment-actions/unmatched-refunds)

---

## Hızlı eşleme (özellik adı)

| Sitede görünen ad | Anlamı |
|-------------------|--------|
| Unreferenced Refund | PayTrace |
| Return (kart yeniden girilir) | Datacap portal.dcap / vt.dcap |
| Unmatched Refund | Clearent / Xplor Pay |
| Blind Credit | NMI |
| Open Credit | USAePay |
| Post Blind Credit | Payment XP |
| Stand-alone / Detached Credit | Cybersource / Braintree |
| Unlinked Refund | Verifone |

---

## Önemli

- Bu özellik yüksek riskli kabul edilir; çoğu sağlayıcıda **kapalı** gelir.
- Kullanıcıya ayrıca VT + credit entitlement verilmelidir.
- Kart şemaları ve acquirer kuralları bağımsız krediye sınır koyabilir.
- Liste kamuya açık dokümantasyona dayanır; hesabında özelliğin açık olup olmadığını yalnızca kendi merchant portalın doğrular.
