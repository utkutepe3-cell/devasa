import { useEffect, useState } from 'react'
import type {
  MerchantConfig,
  NotificationItem,
  PaymentResponse,
  RecurringAccount,
  TabId,
} from './types'
import {
  clearSession,
  loadConfig,
  loadGiftResponses,
  loadPayments,
  loadRecurring,
  loadSession,
} from './lib/storage'
import { BlindCreditTab } from './components/BlindCreditTab'
import { ConfigureTab } from './components/ConfigureTab'
import { GiftTab } from './components/GiftTab'
import { LoginScreen } from './components/LoginScreen'
import { PaymentTab } from './components/PaymentTab'
import { RecurringTab } from './components/RecurringTab'
import { ReportsTab } from './components/ReportsTab'

const TABS: { id: TabId; label: string }[] = [
  { id: 'payment', label: 'Payment' },
  { id: 'blind-credit', label: 'Blind Credit' },
  { id: 'recurring', label: 'Recurring' },
  { id: 'gift', label: 'Gift' },
  { id: 'reports', label: 'Reports' },
  { id: 'configure', label: 'Configure' },
]

export default function App() {
  const [sessionUser, setSessionUser] = useState<string | null>(null)
  const [tab, setTab] = useState<TabId>('configure')
  const [config, setConfig] = useState<MerchantConfig>(loadConfig)
  const [payments, setPayments] = useState<PaymentResponse[]>(loadPayments)
  const [gift, setGift] = useState<PaymentResponse[]>(loadGiftResponses)
  const [recurring, setRecurring] = useState<RecurringAccount[]>(loadRecurring)
  const [notifications, setNotifications] = useState<NotificationItem[]>([])
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    const session = loadSession()
    if (session?.username) setSessionUser(session.username)
  }, [])

  useEffect(() => {
    if (!sessionUser) return
    setTab(config.secret ? 'payment' : 'configure')
  }, [sessionUser])

  function notify(type: NotificationItem['type'], message: string) {
    const item: NotificationItem = {
      id: crypto.randomUUID(),
      type,
      message,
    }
    setNotifications((list) => [item, ...list].slice(0, 4))
    if (type === 'success' || type === 'info') {
      window.setTimeout(() => {
        setNotifications((list) => list.filter((n) => n.id !== item.id))
      }, 8000)
    }
  }

  function closeNote(id: string) {
    setNotifications((list) => list.filter((n) => n.id !== id))
  }

  function signOut() {
    clearSession()
    setSessionUser(null)
    setNotifications([])
  }

  if (!sessionUser) {
    return <LoginScreen onEnter={setSessionUser} />
  }

  return (
    <div className="app-shell">
      <div className="terminal">
        <div className="brand-row">
          <div className="brand">
            <img
              className="brand-logo"
              src="/cornerpay-logo.png"
              alt="CornerPay"
              width={180}
              height={27}
            />
            <div className="brand-copy">
              <h1>
                CornerPay<em>.NET</em>
              </h1>
              <p>Virtual Terminal · {sessionUser}</p>
            </div>
          </div>
          <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
            <div className="demo-chip">Sandbox Demo</div>
            {config.allowBlindUnmatchedCredit ? (
              <div className="demo-chip chip-credit">Blind Credit On</div>
            ) : (
              <div className="demo-chip chip-muted">Blind Credit Off</div>
            )}
            <button type="button" className="btn btn-ghost" onClick={signOut}>
              Sign out
            </button>
          </div>
        </div>

        <nav className="tabs" aria-label="Terminal sections">
          {TABS.map((t) => (
            <button
              key={t.id}
              type="button"
              className={`tab ${tab === t.id ? 'active' : ''}`}
              onClick={() => {
                setTab(t.id)
                setNotifications([])
              }}
            >
              {t.label}
            </button>
          ))}
        </nav>

        <main className="panel">
          {notifications.length > 0 && (
            <div className="alerts">
              {notifications.map((n) => (
                <div className={`alert ${n.type}`} key={n.id} role="status">
                  <span>{n.message}</span>
                  <button type="button" aria-label="Dismiss" onClick={() => closeNote(n.id)}>
                    ×
                  </button>
                </div>
              ))}
            </div>
          )}

          {tab === 'payment' && (
            <PaymentTab
              config={config}
              responses={payments}
              setResponses={setPayments}
              notify={notify}
              setBusy={setBusy}
            />
          )}
          {tab === 'blind-credit' && (
            <BlindCreditTab
              config={config}
              responses={payments}
              setResponses={setPayments}
              notify={notify}
              setBusy={setBusy}
            />
          )}
          {tab === 'recurring' && (
            <RecurringTab
              config={config}
              accounts={recurring}
              setAccounts={setRecurring}
              notify={notify}
              setBusy={setBusy}
            />
          )}
          {tab === 'gift' && (
            <GiftTab
              config={config}
              responses={gift}
              setResponses={setGift}
              notify={notify}
              setBusy={setBusy}
            />
          )}
          {tab === 'reports' && (
            <ReportsTab config={config} payments={payments} gift={gift} />
          )}
          {tab === 'configure' && (
            <ConfigureTab config={config} setConfig={setConfig} notify={notify} />
          )}
        </main>
      </div>

      <p className="footer-note">
        CornerPay.NET Virtual Terminal sandbox — PayTrace / portal.dcap style with blind
        unmatched credit entitlement. Payment · Blind Credit · Recurring · Gift · Reports ·
        Configure. Demo only; no live card processing.
      </p>

      {busy && (
        <div className="overlay" aria-live="polite">
          <div className="progress-card">
            <h5 style={{ margin: 0 }}>Please wait while we process your request</h5>
            <div className="spinner" />
          </div>
        </div>
      )}
    </div>
  )
}
