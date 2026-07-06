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
