# devasa - PayTrace Refund & Void Tool

PayTrace üzerinden refund (iade) ve void (iptal) işlemlerini API ile yapmanızı sağlayan araç.

## Kurulum

```bash
pip install -r requirements.txt
```

## Kullanım

### Tam Refund (Settle Olmuş İşlem)
```bash
python paytrace_refund.py -u API_USER -p API_PASS -t TRANSACTION_ID -i INTEGRATOR_ID
```

### Kısmi Refund
```bash
python paytrace_refund.py -u API_USER -p API_PASS -t TRANSACTION_ID -i INTEGRATOR_ID --amount 10.50
```

### Void / İptal (Henüz Settle Olmamış İşlem)
```bash
python paytrace_refund.py -u API_USER -p API_PASS -t TRANSACTION_ID -i INTEGRATOR_ID --void
```

### İşlem Bilgisi Görüntüleme
```bash
python paytrace_refund.py -u API_USER -p API_PASS -t TRANSACTION_ID -i INTEGRATOR_ID --info
```

### Sandbox (Test) Ortamında Çalıştırma
```bash
python paytrace_refund.py -u API_USER -p API_PASS -t TRANSACTION_ID -i INTEGRATOR_ID --sandbox
```

## Parametreler

| Parametre | Kısa | Açıklama |
|-----------|------|----------|
| `--username` | `-u` | PayTrace API kullanıcı adı |
| `--password` | `-p` | PayTrace API şifresi |
| `--transaction-id` | `-t` | İşlem numarası (Transaction ID) |
| `--integrator-id` | `-i` | PayTrace Integrator ID |
| `--amount` | | Kısmi iade tutarı (belirtilmezse tam iade) |
| `--void` | | Void (iptal) işlemi yap |
| `--sandbox` | | Sandbox ortamını kullan |
| `--info` | | Sadece işlem bilgilerini göster |

## Önemli Notlar

- **Refund** sadece **settle olmuş** işlemler için çalışır
- **Void** sadece **henüz settle olmamış** (pending) işlemler için çalışır
- Aynı gün yapılan işlemler genellikle henüz settle olmamıştır → **void** kullanın
- Ertesi gün veya sonrasında settle olmuş işlemler için → **refund** kullanın
- Kısmi iade tutarı orijinal tutara eşit veya daha az olmalıdır

## API Kullanıcısı Oluşturma

PayTrace Virtual Terminal'de API kullanıcısı oluşturmak için:
1. PayTrace Virtual Terminal'e giriş yapın
2. Account → Users bölümüne gidin  
3. Yeni bir API kullanıcısı oluşturun
4. Bu kullanıcının refund yetkisi olduğundan emin olun

## Hata Kodları

| Kod | Açıklama |
|-----|----------|
| 106 | İade başarılı |
| 107 | İade başarısız |
| 817 | İşlem settle olmamış, refund yapılamaz (void deneyin) |
| 818 | İşlem settle olmuş, void yapılamaz (refund deneyin) |
| 819 | İade tutarı orijinal tutarı aşamaz |
| 981 | Yetersiz yetki (refund izni gerekli) |
