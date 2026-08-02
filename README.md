# devasa

## Unmatched Refund (Eşleşmemiş İade) Destekleyen ABD Virtual Terminal Gateway Siteleri

Unmatched refund (eşleşmemiş/bağlantısız/blind iade), orijinal bir satış işlemine referans verilmeden yapılan kredi/iade işlemidir. Aşağıda bu özelliği virtual terminal üzerinden destekleyen **ABD merkezli** ödeme gateway sağlayıcıları listelenmiştir.

---

### 1. Xplor Pay (Clearent) — ABD, Georgia
- **Merchant Portal:** [my.clearent.net](https://my.clearent.net/) veya [merchantportal.xplorpay.net](https://merchantportal.xplorpay.net)
- **Virtual Terminal Kılavuzu:** [support.xplorpay.com/knowledge-base/merchant-portal-virtual-terminal-user-guide](https://support.xplorpay.com/knowledge-base/merchant-portal-virtual-terminal-user-guide/)
- **Dökümantasyon:** [docs.xplorpay.com - Managing Virtual Terminal](https://docs.xplorpay.com/merchant-portal/merchant-portal/core-features/managing-virtual-terminal)
- Virtual Terminal'da doğrudan **"Unmatched Refund"** sekmesi mevcut (Sale, Authorization, Force Sale, Unmatched Refund)
- Varsayılan olarak kapalıdır, destek ekibinden açtırılması gerekir

### 2. NMI (Network Merchants Inc.) — ABD, Illinois
- **Blind Credits Dökümantasyonu:** [support.nmi.com - Blind Credits](https://support.nmi.com/hc/en-gb/articles/30728947529489-Blind-Credits)
- **Virtual Terminal Kılavuzu:** [support.nmi.com - Credit Card Processing Virtual Terminal Guide](https://support.nmi.com/hc/en-gb/articles/15547776185233-Credit-Card-Processing-Virtual-Terminal-Guide)
- **Standalone Refund vs Linked:** [support.nmi.com - Linked Refund vs Standalone Refund](https://support.nmi.com/hc/en-gb/articles/115001710191-Linked-Refund-vs-Standalone-Refund)
- Virtual Terminal'da "Credit" sekmesinden blind credit (unmatched refund) yapılabilir
- Kullanıcıya "Virtual Terminal Access" + "Create New Credits" izni gerekir
- Risk incelemesinden geçilmesi zorunludur

### 3. USAePay — ABD, California
- **Virtual Terminal:** [help.usaepay.info/merchant-console1/guide/vterm](https://help.usaepay.info/merchant-console1/guide/vterm/)
- **Transaction API:** [docs.usaepay.com/developer/transaction-api](https://docs.usaepay.com/developer/transaction-api/)
- **REST API Refund:** [help.usaepay.info/developer/rest-api/transactions/processing/refund](https://help.usaepay.info/developer/rest-api/transactions/processing/refund/)
- Virtual Terminal'da "Credit" sekmesinden Open Credit (unmatched refund) yapılabilir
- API'de `cc:credit` komutu ile desteklenir
- İşlemcinin open credit desteklemesi gerekir

### 4. Braintree (PayPal) — ABD, Illinois
- **Detached Credits Dökümantasyonu:** [developer.paypal.com/braintree - Refunds, Voids & Credits](https://developer.paypal.com/braintree/articles/control-panel/transactions/refunds-voids-credits)
- **API Referans:** [developer.paypal.com/braintree/docs/reference/request/transaction/refund](https://developer.paypal.com/braintree/docs/reference/request/transaction/refund/php/)
- "Detached credit" (blind credit) özelliği ile vault kaydına veya yeni ödeme yöntemine kredi verilebilir
- Varsayılan olarak kapalıdır, hesap sahibi Braintree'ye başvurarak geçici olarak açtırmalıdır
- ABD ve AB'deki Braintree Direct merchants için kullanılabilir

### 5. PayPal Virtual Terminal — ABD, California
- **Virtual Terminal:** [paypal.com/us/business/accept-payments/virtual-terminal](https://www.paypal.com/us/business/accept-payments/virtual-terminal)
- **Refund Kılavuzu:** [paypal.com/us/cshelp/article/how-do-i-process-a-refund-in-virtual-terminal-ts2234](https://www.paypal.com/us/cshelp/article/how-do-i-process-a-refund-in-virtual-terminal-ts2234)
- **Kullanım Kılavuzu (PDF):** [paypalobjects.com - Virtual Terminal Guide](https://www.paypalobjects.com/webstatic/en_US/developer/docs/pdf/virtualterminal_guide_us.pdf)
- İşlem tipinde "Credit" seçeneği ile orijinal işleme bağlı olmayan kredi gönderilebilir
- Visa, Mastercard, Amex, Discover destekler
- Business hesap gerektirir, ek donanım gerekmez

### 6. JP Morgan Payments (Commerce Center) — ABD, New York
- **Virtual Terminal Kılavuzu (PDF):** [developer.payments.jpmorgan.com - Virtual Terminal User Guide](https://developer.payments.jpmorgan.com/api/download/en/system/downloads/commerce/migration/Virtual_Terminal-Commerce_Center_User_Guide.pdf)
- "Issue One-Time Credit" özelliği ile standalone refund destekler
- "Merchant Standalone Refund" entitlement'ı kullanıcıya atanmalıdır
- Varsayılan olarak kapalıdır, standalone refund limiti ayarlanmalıdır

### 7. Authorize.Net (Visa) — ABD, California
- **Virtual Terminal:** [authorize.net](https://www.authorize.net/)
- **Dökümantasyon:** [developer.authorize.net](https://developer.authorize.net/)
- Gateway ile ACH ve kredi kartı üzerinden ödeme ve iade destekler
- Unlinked credit özelliği ile önceki işleme referans vermeden kredi verilebilir
- Raporlama ve işlem geçmişi tamamen senkronize çalışır

### 8. Stripe — ABD, California
- **Virtual Terminal (Dashboard):** [dashboard.stripe.com](https://dashboard.stripe.com/)
- **Dökümantasyon:** [stripe.com/docs](https://stripe.com/docs)
- **API Refund:** [stripe.com/docs/refunds](https://stripe.com/docs/refunds)
- API-first yaklaşımla MOTO ödemeler ve refund destekler
- Dashboard üzerinden manuel ödeme ve iade işlemleri yapılabilir
- Custom workflow entegrasyonu için uygundur

### 9. Stax Payments (formerly Fattmerchant) — ABD, Florida
- **Refund Dökümantasyonu:** [docs.staxpayments.com/reference/refund-transaction](https://docs.staxpayments.com/reference/refund-transaction)
- **Terminal Credit:** [docs.staxpayments.com/reference/terminals](https://docs.staxpayments.com/reference/terminals)
- **Void/Refund Kılavuzu:** [docs.staxpayments.com/docs/voiding-and-refunding](https://docs.staxpayments.com/docs/voiding-and-refunding)
- `POST /terminal/credit` endpoint'i ile bağımsız kredi işlemi (unmatched refund)
- Stax Pay portalından ve terminal API'den refund yapılabilir
- Credit, Debit, Check, Gift, Loyalty ödeme tipleri desteklenir

### 10. Bluefin (PayConex) — ABD, Georgia
- **CREDIT İşlem Dökümantasyonu:** [developers.bluefin.com/payconex - Processing Transactions](https://developers.bluefin.com/payconex/v4/docs/processing-transactions-1)
- Virtual Terminal'da "CREDIT" işlem tipi ile unreferenced refund yapılabilir
- Varsayılan olarak kapalıdır, Bluefin temsilcisinden açtırılması gerekir
- PayConex Portal ve entegre POS üzerinden desteklenir

### 11. Payroc — ABD, Illinois
- **Unreferenced Refund API:** [docs.payroc.com/api/schema/card-payments/refunds/create-unreferenced-refund](https://docs.payroc.com/api/schema/card-payments/refunds/create-unreferenced-refund)
- `POST /refunds` endpoint'i ile unreferenced refund oluşturulabilir
- Kart bilgileri veya secure token ile işlem yapılabilir
- Yalnızca belirli hesaplarda kullanılabilir

### 12. Helcim — ABD/Kanada
- **Virtual Terminal:** [helcim.com/virtual-terminal](https://www.helcim.com/virtual-terminal/)
- **Refund Kılavuzu:** [learn.helcim.com/docs/processing-a-refund-or-a-void](https://learn.helcim.com/docs/processing-a-refund-or-a-void)
- Web dashboard ve POS uygulamasından refund destekler
- Aylık ücret yok, sözleşme yok
- Purchase, Refund, Pre-authorization işlem tipleri mevcut

### 13. IXOPAY — ABD
- **Developer Hub:** [documentation.ixopay.com](https://documentation.ixopay.com/releases/v26.11)
- Transaction API'de unlinked refund verisi desteği
- Unreferenced refund (payout) işlemlerini refund olarak settle edebilme
- Virtual Terminal üzerinden MOTO işlem desteği

### 14. Verifone — ABD, Florida
- **Virtual Terminal:** [docs.verifone.com/online-payments/virtual-terminal](https://docs.verifone.com/online-payments/virtual-terminal)
- **Unmatched Refunds:** [docs.verifone.com/online-payments/payment-actions/unmatched-refunds](https://docs.verifone.com/online-payments/payment-actions/unmatched-refunds)
- Virtual Terminal'da "Unlinked refund" checkbox'ı ile eşleşmemiş iade
- eCommerce API üzerinden Encrypted Card veya Reuse Token ile desteklenir
- Merchant Supervisor rolü gerektirir

### 15. Adyen — ABD (merkez Hollanda, ABD operasyonları mevcut)
- **Standalone Terminal:** [docs.adyen.com/point-of-sale/standalone/standalone-use](https://docs.adyen.com/point-of-sale/standalone/standalone-use)
- **Refund Detayları:** [docs.adyen.com/point-of-sale/basic-tapi-integration/refund-payment](https://docs.adyen.com/point-of-sale/basic-tapi-integration/refund-payment)
- Terminal API'de `PaymentType: Refund` ile unreferenced refund
- Referenced ve unreferenced refund arasında seçim yapılabilir
- MOTO refund seçeneği mevcut

---

---

## Daha Az Bilinen ABD Merkezli Sağlayıcılar

### 16. Cybersource (Visa) — ABD, California
- **Stand-Alone Credit (SAC) Kılavuzu:** [support.visaacceptance.com - How to Issue a Refund or Credit](https://support.visaacceptance.com/knowledgebase/article/000002070/en-us)
- **SAC İzin Başvurusu:** [support.visaacceptance.com - SAC Permission](https://support.visaacceptance.com/knowledgebase/knowledgearticle/?code=KA-04253)
- **REST API Örneği:** [developer.cybersource.com - Stand-Alone Credit](https://developer.cybersource.com/docs/cybs/en-us/payments/developer/citimb/rest/payments/payments-processing-basic-intro/payments-processing-basic-credit-intro/payments-processing-basic-credit-ex-rest.html)
- EBC (Enterprise Business Center) Virtual Terminal'dan Stand-Alone Credit yapılabilir
- 365 günden eski işlemler için zorunludur (linked refund süresi dolduğunda)
- API üzerinden SAC için hesap düzeyinde izin gerekmez, VT için gerekir
- PAN ve son kullanma tarihi ile tam kart bilgisi gerektirir (token desteklenmez)

### 17. Payment XP (Meritus) — ABD
- **Virtual Terminal Kılavuzu (PDF):** [paymentxp.com/Resources/VT_User_Guide.pdf](https://www.paymentxp.com/Resources/VT_User_Guide.pdf)
- "Post Blind Credit" özelliği ile işleme bağlı olmayan kredi verilebilir
- Virtual Terminal → Post Blind Credit menüsünden erişilir
- Kredi kartı, ACH Checking ve ACH Savings hesaplarına blind credit destekler
- Aktivasyon için satış temsilcisine başvuru gerekir

### 18. Selective Pay — ABD
- **Virtual Terminal:** [selectivepay.com/services/virtual-terminal](https://selectivepay.com/services/virtual-terminal/)
- Blind/void/refund kontrolleri ve kullanıcı bazlı izin yönetimi
- Dual pricing, Cash Discounting ve credit-only surcharging desteği
- IP allowlist, audit log ve kullanıcı rol yönetimi
- White-label Selective Pay Gateway altyapısı kullanır

### 19. PayJunction — ABD, California
- **API - Refund Without Transaction ID:** [developer.payjunction.com - Refunding and Voiding](https://developer.payjunction.com/hc/en-us/articles/218052417-Refunding-and-Voiding-Transactions)
- **Void/Refund Kılavuzu:** [blog.payjunction.com/void-refund-transactions](https://blog.payjunction.com/void-refund-transactions)
- Transaction ID olmadan tam kart numarasıyla refund yapılabilir (standalone credit)
- Smart Terminal ve API üzerinden `action=REFUND` ile desteklenir
- Müşteri kartı otomatik vault'ta saklanır, tekrar kart bilgisi gerekmez

### 20. Payline Data (CardPointe) — ABD
- **CardPointe Virtual Terminal:** [paylinedata.com/virtual-terminal-online-dashboard](https://paylinedata.com/virtual-terminal-online-dashboard)
- Refund, void, authorization ve settlement işlemleri tarayıcıdan yapılabilir
- Tokenization + P2PE şifreleme ile PCI uyumlu
- Gateway hesabıyla birlikte ücretsiz gelir
- Çoklu kullanıcı ve eşzamanlı erişim desteği

### 21. Fluid Pay — ABD
- **Virtual Terminal:** [fluidpay.com/products/virtual-terminal-credit-card-ach](https://www.fluidpay.com/products/virtual-terminal-credit-card-ach)
- **Gateway API:** [sandbox.fluidpay.com/docs](https://sandbox.fluidpay.com/docs/index.html)
- Kredi kartı ve ACH aynı formda, tek ekrandan işlem
- Customer Vault ile tokenization ve kart saklama
- Sale, Auth, Capture, Refund, Void ve Search API endpoint'leri

### 22. PayTrace — ABD, Washington
- **Virtual Terminal:** [paytrace.net/virtual-terminal](https://paytrace.net/virtual-terminal)
- **JSON REST API:** [developers.paytrace.com](https://developers.paytrace.com/)
- OAuth 2.0 ile kimlik doğrulama
- REFUND işlem tipi ile standalone credit destekler
- PCI-certified Customer Vault ile kart bilgisi saklama
- Amex, Visa, Mastercard, Discover, Diner's Club, JCB destekler

### 23. Nexio — ABD, Utah
- **Refund API:** [docs.nexiopay.com/reference/refundtransaction](https://docs.nexiopay.com/reference/refundtransaction)
- Nexio Payment ID ile tam veya kısmi refund
- Kredi kartı, banka kartı ve eCheck işlemleri destekler
- Mock gateway ile test ortamında anında settlement

### 24. Payarc — ABD, New York
- **Merchant Dashboard:** [support.payarc.com - Merchant Dashboard User Guide](https://support.payarc.com/hc/en-us/articles/34351931484055--Merchant-Dashboard-User-Guide)
- **Gateway Çözümleri:** [support.payarc.com - Payment Solutions](https://support.payarc.com/hc/en-us/articles/34497539604247-Payarc-Payment-Solutions)
- Virtual Terminal'dan refund ve ACH debit/credit işlemleri
- Level 1-3 kart işlemleri destekler
- API token üretimi ile üçüncü parti entegrasyon

### 25. Fortis — ABD, Georgia
- **Virtual Terminal:** [fortispay.com/ecommerce-retail](https://fortispay.com/ecommerce-retail/)
- **Ana Sayfa:** [fortispay.com](https://fortispay.com/)
- ERP yazılımlarına gömülü ödeme entegrasyonu
- Level 2/3 işlem desteği ile B2B ödemelere uygun
- Developer-first API, SDK ve API konsolu

### 26. TabaPay — ABD, California
- **Terminal Entegrasyonu:** [developers.tabapay.com/docs/terminal-integration](https://developers.tabapay.com/docs/terminal-integration)
- Unified API ile Sale, Auth, Capture, Void, Refund ve **Credit** işlemleri
- MagTek ve Ingenico terminal desteği
- EMV chip, magnetic stripe ve NFC/contactless ödemeler

### 27. Heartland Payment Systems (Global Payments) — ABD
- **Virtual Terminal:** [heartland.us/products/payments-plus/payments](https://www.heartland.us/products/payments-plus/payments)
- **Payments+:** [contact.heartland.us/payment-software](https://contact.heartland.us/payment-software/)
- Herhangi bir cihazı virtual terminal'a dönüştürebilir
- PAX terminallerinde "Disable Blind Return" ayarı ile blind refund kontrolü
- Kredi kartı, banka kartı, hediye kartı, mobil cüzdan, QR, ACH destekler

---

### Önemli Notlar

- **Güvenlik:** Unmatched/blind refund yüksek dolandırıcılık riski taşır. Çoğu sağlayıcıda varsayılan olarak **kapalıdır**.
- **Yetkilendirme:** Genellikle Merchant Supervisor veya üst düzey yetki / entitlement gerektirir.
- **Aktivasyon:** Çoğu sağlayıcıda bu özelliğin açılması için destek ekibiyle iletişime geçilmesi ve risk incelemesinden geçilmesi gerekir.
- **Limit:** Günlük ve işlem başına iade tutarı limitleri uygulanır.
- **Kart kuralları:** Visa ve Mastercard gibi kart şemaları, genellikle satış olmadan kredi verilmesini kural dışı kabul eder; yalnızca meşru durumlarda (eski işlemci geçişi, kapatılan hesap vb.) izin verilir.
