export type TabId =
  | 'payment'
  | 'blind-credit'
  | 'recurring'
  | 'gift'
  | 'reports'
  | 'configure'

export type SaleType = 'Credit' | 'Gift' | 'ACH'
export type EntryMode = 'Manual' | 'Swipe' | 'Token'
/** Sale / matched Return / standalone Blind Unmatched Credit (PayTrace · portal.dcap style) */
export type TranType = 'Sale' | 'Return' | 'BlindCredit'
export type GiftOp = 'Sale' | 'Load' | 'Balance'

export type BlindCreditReason =
  | 'customer_request'
  | 'duplicate_charge'
  | 'product_return'
  | 'service_adjustment'
  | 'goodwill'
  | 'other'

export interface MerchantConfig {
  secret: string
  merchantName: string
  merchantPhone: string
  merchantAddress1: string
  merchantAddress2: string
  allowPartialAuth: boolean
  /** When true, VT may issue credits without an original sale (unmatched / blind). */
  allowBlindUnmatchedCredit: boolean
}

export interface PaymentResponse {
  id: string
  account: string
  amount: string
  brand: string
  refNo: string
  authCode: string
  tranType: TranType | GiftOp
  saleType: SaleType | 'Gift'
  processedAt: string
  balance?: string
  /** Present on blind / unmatched credits */
  unmatched?: boolean
  reason?: BlindCreditReason
  reasonNote?: string
  originalRefNo?: string | null
}

export interface RecurringAccount {
  id: string
  alias: string
  account: string
  amount: string
  token: string
  lastProcessedDate: string | null
  history: { date: string; amount: string; refNo: string; status: string }[]
}

export interface NotificationItem {
  id: string
  type: 'success' | 'error' | 'info'
  message: string
}

export const DEFAULT_CONFIG: MerchantConfig = {
  secret: '',
  merchantName: '',
  merchantPhone: '',
  merchantAddress1: '',
  merchantAddress2: '',
  allowPartialAuth: true,
  allowBlindUnmatchedCredit: true,
}

export const BLIND_CREDIT_REASONS: { value: BlindCreditReason; label: string }[] = [
  { value: 'customer_request', label: 'Customer request' },
  { value: 'duplicate_charge', label: 'Duplicate charge' },
  { value: 'product_return', label: 'Product / service return' },
  { value: 'service_adjustment', label: 'Service adjustment' },
  { value: 'goodwill', label: 'Goodwill / courtesy credit' },
  { value: 'other', label: 'Other' },
]
