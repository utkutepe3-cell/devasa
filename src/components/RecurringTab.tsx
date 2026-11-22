import { useState } from 'react'
import type { MerchantConfig, RecurringAccount } from '../types'
import { formatAmount, processPayment } from '../lib/processor'
import { saveRecurring } from '../lib/storage'

interface Props {
  config: MerchantConfig
  accounts: RecurringAccount[]
  setAccounts: (items: RecurringAccount[]) => void
  notify: (type: 'success' | 'error' | 'info', message: string) => void
  setBusy: (busy: boolean) => void
}

export function RecurringTab({
  config,
  accounts,
  setAccounts,
  notify,
  setBusy,
}: Props) {
  const configured = Boolean(config.secret)
  const [mode, setMode] = useState<'list' | 'add'>('list')
  const [alias, setAlias] = useState('')
  const [amount, setAmount] = useState('')
  const [account, setAccount] = useState('')
  const [expiration, setExpiration] = useState('')
  const [cvv, setCvv] = useState('')

  async function addAccount(e: React.FormEvent) {
    e.preventDefault()
    if (!configured) return
    if (Number(formatAmount(amount)) <= 0) {
      notify('error', 'Recurring amount must be greater than zero.')
      return
    }
    setBusy(true)
    try {
      // Demo tokenization uses a $0.01 auth check
      const auth = await processPayment({
        amount: '0.01',
        account,
        saleType: 'Credit',
        tranType: 'Sale',
        expiration,
        cvv,
        mode: 'Manual',
      })

      if (!auth.ok) {
        notify('error', auth.message)
        return
      }
      finishAdd(auth.response.account, auth.response.refNo)
    } catch (err) {
      notify('error', err instanceof Error ? err.message : 'Could not add account.')
    } finally {
      setBusy(false)
    }
  }

  function finishAdd(masked: string, tokenSeed: string) {
    if (accounts.some((a) => a.alias.toLowerCase() === alias.toLowerCase())) {
      notify('error', `An account already exists for alias: ${alias}`)
      return
    }
    const next: RecurringAccount = {
      id: crypto.randomUUID(),
      alias,
      account: masked,
      amount: formatAmount(amount),
      token: `TOK${tokenSeed}`,
      lastProcessedDate: null,
      history: [],
    }
    const list = [next, ...accounts]
    setAccounts(list)
    saveRecurring(list)
    notify('success', `Added ${alias}`)
    setAlias('')
    setAmount('')
    setAccount('')
    setExpiration('')
    setCvv('')
    setMode('list')
  }

  async function charge(item: RecurringAccount) {
    setBusy(true)
    const result = await processPayment({
      amount: item.amount,
      account: item.account.replace(/\D/g, '') || '4111111111111111',
      saleType: 'Credit',
      tranType: 'Sale',
      token: item.token,
      mode: 'Token',
    })
    setBusy(false)
    if (!result.ok) {
      notify('error', result.message)
      return
    }
    const updated = accounts.map((a) =>
      a.id === item.id
        ? {
            ...a,
            lastProcessedDate: new Date().toISOString(),
            history: [
              {
                date: new Date().toLocaleString(),
                amount: result.response.amount,
                refNo: result.response.refNo,
                status: 'Approved',
              },
              ...a.history,
            ],
          }
        : a,
    )
    setAccounts(updated)
    saveRecurring(updated)
    notify('success', `Charged ${item.alias} — $${result.response.amount}`)
  }

  function remove(item: RecurringAccount) {
    if (!confirm(`Remove ${item.alias}?`)) return
    const updated = accounts.filter((a) => a.id !== item.id)
    setAccounts(updated)
    saveRecurring(updated)
    notify('info', `Removed ${item.alias}`)
  }

  return (
    <div>
      <h2>On-going Payments</h2>
      <p className="lede">Store cards and run recurring charges</p>

      {!configured && (
        <div className="notice">Configure the terminal before adding recurring accounts.</div>
      )}

      {mode === 'list' ? (
        <>
          <button
            type="button"
            className="btn btn-primary"
            style={{ marginTop: 0 }}
            disabled={!configured}
            onClick={() => setMode('add')}
          >
            Add Account
          </button>

          <div className="recurring-list" style={{ marginTop: 16 }}>
            {accounts.length === 0 && (
              <div className="empty">No recurring accounts yet.</div>
            )}
            {accounts.map((a) => (
              <div className="recurring-item" key={a.id}>
                <header>
                  <strong>{a.alias}</strong>
                  <span className="mono">${a.amount}</span>
                </header>
                <div className="meta mono">
                  {a.account} · {a.token}
                </div>
                <div className="meta">
                  Last charged:{' '}
                  {a.lastProcessedDate
                    ? new Date(a.lastProcessedDate).toLocaleString()
                    : 'Never'}
                </div>
                <div className="actions">
                  <button type="button" className="btn btn-sm" onClick={() => charge(a)}>
                    Charge Now
                  </button>
                  <button type="button" className="btn btn-danger" onClick={() => remove(a)}>
                    Remove
                  </button>
                </div>
              </div>
            ))}
          </div>
        </>
      ) : (
        <form onSubmit={addAccount}>
          <h3 className="section-title" style={{ marginTop: 0 }}>
            Add Account
          </h3>
          <div className="grid two">
            <div className="field">
              <label>Account Name</label>
              <input
                placeholder="John Doe"
                value={alias}
                onChange={(e) => setAlias(e.target.value)}
                required
              />
            </div>
            <div className="amount-wrap">
              <div className="field amount">
                <label>Recurring Amount</label>
                <input
                  placeholder="0.00"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  required
                />
              </div>
            </div>
          </div>
          <div className="grid two" style={{ marginTop: 12 }}>
            <div className="field">
              <label>Card Number</label>
              <input
                placeholder="0000000000000000"
                value={account}
                onChange={(e) => setAccount(e.target.value)}
                required
              />
            </div>
            <div className="field">
              <label>Expiration Date</label>
              <input
                placeholder="1231"
                value={expiration}
                onChange={(e) => setExpiration(e.target.value)}
                required
              />
            </div>
          </div>
          <div className="grid" style={{ marginTop: 12 }}>
            <div className="field">
              <label>CVV</label>
              <input
                placeholder="000"
                value={cvv}
                onChange={(e) => setCvv(e.target.value)}
              />
            </div>
          </div>
          <button className="btn btn-primary" type="submit">
            Authorize & Add
          </button>
          <button
            type="button"
            className="btn btn-ghost"
            style={{ display: 'block', marginTop: 8 }}
            onClick={() => setMode('list')}
          >
            Cancel
          </button>
        </form>
      )}
    </div>
  )
}
