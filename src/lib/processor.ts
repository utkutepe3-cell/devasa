import type { PaymentResponse, SaleType, TranType, GiftOp } from '../types'

const BRANDS: Record<string, string> = {
  '4': 'VISA',
  '5': 'MC',
  '3': 'AMEX',
  '6': 'DISC',
}

function maskAccount(account: string): string {
  const digits = account.replace(/\D/g, '')
  if (digits.length < 4) return 'XXXX'
  return `XXXX-XXXX-XXXX-${digits.slice(-4)}`
}

function detectBrand(account: string): string {
  const first = account.replace(/\D/g, '')[0]
  return BRANDS[first] ?? 'CARD'
}

function refNo(): string {
  return Math.floor(10000000 + Math.random() * 89999999).toString()
}

function authCode(): string {
  return Math.floor(100000 + Math.random() * 899999).toString()
}

function sleep(ms: number) {
  return new Promise((r) => setTimeout(r, ms))
}

export function formatAmount(value: string): string {
  const n = Number.parseFloat(value.replace(/[^0-9.]/g, ''))
  if (Number.isNaN(n)) return '0.00'
  return n.toFixed(2)
}

export async function processPayment(input: {
  amount: string
  account: string
  saleType: SaleType
  tranType: TranType
  cvv?: string
  expiration?: string
  zip?: string
  token?: string
  mode: string
}): Promise<{ ok: true; response: PaymentResponse } | { ok: false; message: string }> {
  await sleep(900)

  const amount = formatAmount(input.amount)
  if (Number(amount) <= 0) {
    return { ok: false, message: 'Amount must be greater than zero.' }
  }

  const account =
    input.mode === 'Token'
      ? `TOK-${(input.token || 'XXXX').slice(0, 8).toUpperCase()}`
      : input.account.replace(/\D/g, '')

  if (input.mode === 'Manual' && account.length < 13) {
    return { ok: false, message: 'Enter a valid card number (demo accepts 13–19 digits).' }
  }

  if (input.mode === 'Manual' && input.saleType === 'Credit') {
    if (!input.expiration || input.expiration.replace(/\D/g, '').length < 4) {
      return { ok: false, message: 'Expiration is required (MMYY).' }
    }
  }

  // Demo decline: card ending in 0000
  if (account.endsWith('0000')) {
    return { ok: false, message: 'Declined — demo card ending in 0000 is always declined.' }
  }

  const brand = input.saleType === 'Gift' ? 'Gift' : detectBrand(account)
  const response: PaymentResponse = {
    id: crypto.randomUUID(),
    account: maskAccount(account),
    amount,
    brand,
    refNo: refNo(),
    authCode: authCode(),
    tranType: input.tranType,
    saleType: input.saleType,
    processedAt: new Date().toISOString(),
  }

  return { ok: true, response }
}

export async function processGift(input: {
  op: GiftOp
  amount: string
  account: string
  cvv?: string
}): Promise<{ ok: true; response: PaymentResponse } | { ok: false; message: string }> {
  await sleep(800)
  const account = input.account.replace(/\D/g, '')
  if (account.length < 8) {
    return { ok: false, message: 'Enter a gift card number (demo: 8+ digits).' }
  }

  const amount = input.op === 'Balance' ? '0.00' : formatAmount(input.amount)
  if (input.op !== 'Balance' && Number(amount) <= 0) {
    return { ok: false, message: 'Amount must be greater than zero.' }
  }

  const balanceBase = (Number(account.slice(-4)) % 500) + 25
  const balance =
    input.op === 'Load'
      ? (balanceBase + Number(amount)).toFixed(2)
      : input.op === 'Sale'
        ? Math.max(0, balanceBase - Number(amount)).toFixed(2)
        : balanceBase.toFixed(2)

  if (input.op === 'Sale' && Number(amount) > balanceBase) {
    return { ok: false, message: `Insufficient gift balance (demo available: $${balanceBase.toFixed(2)}).` }
  }

  return {
    ok: true,
    response: {
      id: crypto.randomUUID(),
      account: maskAccount(account),
      amount: input.op === 'Balance' ? balance : amount,
      brand: 'Gift',
      refNo: refNo(),
      authCode: authCode(),
      tranType: input.op,
      saleType: 'Gift',
      processedAt: new Date().toISOString(),
      balance,
    },
  }
}

export function sampleReportRows() {
  const now = new Date()
  return [
    {
      Date: now.toLocaleDateString(),
      Type: 'Sale',
      Brand: 'VISA',
      Amount: '42.50',
      RefNo: '88112031',
      Status: 'Approved',
    },
    {
      Date: now.toLocaleDateString(),
      Type: 'Sale',
      Brand: 'MC',
      Amount: '19.99',
      RefNo: '88112044',
      Status: 'Approved',
    },
    {
      Date: now.toLocaleDateString(),
      Type: 'Return',
      Brand: 'VISA',
      Amount: '12.00',
      RefNo: '88112055',
      Status: 'Approved',
    },
    {
      Date: now.toLocaleDateString(),
      Type: 'Gift Load',
      Brand: 'Gift',
      Amount: '50.00',
      RefNo: '88112066',
      Status: 'Approved',
    },
  ]
}
