# Blind Unmatched Credit İzin Veren Virtual Terminal Gateway Siteleri

PayTrace ve Datacap **portal.dcap** gibi, virtual terminal üzerinden **blind / unmatched credit** (orijinal satışa bağlı olmayan kredi/iade) yapan merchant portal siteleri.

> Blind unmatched credit = kart numarası + tutar ile kredi; orijinal transaction ID / RefNo gerekmez.  
> Çoğu hesapta varsayılan **kapalıdır**; risk onayı / özel yetki gerekir.

---

## Unmatched Refund (adı birebir geçenler)

| # | Sağlayıcı | Portal | Özellik | Nasıl |
|---|-----------|--------|---------|-------|
| U1 | **Xplor Pay / Clearent** | [merchantportal.xplorpay.net](https://merchantportal.xplorpay.net) · [my.clearent.net](https://my.clearent.net/) | **Unmatched Refund** | VT → Take a Payment → **Unmatched Refund** sekmesi · destek açtırır · [VT guide](https://support.xplorpay.com/knowledge-base/merchant-portal-virtual-terminal-user-guide/) |
| U2 | **Verifone Central** | Verifone Central (merchant login) | **Unmatched Refund** | PPC → **Allow Unmatched Refunds** · VT’de **Unlinked refund** · [docs](https://docs.verifone.com/online-payments/payment-actions/unmatched-refunds) |

Aynı iş, farklı isim (Unreferenced / Unlinked / Blind):

| Özellik adı | Siteler |
|-------------|---------|
| **Unreferenced Refund** | PayTrace · Planet · Adyen · Yuno · Worldnet · Payroc · Checkout.com · Integrated Commerce |
| **Unreferenced Return** | Nuvei |
| **Unlinked Refund** | Authorize.Net (ECC) · Global Payments / OpenEdge · Verifone |
| **Blind Refund / Blind Credit** | Fortis · NMI |
| **Independent Refund** | Moneris Go |
| **CREDIT (unreferenced)** | Bluefin PayConex |

---

## Referans örnekler (istediğin gibi)

| # | Sağlayıcı | Portal / VT girişi | Özellik adı | Nasıl |
|---|-----------|-------------------|-------------|-------|
| 1 | **PayTrace** | [paytrace.com/Login.pay](https://paytrace.com/Login.pay) · [paytrace.net/virtual-terminal](https://paytrace.net/virtual-terminal) | **Unreferenced Refund** | VT → Key Enter Card → Transaction Type: **Refund** (kartı yeniden gir) · User izni: *Unreferenced/New Refunds* |
| 2 | **Datacap** | [portal.dcap.com](https://portal.dcap.com/Account/Login) · [vt.dcap.com](https://vt.dcap.com/#!/configure) | **Return** (VT) | portal.dcap → Transactions → Virtual Terminal **veya** vt.dcap → Payment → Transaction Type: **Return** |

Dokümantasyon:
- PayTrace: [FAQ](https://paytracesupport.wikidot.com/10-common-faq) · [User permission](https://paytrace.atlassian.net/wiki/spaces/HD/pages/2025783617)
- Datacap: [vt.dcap refund](https://cardconceptsinc.atlassian.net/wiki/spaces/KB/pages/8556358/How-To+Issue+a+Refund+via+Datacap)

---

## Yeni kuruluşlar / modern platformlar (PayTrace · portal.dcap benzeri)

| # | Sağlayıcı | Kuruluş / tip | Portal girişi | Özellik adı | Kanıt |
|---|-----------|---------------|---------------|-------------|-------|
| A | **Apexx Global** | Modern orchestration · Atomic Portal | [portalv2.apexx.global](https://portalv2.apexx.global/) | **Original Credit (OCT)** / standalone credit | VT → Original Credit · [OCT guide](https://support.apexx.global/support/solutions/articles/19000102433-how-do-i-process-original-credit-transactions-unlinked-refunds-) · [VT](https://support.apexx.global/support/solutions/articles/19000166542-product-suite-virtual-terminal) |
| B | **Planet (WeArePlanet)** | Modern gateway portal | [weareplanet.com/login](https://www.weareplanet.com/login) → Planet Portal | **Unreferenced Refund** | VT’de kart/token ile unreferenced refund · [VT docs](https://docs.weareplanet.com/docs/virtual-terminal) |
| C | **Chargezoom Gateway** | Yeni self-host gateway + merchant VT | [chargezoomgateway.com/auth](https://chargezoomgateway.com/auth) | **Unreferenced credit** (`type: credit`) | API + merchant VT · [gateway site](https://chargezoomgateway.com/) · [API docs](https://chargezoomgateway.com/docs) |
| D | **Nuvei** | Control Panel VT (modern REST 2.0) | [cpanel.nuvei.com](https://cpanel.nuvei.com/login) | **Unreferenced Return** | Operations → VT → Transaction Type: Unreferenced Return · [VT docs](https://docs.nuvei.com/documentation/control-panel-docs/operations/virtual-terminal/) |
| E | **Inyo Global** | Yeni orchestration / Visa Direct | Dashboard (onboarding URL) · [inyoglobal.com](https://www.inyoglobal.com/) | **OCT — Card Payouts** | Visa Direct / Mastercard Send push-to-card · [product](https://www.inyoglobal.com/) |
| F | **IXOPAY** | Orchestration + VT | [ixopay.com/login](https://www.ixopay.com/login) · [gateway.ixopay.com](https://gateway.ixopay.com/en/login) | VT transaction types (connector’da credit açılabilir) | [VT MOTO](https://documentation.ixopay.com/manual/docs/virtual-terminal-moto) |
| G | **Adyen** | Customer Area / standalone terminal | Adyen Customer Area | **Unreferenced Refund** | CA’da Allow unreferenced refunds · [docs](https://docs.adyen.com/point-of-sale/basic-tapi-integration/refund-payment/unreferenced) |
| H | **Checkout.com** | Modern acquirer / money movement | Checkout Dashboard | **OCT** (Original Credit Transaction) | Visa Direct OCT / payouts · [terminology](https://www.checkout.com/docs/business-operations/terminology) |

> Bu satırlar özellikle daha yeni / modern platformlar. OCT = Original Credit Transaction (kart’a push; klasik “blind credit”in network karşılığı).

---

## Daha fazla benzer site (ek tur)

| # | Sağlayıcı | Portal girişi | Özellik adı | Kanıt |
|---|-----------|---------------|-------------|-------|
| I | **Shift4** | [dollarsonthenet.net](https://dollarsonthenet.net/login.cfm) (Lighthouse TM) · [myportal.shift4.com](https://myportal.shift4.com/index.cfm?action=user.login) | **Independent Credit** | Stand-alone credit; full PAN gerekir · [API spec](https://epower.shift4.com/pdf/Shift4-Payments-Platform-API-Specifications-v1.10.pdf) |
| J | **Paysafe** | [merchant.paysafe.com/portal](https://merchant.paysafe.com/portal/login) | **STANDALONE_CREDIT** / **ORIGINAL_CREDIT** | Kart payout API · [Paysafe cards](https://developer.paysafe.com/en/api-docs/payments-api/add-payment-methods/cards/about-card-payments/) · VT: Merchant Back Office |
| K | **Integrated Commerce (Omni)** | Omni API / Selfcare (destek açar) | **Unreferenced virtual refund** | `POST /transactions/unreferenced-virtual-refund` · [docs](https://docs.omni.integratedcommerce.io/operation/operation-unreferencedrefundcardnotpresent.md) · [Selfcare](https://docs.gateway.integratedcommerce.io/doku.php%3Fid=merchant:existing_merchant:selfcare_system:unreferenced_refunds_after_online_refund_decline.html) |
| L | **Authorize.Net** | [login.authorize.net](https://login.authorize.net/) / Merchant Interface | **Unlinked Refund (ECC)** | Expanded Credit Capabilities · Payments → Unlinked Refund · [KA-08343](https://support.authorize.net/knowledgebase/Knowledgearticle/?code=KA-08343) |
| M | **JP Morgan Commerce Center** | Commerce Center VT | **Issue One-Time Credit** | Standalone Refund entitlement · [VT guide PDF](https://developer.payments.jpmorgan.com/api/download/en/system/downloads/commerce/migration/Virtual_Terminal-Commerce_Center_User_Guide.pdf?type=stream) |
| N | **Worldpay Element/Express** | Worldpay / Element portal | **Stand-alone payout** (adapter) | IXOPAY Worldpay adapter: stand-alone payouts · [adapter](https://adapters.ixopay.com/en/payment-adapter/worldpay) |
| O | **TabaPay** | TabaPay developer / merchant tools | **Credit** (Unified API) | Sale/Auth/Void/Refund/**Credit** · [terminal docs](https://developers.tabapay.com/docs/terminal-integration) |

---

## Daha fazla benzer site (ek tur 2)

| # | Sağlayıcı | Portal girişi | Özellik adı | Kanıt |
|---|-----------|---------------|-------------|-------|
| P | **Yuno** | [dashboard.y.uno](https://dashboard.y.uno) | **Unreferenced Refund** (standalone credit) | `POST /v1/unreferenced-refunds` · [overview](https://docs.y.uno/docs/direct-integration-use-cases/unreferenced-refunds-overview) · [API](https://docs.y.uno/reference/unreferenced-refunds/create-unreferenced-refund) |
| Q | **Truvora** | [dashboard.truvora.com/auth](https://dashboard.truvora.com/auth) | **Unreferenced credit** (`type: credit`) | Gateway API · [docs](https://dashboard.truvora.com/docs) |
| R | **Qualpay** | [app.qualpay.com/login](https://app.qualpay.com/login) | **Credit** (standalone / unlinked) | VT → New Transaction → **Credit** · ilk 30 gün sonra risk açtırır · [transaction types](https://help.qualpay.com/help/transaction-types) · [API credit](https://developer.qualpay.com/reference/credit) |
| S | **Worldline** | [myportal.worldline-solutions.com](https://myportal.worldline-solutions.com/merchantportal/?login=) | **Standalone refund** / **Originalcredits** | Unreferenced refund API · [standalone refund](https://docs.acquiring.worldline-solutions.com/Features/Card-based/Refunds/standalone-refund) · [OCH originalcredits](https://developer.payments.worldline.com/techguides/api-resources/payment-rest-api-ref-topics/payment-rest-api-ref-origcredits.html) |
| T | **Spreedly** | [app.spreedly.com](https://app.spreedly.com) · [id.spreedly.com/signin](https://id.spreedly.com/signin) | **General credit** | Gateway’e bağlı unreferenced credit · [API](https://developer.spreedly.com/reference/general-credit-transaction) |
| U | **Till Payments** | [gateway.tillpayments.com](https://gateway.tillpayments.com/documentation/apiv3) | **Payout** (`cardData`) | Stand-alone payout; connector’da açılır · [API v3](https://gateway.tillpayments.com/documentation/apiv3) |

---

## Daha fazla benzer hesap (ek tur 3)

| # | Sağlayıcı | Portal girişi | Özellik adı | Kanıt |
|---|-----------|---------------|-------------|-------|
| V | **PayJunction** | [payjunction.com/.../authenticate](https://www.payjunction.com/trinity/virtualterminal/authenticate) | **Refund** (kart + tutar, transactionId yok) | VT → Action: **Refund** + full PAN · [Refund without txn id](https://developer.payjunction.com/hc/en-us/articles/218052417-Refunding-and-Voiding-Transactions) |
| W | **Rapyd** | [dashboard.rapyd.net](https://dashboard.rapyd.net) | **Card payout (OCT)** | Disburse → Payouts → Card · [create payout](https://docs.rapyd.net/en/create-a-payout.html) · [OCT eligibility](https://docs.rapyd.net/en/card-eligibility-for-card-payouts.html) |
| X | **Worldpay iQ (Vantiv)** | [reports.iq.vantivcnp.com](https://reports.iq.vantivcnp.com/ui/login) | **VT Refund** (sistem dışı satış) / **CreditCardCredit** | iQ → Operations → Virtual Terminal → Refund · [VT guide](https://docs.worldpay.com/support/iq-reporting-analytics-user-guide/operations-reports-tools/virtualterminal) · [CreditCardCredit](https://docs.worldpay.com/apis/express/express-xml/methods/credit) |
| Y | **Computop (Nexi Paygate)** | [paygate.computop.de/MerchantPortal](https://paygate.computop.de/MerchantPortal/Account/Login) | **Refund without reference** | Helpdesk açtırır · [REST cards](https://developer.computop.com/display/EN/REST+API+Cards) · [refund external](https://computop-docs.redocly.app/payments/refundexternalpayment) |
| Z | **Finaro (Credorax)** | Finaro/Credorax gateway · [finaro.com](https://www.finaro.com/) | **Credit** (op. 6 / O=35) | Unreferenced credit · [PaymentsOS Finaro](https://developers.paymentsos.com/docs/connect/partner-providers/finaro.html) · ActiveMerchant `credit: '35'` |
| AA | **Wirecard / Fiserv PG** | Wirecard Payment Gateway · [doc.wirecard.com](https://doc.wirecard.com/CC_Main.html) | **original-credit** / **PaymentCardCreditTransaction** | Non-referenced OCT · [Wirecard OCT](https://doc.wirecard.com/CC_Main.html) · [Fiserv OCT](https://docs.fiserv.dev/public/docs/visa-oct-restapi) |

---

## Daha fazla benzer hesap (ek tur 4)

| # | Sağlayıcı | Portal girişi | Özellik adı | Kanıt |
|---|-----------|---------------|-------------|-------|
| AB | **Moneris Go** | [monerisgo.com](https://www.monerisgo.com) | **Independent Refund** | Payment → Credit → Transaction type: **Refund** + PAN; varsayılan kapalı · [Go portal guide PDF](https://www.moneris.com/-/media/Files/Products/Moneris-Go-Portal/MonerisGo_Portal_RefGuide-ENG.pdf) |
| AC | **Global Payments / OpenEdge** | [openedgeview.paygateway.com](https://openedgeview.paygateway.com/Account/Login) · [reporting.globalpay.com](https://reporting.globalpay.com) | **Unlinked Refund** (Standalone Credit) | `POST .../creditreturn` + full card/token · [refund docs](https://developer.globalpayments.com/en-US/partner.globalpayments.com/integrated-partner/payments/manage-payments/refund) |
| AD | **Bluefin PayConex** | [secure.payconex.net](https://secure.payconex.net/) | **CREDIT** (unreferenced) | Keyed → Transaction Type: **CREDIT**; risk açtırır · [processing](https://developers.bluefin.com/payconex/v4/docs/processing-transactions-1) |
| AE | **Checkbook** | [app.checkbook.io](https://app.checkbook.io) | **Push to Card (OCT)** | Send Payment → Debit Card · [push-to-card](https://checkbook.io/product/payments/push-to-card/) · [how-to](https://support.checkbook.io/hc/en-us/articles/11286487140123-How-to-send-funds-to-a-Debit-Card) |
| AF | **Paywint** | [merchant.paywint.com](https://merchant.paywint.com/) | **Push to Card (OCT)** | Visa Direct / Mastercard Send · [product](https://paywint.com/push-to-card/) |
| AG | **Verifone Central** | Verifone Central (merchant login) | **Unmatched / Unlinked Refund** | PPC’de Allow Unmatched Refunds · VT’de Unlinked refund · [docs](https://docs.verifone.com/online-payments/payment-actions/unmatched-refunds) |

---

## Daha fazla benzer hesap (ek tur 5)

| # | Sağlayıcı | Portal girişi | Özellik adı | Kanıt |
|---|-----------|---------------|-------------|-------|
| AH | **Elavon CenPOS** | [cenpos.net/vt](https://www.cenpos.net/vt/) · [www3.cenpos.net](https://www3.cenpos.net/ebpphtml5) | **Credit** (önceki satışa bağlı değil) | VT Credit privilege · herhangi kart/tutar · [Cashiering Credit](https://developer.elavon.com/products/cenpos/v1/cashiering-api-reference) |
| AI | **Worldnet Payments** | [payments.worldnettps.com/.../selfcare](https://payments.worldnettps.com/merchant/selfcare/) | **Unreferenced Refund** | Kart detayı veya token ile; banka onayı · [XML Unreferenced Refund](https://testdocs.worldnettps.com/doku.php?id=developer%3Aapi_specification%3Axml_payment_features) · [SelfCare](https://merchants.worldnetpayments.com/selfcare/introduction) |
| AJ | **RadiumOne** | API / support (dashboard yok) · [docs.radiumone.io](https://docs.radiumone.io/payments-api/standalone-refunds) | **Standalone / open refund** | `transaction-refund-unreferenced` scope · [standalone refunds](https://docs.radiumone.io/payments-api/standalone-refunds) |
| AK | **Nium** | [app.nium.com](https://app.nium.com) | **Visa Direct card payout** | Portal + card widget · [Nium Portal](https://docs.nium.com/docs/nium-portal) · [Visa card payouts](https://mpdocs.nium.com/payout-payin/visa-card-payouts) |
| AL | **Dwolla** | [accounts.dwolla.com/login](https://accounts.dwolla.com/login) | **Push to Card** | Settlement account + Checkout.com · [Push to Card docs](https://developers.dwolla.com/docs/push-to-card) |
| AM | **Checkout.com** (ek) | Checkout Dashboard | **Unreferenced Refund** | US kart · `payment_type=UnreferencedRefund` · [docs](https://www.checkout.com/docs/payments/manage-payments/refund-a-payment/refund-a-payment-without-a-reference) |

---

## Daha fazla benzer hesap (ek tur 6 — son tur)

| # | Sağlayıcı | Portal girişi | Özellik adı | Kanıt |
|---|-----------|---------------|-------------|-------|
| AN | **CardPointe (Fiserv)** | [cardpointe.com/account/login](https://cardpointe.com/account/login) | **Force Credit** | VT → Force Credit + full PAN; hesapta açılır · [CardPointe VT](https://support.cardpointe.com/cardpointe/cardpointe-desktop-app/) |
| AO | **Payroc** | [payments.payroc.com/.../selfcare](https://payments.payroc.com/merchant/selfcare/) | **Unreferenced Refund** | `POST /v1/refunds` (paymentId yok) · [docs](https://docs.payroc.com/guides/payments/refunds/unreferenced-refund-card) |
| AP | **Stax** | [app.staxpayments.com](https://app.staxpayments.com) · [webapp.staxpayments.com](https://webapp.staxpayments.com/Login) | **Credit** (general / standalone) | Terminal API Credit · gateway desteklerse · [Credit API](https://docs.staxpayments.com/reference/credit) |
| AQ | **Marqeta** | [app.marqeta.com](https://app.marqeta.com) | **Push-to-Card** (OCT) | `POST /pushtocards/disburse` · [docs](https://www.marqeta.com/docs/core-api/push-to-card-payments-hidden/create-disbursement) |
| AR | **Modern Treasury** | [app.moderntreasury.com](https://app.moderntreasury.com) | **Push to Card** | Visa Direct / Mastercard Send · [product](https://www.moderntreasury.com/payments/rails/push-to-card) |

> Kamuya açık VT/OCT dokümanında yeni benzersiz isimler artık çok seyrek. Büyük oyuncuların çoğu listede.

---

## Klasik / bilinen benzer siteler (PayTrace / portal.dcap gibi)

| # | Sağlayıcı | Portal girişi | Özellik adı | Kanıt |
|---|-----------|---------------|-------------|-------|
| 3 | **Fortis** | [portal.fortis.tech](https://portal.fortis.tech/) | **Blind Refund** | VT → Refund + kart girişi; varsayılan kapalı · [KB](https://kb.fortis.support/Process-a-Refund-Using-the-Virtual-Terminal---Blind-Refunds) |
| 4 | **Clover / Fiserv IPG** | [ipg-online.com/virtual-terminal](https://www.ipg-online.com/virtual-terminal/) | **Credit (Naked Refund)** | VT menü → Credit; hesapta açık olmalı · [VT 2.0 guide](https://uk.clover.com/content/dam/firstdata/clover-uk/en/assets/api-docs/Clover_VT_2.0_Guide.pdf) · [Fiserv Credit](https://docs.fiserv.dev/public/docs/credit-naked-refund) |
| 5 | **PayPal Payflow Manager** | [manager.paypal.com](https://manager.paypal.com/) | **Non-referenced Credit** | VT → Single Transaction → Credit + kart no · *Allow non-referenced credits = Yes* · [PayPal help](https://www.paypal.com/us/cshelp/article/how-do-i-issue-a-credit-or-refund-to-a-customer-with-payflow-ts1226) |
| 6 | **Elavon Converge** | [myvirtualmerchant.com](https://www.myvirtualmerchant.com/VirtualMerchant/login.do) · [convergepay.com](https://www.convergepay.com/converge-webapp/#!/login) | **cccredit** (kart ile credit) | Full card / track ile refund; matched `ccreturn` de var · [cccredit note](https://developer-uat.elavon.com/products/converge/v1/ccreturn) |
| 7 | **Sola (eski Cardknox)** | [portal.solapayments.com](https://portal.solapayments.com/) | **cc:credit** (unlinked credit) | API/gateway: satışa bağlı olmayan credit · [Credit docs](https://cardknox.gitbook.io/sola-dev-docs/transaction-api/credit-card/credit) |
| 8 | **Xplor Pay / Clearent** | [merchantportal.xplorpay.net](https://merchantportal.xplorpay.net) · [my.clearent.net](https://my.clearent.net/) | **Unmatched Refund** | VT’de ayrı sekme; destek açtırır · [VT guide](https://support.xplorpay.com/knowledge-base/merchant-portal-virtual-terminal-user-guide/) |
| 9 | **NMI** | Merchant Portal → Credit Cards → Credit | **Blind Credit** | Advanced Merchant Features + risk review · [Blind Credits](https://support.nmi.com/hc/en-gb/articles/30728947529489-Blind-Credits) |
| 10 | **USAePay** | [secure.usaepay.com/login](https://secure.usaepay.com/login) | **Open Credit** | vTerminal → Credit · [vTerminal](https://help.usaepay.info/merchant-console1/guide/vterm/) |
| 11 | **Payment XP (KORT)** | [paymentxp.com](https://www.paymentxp.com/) | **Post Blind Credit** | VT → Post Blind Credit · [PDF](https://www.paymentxp.com/Resources/VT_User_Guide.pdf) |

---

## Diğer bilinen benzer portaller

| # | Sağlayıcı | Portal / araç | Özellik adı |
|---|-----------|---------------|-------------|
| 12 | **Cybersource** | EBC Virtual Terminal | Stand-Alone Credit (SAC) |
| 13 | **Braintree** | Control Panel | Detached Credit |
| 14 | **PayPal Business VT** | PayPal Virtual Terminal | Credit |
| 15 | **Helcim** | Helcim dashboard | Refund / credit |
| 16 | **Fluidpay** | Fluidpay gateway VT | Sale / Refund / Void |
| 17 | **Heartland Payments+** | Payments+ / PAX | Blind Return toggle |
| 18 | **Visa Acceptance Business Center** | VT → Credit Card Credit | Stand-alone Credit |
| 19 | **Ingo Money** | ingomoney.com (enterprise) | Push-to-card / OCT disbursements |

---

## Hızlı eşleme (özellik adı ↔ site)

| Sitede görünen ad | Sağlayıcı |
|------------------|-----------|
| Unreferenced Refund | PayTrace · Planet |
| Return (kart yeniden girilir) | Datacap portal.dcap / vt.dcap |
| Original Credit (OCT) | Apexx · Inyo · Checkout.com · Paysafe |
| Independent Credit | Shift4 |
| STANDALONE_CREDIT | Paysafe |
| Unreferenced virtual refund | Integrated Commerce |
| Unlinked Refund (ECC) | Authorize.Net |
| Issue One-Time Credit | JP Morgan |
| Unreferenced Return | Nuvei |
| Unreferenced credit (`type: credit`) | Chargezoom Gateway |
| Blind Refund | Fortis |
| Naked Refund / Credit | Clover · Fiserv IPG |
| Non-referenced Credit | PayPal Payflow Manager |
| cccredit | Elavon Converge |
| cc:credit | Sola / Cardknox |
| Unmatched Refund | Clearent / Xplor Pay |
| Blind Credit | NMI |
| Open Credit | USAePay |
| Post Blind Credit | Payment XP |
| Stand-alone / Detached Credit | Cybersource · Braintree · Visa Acceptance |
| Unlinked / Unreferenced Refund | Verifone · Adyen · Yuno |
| Credit (API) | TabaPay · Truvora |
| Credit (VT standalone) | Qualpay |
| Standalone refund / Originalcredits | Worldline |
| General credit | Spreedly |
| Payout (cardData) | Till Payments |
| Refund (no transactionId) | PayJunction |
| Card payout (OCT) | Rapyd |
| VT Refund / CreditCardCredit | Worldpay iQ |
| Refund without reference | Computop |
| Credit (op. 6 / O=35) | Finaro / Credorax |
| original-credit / PaymentCardCredit | Wirecard · Fiserv PG |
| Independent Refund | Moneris Go |
| Unlinked Refund (Standalone Credit) | Global Payments / OpenEdge |
| CREDIT (unreferenced) | Bluefin PayConex |
| Push to Card (OCT) | Checkbook · Paywint |
| Unmatched / Unlinked Refund | Verifone Central |
| Credit (unassociated) | Elavon CenPOS |
| Unreferenced Refund (SelfCare) | Worldnet Payments |
| Standalone / open refund | RadiumOne |
| Visa Direct card payout | Nium |
| Push to Card | Dwolla · Checkbook · Paywint |
| Unreferenced Refund (US) | Checkout.com |
| Force Credit | CardPointe |
| Unreferenced Refund (API) | Payroc |
| Credit (general / standalone) | Stax |
| Push-to-Card (OCT) | Marqeta · Modern Treasury · Dwolla · Checkbook · Paywint |

---

## Önemli

- Bu özellik yüksek riskli kabul edilir; çoğu sağlayıcıda **kapalı** gelir.
- Kullanıcıya VT + credit entitlement verilmelidir.
- Liste kamuya açık dokümantasyona dayanır; hesabında açık olup olmadığını yalnızca kendi portalın doğrular.
