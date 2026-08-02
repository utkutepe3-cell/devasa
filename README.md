# devasa

## Unmatched Refund (Eşleşmemiş İade) Destekleyen Virtual Terminal Gateway Siteleri

Unmatched refund (eşleşmemiş/bağlantısız iade), orijinal bir satış işlemine referans verilmeden yapılan kredi/iade işlemidir. Aşağıda bu özelliği virtual terminal üzerinden destekleyen ödeme gateway sağlayıcıları listelenmiştir.

---

### Uluslararası Sağlayıcılar

#### 1. Verifone
- **Virtual Terminal:** [docs.verifone.com/online-payments/virtual-terminal](https://docs.verifone.com/online-payments/virtual-terminal)
- **Unmatched Refunds Dökümantasyonu:** [docs.verifone.com/online-payments/payment-actions/unmatched-refunds](https://docs.verifone.com/online-payments/payment-actions/unmatched-refunds)
- Virtual Terminal'da "Unlinked refund" checkbox'ını işaretleyerek eşleşmemiş iade yapılabilir
- eCommerce API üzerinden de Encrypted Card veya Reuse Token ile desteklenir
- Merchant Supervisor rolü gerektirir

#### 2. Adyen
- **Dökümantasyon:** [docs.adyen.com/point-of-sale/standalone/standalone-use](https://docs.adyen.com/point-of-sale/standalone/standalone-use)
- **Refund Detayları:** [docs.adyen.com/point-of-sale/basic-tapi-integration/refund-payment](https://docs.adyen.com/point-of-sale/basic-tapi-integration/refund-payment)
- Standalone terminal ve Terminal API üzerinden unreferenced refund destekler
- Referenced ve unreferenced refund arasında seçim yapılabilir
- MOTO refund seçeneği de mevcut

#### 3. Xplor Pay (Clearent)
- **Merchant Portal:** [my.clearent.net](https://my.clearent.net/) veya [merchantportal.xplorpay.net](https://merchantportal.xplorpay.net)
- **Virtual Terminal Kılavuzu:** [support.xplorpay.com/knowledge-base/merchant-portal-virtual-terminal-user-guide](https://support.xplorpay.com/knowledge-base/merchant-portal-virtual-terminal-user-guide/)
- Virtual Terminal'da Sale, Authorization, Force Sale ve **Unmatched Refund** sekmeleri mevcut
- Dolandırıcılık riski nedeniyle varsayılan olarak kapalıdır, destek ekibinden açtırılması gerekir

#### 4. MultiSafepay
- **Unreferenced Refunds Dökümantasyonu:** [docs.multisafepay.com/docs/unreferenced-refunds](https://docs.multisafepay.com/docs/unreferenced-refunds)
- SmartPOS ve CTAP terminallerde unreferenced refund desteği
- Cloud POS modunda da kullanılabilir
- Aktivasyon için support@multisafepay.com adresine e-posta gerekir

#### 5. Nuvei (eski Safecharge)
- **Unreferenced Refund Dökümantasyonu:** [helpdesk.nuvei.com - Unreferenced Refunds](https://helpdesk.nuvei.com/doku.php?id=merchant:existing_merchant:selfcare_system:unreferenced_refunds_after_online_refund_decline)
- Online refund reddedildiğinde otomatik unreferenced refund seçeneği sunar
- Virtual Terminal, Open Batch ve Closed Batch üzerinden yapılabilir
- Farklı kart numarası kullanılması gerekir

#### 6. Integrated Commerce (Omni)
- **API Dökümantasyonu:** [docs.omni.integratedcommerce.io - Unreferenced Refund](https://docs.omni.integratedcommerce.io/operation/operation-unreferencedrefundcardpresent)
- **Gateway Dökümantasyonu:** [docs.gateway.integratedcommerce.io](https://docs.gateway.integratedcommerce.io/doku.php?id=merchant:existing_merchant:selfcare_system:unreferenced_refunds_after_online_refund_decline.html)
- Fiziksel terminal ve virtual terminal üzerinden unreferenced refund destekler
- Aktivasyon için support@integratedcommerce.io adresine başvuru gerekir

#### 7. Authorize.Net
- **Virtual Terminal:** [authorize.net](https://www.authorize.net/)
- Gateway versatility ile ACH ve kredi kartı destekler
- Standalone refund (One-Time Credit) işlemi mevcut

#### 8. JP Morgan Payments (Commerce Center)
- **Virtual Terminal Kılavuzu:** [developer.payments.jpmorgan.com](https://developer.payments.jpmorgan.com/api/download/en/system/downloads/commerce/migration/Virtual_Terminal-Commerce_Center_User_Guide.pdf)
- "Issue One-Time Credit" özelliği ile standalone refund destekler
- Özel yetkilendirme (entitlement) gerektirir

#### 9. Stripe
- **Dökümantasyon:** [stripe.com/docs](https://stripe.com/docs)
- API-first yaklaşımla MOTO ödemeler ve refund destekler
- Custom workflow entegrasyonu için uygundur

---

### Türkiye'deki Sağlayıcılar

#### 10. Craftgate
- **Üye İşyeri Paneli:** [craftgate.io/urunler/gelismis-uye-isyeri-paneli](https://craftgate.io/urunler/gelismis-uye-isyeri-paneli)
- **API Dökümantasyonu:** [developer.craftgate.io](https://developer.craftgate.io)
- Gelişmiş panel üzerinden iptal/iade yönetimi
- Tek entegrasyonla çoklu sanal POS desteği
- CREDIT işlem tipi ile iade yapılabilir

#### 11. iyzico
- **İşyeri Paneli:** [iyzico.com/en/business](https://www.iyzico.com/en/business)
- **Terminal API İade:** [docs.iyzico.com - İptal/İade](https://docs.iyzico.com/urunler/fiziksel-pos/terminal-api-entegrasyonu/vuk-507-servisleri/iptal-iade)
- Fiziksel POS ve sanal POS üzerinden iade desteği
- Merchant Panel'den iade yönetimi

#### 12. Param (TurkPos)
- **API Dökümantasyonu:** [dev.param.com.tr/tr/api/islem-iptal-ve-iadeleri](https://dev.param.com.tr/tr/api/islem-iptal-ve-iadeleri)
- `TP_Islem_Iptal_Iade_Kismi2` metodu ile iptal/iade
- Durum parametresine `IPTAL` veya `IADE` değeri girilir
- Kısmi iade desteği mevcut

#### 13. Garanti BBVA Sanal POS
- **Developer Portal:** [dev.garantibbva.com.tr](https://dev.garantibbva.com.tr/sanalpos-iade-iade-3dsiz)
- 3D'siz iade işlemleri
- Tam ve kısmi iade desteği

#### 14. Payfoni Gateway
- **Site:** [payfoni.com.tr/gateway](https://payfoni.com.tr/gateway)
- Çoklu POS yönlendirme ve kurtarma sistemi
- Birden fazla sanal POS'u tek panelden yönetme

#### 15. SanalPos.com
- **Site:** [sanalpos.com](https://www.sanalpos.com/)
- Tek entegrasyonla Visa, Mastercard, Troy, Amex destekler
- PHP, Python, Node.js, Java, C#, Ruby, Go SDK'ları mevcut

#### 16. Ödeal
- **Dökümantasyon:** [docs.odeal.com/sanalpos/tr/sss](https://docs.odeal.com/sanalpos/tr/sss)
- İptal ve iade API desteği
- Kısmi iade destekler

---

### Önemli Notlar

- **Güvenlik:** Unmatched refund yüksek dolandırıcılık riski taşır. Çoğu sağlayıcıda varsayılan olarak kapalıdır.
- **Yetkilendirme:** Genellikle Merchant Supervisor veya üst düzey yetki gerektirir.
- **Aktivasyon:** Çoğu sağlayıcıda bu özelliğin açılması için destek ekibiyle iletişime geçilmesi gerekir.
- **Limit:** Günlük ve işlem başına iade tutarı limitleri uygulanır.
