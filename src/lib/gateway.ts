/**
 * Virtual terminal gateway profile — PayTrace / Datacap (portal.dcap) style.
 * Blind unmatched credit = standalone credit with card data, no original sale RefNo.
 */
export interface VirtualTerminalGatewayInfo {
  gateway: string
  display_name: string
  provider: string
  mode: 'virtual_terminal'
  inspired_by: string[]
  virtual_terminal_enabled: boolean
  supports_sale: boolean
  supports_matched_return: boolean
  /** Standalone / blind / unmatched credit (no original transaction required) */
  supports_blind_unmatched_credit: boolean
  blind_unmatched_credit: {
    enabled_by_default: boolean
    requires_merchant_entitlement: boolean
    requires_card_present: boolean
    requires_original_ref: boolean
    aliases: string[]
  }
  card_types_accepted: string[]
  entry_modes: string[]
  status: 'active' | 'disabled'
}

export function getPayTraceDcapStyleGateway(
  overrides: Partial<VirtualTerminalGatewayInfo> = {},
): VirtualTerminalGatewayInfo {
  const base: VirtualTerminalGatewayInfo = {
    gateway: 'paytrace_dcap_virtual_terminal',
    display_name: 'PayTrace / Datacap-style Virtual Terminal',
    provider: 'CornerPay Sandbox',
    mode: 'virtual_terminal',
    inspired_by: [
      'PayTrace Virtual Terminal (standalone REFUND / credit)',
      'Datacap portal.dcap Virtual Terminal (Return / credit without matched sale)',
    ],
    virtual_terminal_enabled: true,
    supports_sale: true,
    supports_matched_return: true,
    supports_blind_unmatched_credit: true,
    blind_unmatched_credit: {
      enabled_by_default: true,
      requires_merchant_entitlement: true,
      requires_card_present: false,
      requires_original_ref: false,
      aliases: [
        'blind credit',
        'unmatched credit',
        'unmatched refund',
        'standalone credit',
        'independent credit',
        'open credit',
      ],
    },
    card_types_accepted: ['Visa', 'Mastercard', 'American Express', 'Discover'],
    entry_modes: ['Manual', 'Swipe', 'Token'],
    status: 'active',
  }

  return { ...base, ...overrides }
}

export function createVirtualTerminal(config: {
  merchantName: string
  allowBlindUnmatchedCredit: boolean
}) {
  const gateway = getPayTraceDcapStyleGateway({
    supports_blind_unmatched_credit: config.allowBlindUnmatchedCredit,
    status: config.allowBlindUnmatchedCredit ? 'active' : 'disabled',
    blind_unmatched_credit: {
      ...getPayTraceDcapStyleGateway().blind_unmatched_credit,
      enabled_by_default: config.allowBlindUnmatchedCredit,
    },
  })

  return {
    success: true,
    message: config.allowBlindUnmatchedCredit
      ? 'Virtual terminal active with blind unmatched credit enabled.'
      : 'Virtual terminal active; blind unmatched credit is disabled for this merchant.',
    virtual_terminal: {
      id: `vt-${config.merchantName.trim().toLowerCase().replace(/\s+/g, '-') || 'demo'}`,
      status: 'active',
      blind_unmatched_credit_status: config.allowBlindUnmatchedCredit ? 'enabled' : 'disabled',
      provider_style: 'paytrace_portal_dcap',
    },
    gateway,
  }
}
