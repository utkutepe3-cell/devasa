# PayTrace Mass Checker (Token API)

PayTrace API'ye toplu username/password kontrolü yapan Python aracı. OAuth 2.0 password grant ile token doğrulaması yapar.

## Kurulum

```bash
pip install -r requirements.txt
```

## Kullanım

### Toplu kontrol (mass check)

`combo.txt` dosyası oluştur — her satırda `user pass` formatında:

```
user1 pass1
user2 pass2
user3 pass3
```

Desteklenen ayraçlar: boşluk, `:`, `|`, tab

```
user1 pass1
user2:pass2
user3|pass3
```

Çalıştır:

```bash
python paytrace_checker.py -f combo.txt
```

### Thread ile hızlı kontrol

```bash
python paytrace_checker.py -f combo.txt -t 10
```

### Hit sonuçlarını dosyaya kaydet

```bash
python paytrace_checker.py -f combo.txt -o hits.txt
```

Belirtilmezse otomatik `hits_YYYYMMDD_HHMMSS.txt` oluşturulur.

### Sandbox ortamı

```bash
python paytrace_checker.py -f combo.txt --sandbox
```

### Tek hesap kontrol

```bash
python paytrace_checker.py -u kullanici -p sifre
```

### JSON çıktı

```bash
python paytrace_checker.py -f combo.txt --json
```

## Tüm parametreler

| Parametre | Açıklama |
|-----------|----------|
| `-f`, `--file` | Combo dosyası yolu |
| `-u`, `--username` | Tek kullanıcı adı |
| `-p`, `--password` | Tek şifre |
| `-t`, `--threads` | Thread sayısı (varsayılan: 3) |
| `-o`, `--output` | Hit çıktı dosyası |
| `--retries` | Hata tekrar deneme sayısı (varsayılan: 2) |
| `--sandbox` | Sandbox ortamı kullan |
| `--json` | JSON formatında çıktı |
| `--timeout` | İstek zaman aşımı (varsayılan: 30s) |

## API Bilgisi

- **Production:** `https://api.paytrace.com/oauth/token`
- **Sandbox:** `https://api.sandbox.paytrace.com/oauth/token`
- **Grant type:** `password`
- Token süresi: 2 saat
