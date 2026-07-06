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
            'status' => 'active',
            'virtual_terminal_enabled' => true,
            'return_refund_enabled' => true,
            'supports_3d_secure' => true,
            'supports_installment' => false,
            'supports_refund' => true,
        ];
    }

    /**
     * Creates an active virtual terminal response payload.
     */
    public function createVirtualTerminal(array $overrides = []): array
    {
        $gatewayInfo = $this->getGatewayInfo();
        $terminal = array_replace(
            [
                'merchant_number' => $gatewayInfo['merchant_profile']['merchant_number'],
                'store_number' => $gatewayInfo['merchant_profile']['store_number'],
                'terminal_number' => $gatewayInfo['merchant_profile']['terminal_number'],
                'location_number' => $gatewayInfo['merchant_profile']['location_number'],
            ],
            $overrides
        );

        return [
            'success' => true,
            'message' => 'Virtual terminal created successfully.',
            'status' => 'active',
            'return' => [
                'enabled' => true,
                'status' => 'active',
            ],
            'virtual_terminal' => [
                'id' => sprintf(
                    'vt-%s-%s',
                    $terminal['terminal_number'],
                    $terminal['location_number']
                ),
                'status' => 'active',
                'return_refund_status' => 'active',
                'merchant_number' => $terminal['merchant_number'],
                'store_number' => $terminal['store_number'],
                'terminal_number' => $terminal['terminal_number'],
                'location_number' => $terminal['location_number'],
                'supported_card_types' => $gatewayInfo['card_types_accepted'],
            ],
        ];
    }

    /**
     * Alias for integrations that call a generic create method.
     */
    public function create(array $overrides = []): array
    {
        return $this->createVirtualTerminal($overrides);
    }
}

// Allows "new TsysVirtualTerminalGateway()" without namespace.
if (!class_exists('TsysVirtualTerminalGateway', false)) {
    class_alias(TsysVirtualTerminalGateway::class, 'TsysVirtualTerminalGateway');
}
