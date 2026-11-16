export type TabId = 'payment' | 'recurring' | 'gift' | 'reports' | 'configure'

export type SaleType = 'Credit' | 'Gift'
export type EntryMode = 'Manual' | 'Swipe' | 'Token'
export type TranType = 'Sale' | 'Return'
export type GiftOp = 'Sale' | 'Load' | 'Balance'

export interface MerchantConfig {
  secret: string
  merchantName: string
  merchantPhone: string
  merchantAddress1: string
  merchantAddress2: string
  allowPartialAuth: boolean
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
}
