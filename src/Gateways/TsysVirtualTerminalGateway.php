<?php

declare(strict_types=1);

namespace Devasa\Gateways;

final class TsysVirtualTerminalGateway
{
    /**
     * Returns TSYS Virtual Terminal gateway metadata and required fields.
     */
    public function getGatewayInfo(): array
    {
        return [
            'gateway' => 'tsys_virtual_terminal',
            'display_name' => 'TSYS Virtual Terminal',
            'provider' => 'TSYS',
            'mode' => 'virtual_terminal',
            'api' => [
                'base_url' => 'https://secure.ipg-online.com',
                'authorize_endpoint' => '/api/v1/transactions/authorize',
                'capture_endpoint' => '/api/v1/transactions/capture',
                'refund_endpoint' => '/api/v1/transactions/refund',
            ],
            'credentials' => [
                'merchant_id' => '',
                'terminal_id' => '',
                'store_id' => '',
                'api_username' => '',
                'api_password' => '',
                'shared_secret' => '',
            ],
            'required_customer_fields' => [
                'first_name',
                'last_name',
                'email',
                'phone',
            ],
            'required_payment_fields' => [
                'card_holder_name',
                'card_number',
                'expiry_month',
                'expiry_year',
                'cvv',
                'amount',
                'currency',
            ],
            'supported_currencies' => [
                'TRY',
                'USD',
                'EUR',
                'GBP',
            ],
            'supports_3d_secure' => true,
            'supports_installment' => false,
        ];
    }
}
