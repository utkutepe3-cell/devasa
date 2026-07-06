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
