# PayTrace Giriş Aracı

Kendi PayTrace hesaplarınızla OAuth 2.0 password grant üzerinden giriş yapıp access token alan Python aracı.

## Kurulum

```bash
pip install -r requirements.txt
```

## Kullanım

### Tek hesap

```bash
python3 paytrace_login.py -u KULLANICI -p SIFRE
python3 paytrace_login.py -u KULLANICI -p SIFRE --sandbox
python3 paytrace_login.py -u KULLANICI -p SIFRE --save token.json
```

### Birden fazla hesabınız

`hesaplar.txt` oluşturun (`hesaplar.example.txt` örneğine bakın):

```
hesap1:sifre1
hesap2|sifre2
hesap3 sifre3
```

```bash
python3 paytrace_login.py -f hesaplar.txt
python3 paytrace_login.py -f hesaplar.txt --save-dir tokens
```

### İnteraktif menü

```bash
python3 paytrace_login.py
```

### JSON çıktı

```bash
python3 paytrace_login.py -u KULLANICI -p SIFRE --json --show-token
```

## Parametreler

| Parametre | Açıklama |
|-----------|----------|
| `-u`, `--username` | PayTrace kullanıcı adı |
| `-p`, `--password` | PayTrace şifresi |
| `-f`, `--file` | Hesap listesi dosyası |
| `--sandbox` | Sandbox ortamı |
| `--save PATH` | Tek hesap token kaydı |
| `--save-dir DIR` | Çoklu hesap token klasörü |
| `--json` | JSON çıktı |
| `--timeout` | İstek zaman aşımı (sn) |

## API

- Production: `https://api.paytrace.com/oauth/token`
- Sandbox: `https://api.sandbox.paytrace.com/oauth/token`
- Grant type: `password`
- Token süresi: genelde 2 saat

> Yalnızca size ait PayTrace hesaplarıyla kullanın.
