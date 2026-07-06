# devasa

## TSYS PHP Virtual Terminal Ornegi

Bu repoya tek dosyalik bir PHP odeme ekrani eklendi:

- `tsys_checkout.php`
- `.env.example`

### Kurulum

1. `.env.example` dosyasini `.env` olarak kopyala:

   ```bash
   cp .env.example .env
   ```

2. TSYS tarafindan verilen **gercek API endpoint** ve `TSYS_API_KEY` degerlerini `.env` icinde guncelle.
   - Alternatif olarak bu iki degeri form ekranindan da girebilirsin.
   - Varsayilan endpoint `https://ssl2.vitalps.net/scripts/gateway.dll?transact` olarak ayarlandi.
   - Bazi hesaplarda API key gerekmez; bazilarinda gateway/partner key gerekir.
3. Hemen deneme icin formdan `Gateway Mode = Mock` sec. Bu modda dis servise cikmadan basarili/hatali test cevabi uretilir.
4. Canliya gecis icin `Gateway Mode = Live TSYS` sec ve gercek endpoint/key kullan.

3. Yerelde calistir:

   ```bash
   php -S 0.0.0.0:8080
   ```

4. Tarayicida ac:

   ```text
   http://localhost:8080/tsys_checkout.php
   ```

### Uretim Notlari (Onemli)

- Bu ornek teknik entegrasyon iskeletidir.
- Gercek internet odemelerinde PCI DSS kapsaminda kart verisini dogrudan sunucuna almamak icin TSYS hosted fields/tokenizasyon kullan.
- 3D Secure, AVS/CVV kontrolu, fraud kurallari ve webhook ile onay/reversal akisi eklenmelidir.
- Iade (`return`) islemi icin ekranda `Original Transaction ID` zorunludur.
- Merchant number otomatik 12 haneye normalize edilir, V Number `V1234567 -> 71234567` seklinde normalize edilir.
