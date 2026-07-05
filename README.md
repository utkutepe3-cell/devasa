# devasa

## TSYS Virtual Terminal Gateway

`src/Gateways/TsysVirtualTerminalGateway.php` dosyası, TSYS virtual terminal yapılandırmasını ve gerekli alanları döndürür.

Örnek kullanım:

```php
<?php

use Devasa\Gateways\TsysVirtualTerminalGateway;

$gateway = new TsysVirtualTerminalGateway();
$info = $gateway->getGatewayInfo();
```
