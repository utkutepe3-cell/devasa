# devasa - PayTrace Sale Refund Tool

PayTrace'de sale (satış) bölümünden refund yapmanızı sağlayan araç. Satışları listeler, seçtiğiniz işleme doğrudan refund veya void uygular.

## Kurulum

```bash
pip install -r requirements.txt
```

## Hızlı Başlangıç

### 1. Satışları Listele ve Refund Yap (İnteraktif Mod)
```bash
python paytrace_refund.py -u API_USER -p API_PASS -i INTEGRATOR_ID --list-sales
```
Bu komut:
- Son 30 günün satışlarını tablo halinde gösterir
- Refund yapmak istediğiniz işlemi numara ile seçersiniz
- Tam veya kısmi iade tutarını girersiniz
- Onayladığınızda refund işlenir

### 2. Son 90 Günün Satışlarını Listele
```bash
python paytrace_refund.py -u API_USER -p API_PASS -i INTEGRATOR_ID --list-sales --days 90
```

### 3. Direkt Transaction ID ile Refund
```bash
python paytrace_refund.py -u API_USER -p API_PASS -i INTEGRATOR_ID -t TRANSACTION_ID
```

### 4. Kısmi Refund
```bash
python paytrace_refund.py -u API_USER -p API_PASS -i INTEGRATOR_ID -t TRANSACTION_ID --amount 10.50
```

### 5. Void (Aynı Gün İptal)
```bash
python paytrace_refund.py -u API_USER -p API_PASS -i INTEGRATOR_ID -t TRANSACTION_ID --void
```

### 6. Sandbox Test
```bash
python paytrace_refund.py -u API_USER -p API_PASS -i INTEGRATOR_ID --list-sales --sandbox
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
