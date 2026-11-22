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
| 14 | **Verifone** | Verifone Central / VT | Unlinked / Unmatched Refund |
| 15 | **Bluefin PayConex** | PayConex Portal | CREDIT (unreferenced) |
| 16 | **Payroc** | Merchant tools / API | Unreferenced Refund |
| 17 | **Stax** | Stax Pay / Terminal API | Terminal Credit |
| 18 | **PayPal Business VT** | PayPal Virtual Terminal | Credit |
| 19 | **Helcim** | Helcim dashboard | Refund / credit |
| 20 | **Fluidpay** | Fluidpay gateway VT | Sale / Refund / Void |
| 21 | **CardPointe / Fiserv** | CardPointe VT | Refund / credit |
| 22 | **Heartland / Global Payments** | Payments+ / PAX | Blind Return toggle |
| 23 | **Visa Acceptance Business Center** | VT → Credit Card Credit | Stand-alone Credit |

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
| Unlinked / Unreferenced Refund | Verifone · Adyen |
| Credit (API) | TabaPay |

---

## Önemli

- Bu özellik yüksek riskli kabul edilir; çoğu sağlayıcıda **kapalı** gelir.
- Kullanıcıya VT + credit entitlement verilmelidir.
- Liste kamuya açık dokümantasyona dayanır; hesabında açık olup olmadığını yalnızca kendi portalın doğrular.
