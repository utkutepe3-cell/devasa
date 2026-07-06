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
