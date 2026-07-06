# devasa

## TSYS Virtual Terminal Gateway

`src/Gateways/TsysVirtualTerminalGateway.php` dosyası, TSYS virtual terminal yapılandırmasını ve gerekli alanları döndürür.

Örnek kullanım:

```php
<?php

require_once __DIR__ . '/src/Gateways/TsysVirtualTerminalGateway.php';

$gateway = new TsysVirtualTerminalGateway();
$info = $gateway->getGatewayInfo();
$virtualTerminal = $gateway->createVirtualTerminal();
$virtualTerminalViaCreate = $gateway->create(); // alias
```

## Virtual Terminal Panel

Kart ile odeme almak ve iade yapmak icin panel:

```bash
php -S 127.0.0.1:8080 -t panel
```

Ardindan tarayicida ac:

`http://127.0.0.1:8080/index.php`

### XAMPP Notu (Windows)

Eger dosyayi `C:\xampp\htdocs` altinda calistiriyorsan, su yapiyi koru:

- `C:\xampp\htdocs\index.php` (panel dosyasi)
- `C:\xampp\htdocs\src\Gateways\TsysVirtualTerminalGateway.php` (gateway sinifi)

Panel, hem `../src/...` hem `./src/...` yollarini otomatik dener.

Eger beyaz ekran goruyorsan:

- `php -v` ile surumu kontrol et (onerilen: PHP 7.4+)
- panel artik hata mesajlarini ekrana basar; sayfayi yenileyip hatayi kontrol et
