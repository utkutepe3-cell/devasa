# PayTrace Hesap Test Uygulaması

PayTrace API hesaplarınızın çalışıp çalışmadığını test eden Python uygulaması.

## Özellikler

- **Bağlantı Testi** — Production ve Sandbox sunucu erişim kontrolü
- **Tek Hesap Testi** — OAuth 2.0 ile kimlik doğrulama
- **Toplu Hesap Testi** — Dosyadan çoklu hesap kontrolü (thread destekli)
- **Tam API Testi** — Kimlik doğrulama + API endpoint testleri
- **İnteraktif Menü** — Kolay kullanım için menü arayüzü
- **JSON Çıktı** — Programatik kullanım için JSON desteği

## Kurulum

```bash
pip install -r requirements.txt
```

## Kullanım

### İnteraktif Menü
```bash
python3 paytrace_test_app.py
```

### Hızlı Bağlantı Testi
```bash
python3 paytrace_test_app.py --quick
```

### Tek Hesap Testi
```bash
python3 paytrace_test_app.py -u KULLANICI -p SIFRE
python3 paytrace_test_app.py -u KULLANICI -p SIFRE --sandbox
```

### Toplu Hesap Testi
```bash
python3 paytrace_test_app.py -f hesaplar.txt
python3 paytrace_test_app.py -f hesaplar.txt -t 5 --sandbox
```

### Tam API Testi (Endpoint'ler dahil)
```bash
python3 paytrace_test_app.py -u KULLANICI -p SIFRE -i INTEGRATOR_ID
```

### JSON Çıktı
```bash
python3 paytrace_test_app.py -u KULLANICI -p SIFRE --json
```

## Hesap Dosyası Formatı

Her satırda bir hesap, aşağıdaki formatlardan biriyle:
```
kullanici:sifre
kullanici sifre
kullanici|sifre
```

## Parametreler

| Parametre | Açıklama |
|-----------|----------|
| `-u`, `--username` | PayTrace kullanıcı adı |
| `-p`, `--password` | PayTrace şifresi |
| `-i`, `--integrator-id` | Integrator ID (API endpoint testi için) |
| `-f`, `--file` | Hesap dosyası yolu |
| `-t`, `--threads` | Thread sayısı (varsayılan: 3) |
| `--sandbox` | Sandbox ortamını kullan |
| `--quick` | Sadece bağlantı testi |
| `--proxy` | Proxy adresi |
| `--json` | JSON formatında çıktı |
| `--timeout` | İstek zaman aşımı (saniye) |

## Diğer Araçlar

- `paytrace_checker.py` — Toplu hesap doğrulama aracı
- `paytrace_refund.py` — Refund/void CLI aracı
