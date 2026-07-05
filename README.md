# devasa

## TSYS Virtual Terminal - Web + C++ App

Bu depoda iki farklı demo bulunur:

1. **Web arayüzü** (`index.html`, `styles.css`, `app.js`)
2. **C++ uygulaması** (`tsys_terminal.cpp`)

Web sürümünde ekran görüntüsüne benzer terminal düzeni bulunur:
- üst menü ve sekmeli görünüm
- işlem sekmeleri: **Charge / Auth / Void / Return (iade)**
- sağ panelde transaction result log alanı

## Web sürümü çalıştırma

Bu proje statik dosyalardan oluşur. `index.html` dosyasını tarayıcıda açmanız yeterlidir.

İsterseniz yerel sunucu ile:

```bash
python3 -m http.server 8080
```

Ardından `http://localhost:8080` adresine gidin.

## C++ uygulaması çalıştırma

Uygulama terminal üzerinden çalışır ve şu işlemleri destekler:
- Charge (Sale)
- Auth
- Void (orijinal reference ile)
- Return / Iade (orijinal reference ile)
- İşlem listeleme
- Merchant ID / Terminal ID girme ve sonradan güncelleme
- Kod içinde sabit merchant profili (DBA, adres, MCC, BIN, Store/Terminal/Location, vb.)
- Menüden `7) Show Merchant Profile` ile profil görüntüleme

Not: Void/Return için `Original Reference #` alanına `LAST` yazarak son Charge/Auth işlemini otomatik kullanabilirsiniz.

Derleme:

```bash
make
```

Çalıştırma:

```bash
./tsys-terminal
```
