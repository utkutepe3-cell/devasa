# devasa - PayTrace Sale Refund Tool

PayTrace'de sale (satış) bölümünden refund yapmanızı sağlayan araç. Satışları listeler, seçtiğiniz işleme doğrudan refund veya void uygular.

**Windows EXE olarak çalışır - Python kurmanıza gerek yok!**

## EXE Oluşturma (Windows)

### Yöntem 1: Bat Dosyası ile (Kolay)
```
build_exe.bat
```
Çift tıklayın, `dist\PayTrace_Refund.exe` oluşacaktır.

### Yöntem 2: Manuel
```bash
pip install pyinstaller requests
pyinstaller --onefile --console --name PayTrace_Refund paytrace_refund.py
```

EXE dosyası `dist\PayTrace_Refund.exe` konumunda oluşur.

## Kullanım (EXE)

### Satışları Listele ve Refund Yap
```
PayTrace_Refund.exe -u KULLANICI -p SIFRE -i INTEGRATOR_ID --list-sales
```

### Direkt Transaction ID ile Refund
```
PayTrace_Refund.exe -u KULLANICI -p SIFRE -i INTEGRATOR_ID -t 12345
```

### Kısmi Refund
```
PayTrace_Refund.exe -u KULLANICI -p SIFRE -i INTEGRATOR_ID -t 12345 --amount 10.50
```

### Void (Aynı Gün İptal)
```
PayTrace_Refund.exe -u KULLANICI -p SIFRE -i INTEGRATOR_ID -t 12345 --void
```

### Son 90 Günün Satışları
```
PayTrace_Refund.exe -u KULLANICI -p SIFRE -i INTEGRATOR_ID --list-sales --days 90
```

### Sandbox Test
```
PayTrace_Refund.exe -u KULLANICI -p SIFRE -i INTEGRATOR_ID --list-sales --sandbox
```

## Parametreler

| Parametre | Kısa | Açıklama |
|-----------|------|----------|
| `--username` | `-u` | PayTrace API kullanıcı adı |
| `--password` | `-p` | PayTrace API şifresi |
| `--integrator-id` | `-i` | PayTrace Integrator ID |
| `--list-sales` | | Satışları listele (interaktif refund) |
| `--transaction-id` | `-t` | Doğrudan Transaction ID ile refund |
| `--amount` | | Kısmi iade tutarı (belirtilmezse tam iade) |
| `--void` | | Void (iptal) işlemi yap |
| `--days` | | Kaç günlük satış getirilsin (varsayılan: 30) |
| `--sandbox` | | Sandbox (test) ortamını kullan |

## Önemli Notlar

- **Refund** sadece **settle olmuş** işlemler için çalışır (genellikle ertesi gün)
- **Void** sadece **henüz settle olmamış** (pending) işlemler için çalışır (aynı gün)
- Araç akıllıdır: refund başarısız olursa otomatik void önerir
- Kısmi iade tutarı orijinal tutara eşit veya daha az olmalıdır

## Refund vs Void

| Durum | Ne Yapmalı | Parametre |
|-------|-----------|-----------|
| İşlem bugün yapıldı (settle olmadı) | Void | `--void` |
| İşlem daha önce yapıldı (settle oldu) | Refund | (varsayılan) |
| Hangisi olduğunu bilmiyorum | Refund dene | Araç otomatik void önerir |

## API Kullanıcısı Oluşturma

1. PayTrace Virtual Terminal'e giriş yapın
2. **Account → Users** bölümüne gidin
3. Yeni bir API kullanıcısı oluşturun
4. **Refund yetkisi** verildiğinden emin olun

## Hata Kodları

| Kod | Açıklama | Çözüm |
|-----|----------|-------|
| 106 | İade başarılı | - |
| 107 | İade başarısız | İşlem detaylarını kontrol edin |
| 817 | Settle olmamış | `--void` kullanın |
| 818 | Settle olmuş | `--void` kaldırın (refund yapın) |
| 819 | Tutar fazla | Daha düşük tutar girin |
| 981 | Yetki yok | API kullanıcısına refund izni verin |
