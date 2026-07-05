# devasa

## TSYS Virtual Terminal Demo

Bu depoya basit bir **TSYS Virtual Terminal** arayüzü eklendi.

Yeni sürümde ekran görüntüsüne benzer terminal düzeni bulunur:
- üst menü ve sekmeli görünüm
- işlem sekmeleri: **Charge / Auth / Void / Return (iade)**
- sağ panelde transaction result log alanı

### Çalıştırma

Bu proje statik dosyalardan oluşur. `index.html` dosyasını tarayıcıda açmanız yeterlidir.

İsterseniz yerel sunucu ile:

```bash
python3 -m http.server 8080
```

Ardından `http://localhost:8080` adresine gidin.
