import { useMemo, useState } from 'react'
import type {
  EntryMode,
  MerchantConfig,
  PaymentResponse,
  SaleType,
  TranType,
} from '../types'
import { processPayment } from '../lib/processor'
import { savePayments } from '../lib/storage'
import { ReceiptModal } from './ReceiptModal'

interface Props {
  config: MerchantConfig
  responses: PaymentResponse[]
  setResponses: (items: PaymentResponse[]) => void
  notify: (type: 'success' | 'error' | 'info', message: string) => void
  setBusy: (busy: boolean) => void
}

export function PaymentTab({
  config,
  responses,
  setResponses,
  notify,
  setBusy,
}: Props) {
  const configured = Boolean(config.secret)
  const [saleType, setSaleType] = useState<SaleType>('Credit')
  const [mode, setMode] = useState<EntryMode>('Manual')
  const [tranType, setTranType] = useState<TranType>('Sale')
  const [amount, setAmount] = useState('')
  const [account, setAccount] = useState('')
  const [expiration, setExpiration] = useState('')
  const [cvv, setCvv] = useState('')
  const [zip, setZip] = useState('')
  const [token, setToken] = useState('')
  const [receipt, setReceipt] = useState<PaymentResponse | null>(null)

  const showEntryMode = true

  const cols = useMemo(() => (showEntryMode ? 'three' : 'two'), [showEntryMode])

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!configured) return
    setBusy(true)
    const result = await processPayment({
      amount,
      account,
      saleType,
      tranType: saleType === 'Gift' ? 'Sale' : tranType,
      cvv,
      expiration,
      zip,
      token,
      mode,
    })
    setBusy(false)

    if (!result.ok) {
      notify('error', result.message)
      return
    }

    const next = [result.response, ...responses]
    setResponses(next)
    savePayments(next)
    notify('success', `Approved — Ref ${result.response.refNo}`)
    setAmount('')
    setAccount('')
    setExpiration('')
    setCvv('')
    setZip('')
    setToken('')
  }

  return (
    <div>
      <h2>One Time Payment</h2>
      <p className="lede">Run a single card-not-present transaction</p>

      {!configured && (
        <div className="notice">
          Configure a merchant secret on the Configure tab before processing.
        </div>
      )}

      <form onSubmit={onSubmit}>
        <div className={`grid ${cols}`}>
          <div className="field">
            <label>Sale Type</label>
            <select
              value={saleType}
              onChange={(e) => {
                const v = e.target.value as SaleType
                setSaleType(v)
                if (v === 'Gift') {
                  setTranType('Sale')
                  if (mode === 'Token') setMode('Manual')
                }
              }}
            >
              <option value="Credit">Credit</option>
              <option value="Gift">Gift</option>
            </select>
          </div>

          {showEntryMode && (
            <div className="field">
              <label>Entry Mode</label>
              <select
                value={mode}
                onChange={(e) => setMode(e.target.value as EntryMode)}
              >
                <option value="Manual">Manual</option>
                <option value="Swipe">Swipe</option>
                <option value="Token" disabled={saleType === 'Gift'}>
                  Token
                </option>
              </select>
            </div>
          )}

          <div className={`field ${saleType !== 'Credit' ? 'disabled' : ''}`}>
            <label>Transaction Type</label>
            <select
              value={tranType}
              onChange={(e) => setTranType(e.target.value as TranType)}
              disabled={saleType !== 'Credit'}
            >
              <option value="Sale">Sale</option>
              <option value="Return">Return</option>
            </select>
          </div>
        </div>

        <div className="grid" style={{ marginTop: 12 }}>
          <div className="amount-wrap">
            <div className="field amount">
              <label>Amount</label>
              <input
                inputMode="decimal"
                placeholder="0.00"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                required
              />
            </div>
          </div>
        </div>

        {mode === 'Manual' && (
          <div className="grid two" style={{ marginTop: 12 }}>
            <div className="field">
              <label>Card Number</label>
              <input
                placeholder="################"
                value={account}
                onChange={(e) => setAccount(e.target.value)}
                required
              />
            </div>
            <div className={`field ${saleType === 'Gift' ? 'disabled' : ''}`}>
              <label>Expiration Date</label>
              <input
                placeholder="1231"
                value={expiration}
                onChange={(e) => setExpiration(e.target.value)}
                disabled={saleType === 'Gift'}
              />
            </div>
          </div>
        )}

        {mode === 'Swipe' && (
          <div className="grid" style={{ marginTop: 12 }}>
            <div className="field">
              <label>Account Details (demo swipe)</label>
              <input
                placeholder="Paste track data or card number"
                value={account}
                onChange={(e) => setAccount(e.target.value)}
                required
              />
            </div>
          </div>
        )}

        {mode === 'Token' && (
          <div className="grid" style={{ marginTop: 12 }}>
            <div className="field">
              <label>Token</label>
              <input
                placeholder="T0K3N"
                value={token}
                onChange={(e) => setToken(e.target.value)}
                required
              />
            </div>
          </div>
        )}

        <div className="grid two" style={{ marginTop: 12 }}>
          <div className="field">
            <label>CVV</label>
            <input
              placeholder="###"
              value={cvv}
              onChange={(e) => setCvv(e.target.value)}
            />
          </div>
          <div className={`field ${saleType === 'Gift' ? 'disabled' : ''}`}>
            <label>Zip</label>
            <input
              placeholder="#####"
              value={zip}
              onChange={(e) => setZip(e.target.value)}
              disabled={saleType === 'Gift'}
            />
          </div>
        </div>

        <button className="btn btn-primary" type="submit" disabled={!configured}>
          Process Transaction
        </button>
        <p className="hint">
          Demo tip: use any 16-digit card (e.g. 4111111111111111). Cards ending in 0000 decline.
        </p>
      </form>

      {responses.length > 0 && (
        <>
          <h3 className="section-title">Responses</h3>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Account</th>
                  <th>Amount</th>
                  <th>Brand</th>
                  <th>RefNo</th>
                  <th>Receipt</th>
                </tr>
              </thead>
              <tbody>
                {responses.map((r) => (
                  <tr key={r.id}>
                    <td className="mono">{r.account}</td>
                    <td className="mono">${r.amount}</td>
                    <td>{r.brand}</td>
                    <td className="mono">{r.refNo}</td>
                    <td>
                      <button
                        type="button"
                        className="btn btn-sm"
                        onClick={() => setReceipt(r)}
                      >
                        {r.tranType} Receipt
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      <ReceiptModal
        open={Boolean(receipt)}
        onClose={() => setReceipt(null)}
        config={config}
        response={receipt}
      />
    </div>
  )
}
