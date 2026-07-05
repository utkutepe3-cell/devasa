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
            'business' => [
                'dba' => 'Get Your Life Back LLC',
                'street_address' => '28 Tindall Rd',
                'city' => 'Middletown',
                'state' => 'New Jersey',
                'zip' => '07748',
                'customer_service_phone' => '+1 800-993-0929',
            ],
            'merchant_profile' => [
                'merchant_number' => '401151759710',
                'v_number' => 'V6298237',
                'mcc' => '5499',
                'bin' => '494306',
                'chain' => '031776',
                'agent_bank' => '031776',
                'store_number' => '0001',
                'terminal_number' => '7000',
                'location_number' => '00001',
                'approved_monthly_volume' => '30000.00',
                'approved_monthly_volume_currency' => 'USD',
            ],
            'api' => [
                'base_url' => 'https://secure.ipg-online.com',
                'authorize_endpoint' => '/api/v1/transactions/authorize',
                'capture_endpoint' => '/api/v1/transactions/capture',
                'refund_endpoint' => '/api/v1/transactions/refund',
            ],
            'credentials' => [
                'merchant_id' => '401151759710',
                'terminal_id' => '7000',
                'store_id' => '0001',
                'api_username' => '',
                'api_password' => '',
                'shared_secret' => '',
            ],
            'card_types_accepted' => [
                'Visa',
                'Mastercard',
                'PIN Debit',
                'Gift Card',
                'American Express',
                'EBT',
                'Discover',
                'JCB',
                'ACH',
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
