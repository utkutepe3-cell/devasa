import type { MerchantConfig, PaymentResponse, RecurringAccount } from '../types'
import { DEFAULT_CONFIG } from '../types'

const KEYS = {
  config: 'cornerpay.vt.config',
  payments: 'cornerpay.vt.payments',
  recurring: 'cornerpay.vt.recurring',
  gift: 'cornerpay.vt.gift',
  session: 'cornerpay.vt.session',
} as const

function read<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(key)
    if (!raw) return fallback
    return JSON.parse(raw) as T
  } catch {
    return fallback
  }
}

function write<T>(key: string, value: T) {
  localStorage.setItem(key, JSON.stringify(value))
}

export function loadConfig(): MerchantConfig {
  return { ...DEFAULT_CONFIG, ...read(KEYS.config, {}) }
}

export function saveConfig(config: MerchantConfig) {
  write(KEYS.config, config)
}

export function loadPayments(): PaymentResponse[] {
  return read(KEYS.payments, [])
}

export function savePayments(items: PaymentResponse[]) {
  write(KEYS.payments, items.slice(0, 50))
}

export function loadRecurring(): RecurringAccount[] {
  return read(KEYS.recurring, [])
}

export function saveRecurring(items: RecurringAccount[]) {
  write(KEYS.recurring, items)
}

export function loadGiftResponses(): PaymentResponse[] {
  return read(KEYS.gift, [])
}

export function saveGiftResponses(items: PaymentResponse[]) {
  write(KEYS.gift, items.slice(0, 50))
}

export function loadSession(): { username: string } | null {
  return read(KEYS.session, null)
}

export function saveSession(username: string) {
  write(KEYS.session, { username })
}

export function clearSession() {
  localStorage.removeItem(KEYS.session)
}
