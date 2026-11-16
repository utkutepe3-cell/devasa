import { useState } from 'react'
import type { GiftOp, MerchantConfig, PaymentResponse } from '../types'
import { processGift } from '../lib/processor'
import { saveGiftResponses } from '../lib/storage'
import { ReceiptModal } from './ReceiptModal'

interface Props {
  config: MerchantConfig
  responses: PaymentResponse[]
  setResponses: (items: PaymentResponse[]) => void
  notify: (type: 'success' | 'error' | 'info', message: string) => void
  setBusy: (busy: boolean) => void
}

export function GiftTab({
  config,
  responses,
  setResponses,
  notify,
  setBusy,
}: Props) {
  const configured = Boolean(config.secret)
  const [op, setOp] = useState<GiftOp>('Sale')
  const [amount, setAmount] = useState('')
  const [account, setAccount] = useState('')
  const [cvv, setCvv] = useState('')
  const [receipt, setReceipt] = useState<PaymentResponse | null>(null)

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!configured) {
      notify('error', 'Configure the terminal before gift operations.')
      return
    }
    setBusy(true)
    try {
      const result = await processGift({ op, amount, account, cvv })
      if (!result.ok) {
        notify('error', result.message)
        return
      }

      if (op === 'Balance') {
        notify('info', `Gift balance: $${result.response.balance}`)
        return
      }

      const next = [result.response, ...responses]
      setResponses(next)
      saveGiftResponses(next)
      notify('success', `${op} approved — Ref ${result.response.refNo}`)
      setAmount('')
      setAccount('')
      setCvv('')
    } catch (err) {
      notify('error', err instanceof Error ? err.message : 'Gift processing failed.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div>
      <h2>Gift Card</h2>
      <p className="lede">Run transactions, load value, and check balances</p>

      {!configured && (
        <div className="notice">Configure the terminal before gift operations.</div>
      )}

      <div className="segment">
        {(['Sale', 'Load', 'Balance'] as GiftOp[]).map((item) => (
          <button
            key={item}
            type="button"
            className={op === item ? 'active' : ''}
            onClick={() => setOp(item)}
          >
            {item}
          </button>
        ))}
      </div>

      <form onSubmit={onSubmit}>
        {op !== 'Balance' && (
          <div className="amount-wrap" style={{ marginBottom: 12 }}>
            <div className="field amount">
              <label>Amount</label>
              <input
                placeholder="0.00"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                required
              />
            </div>
          </div>
        )}

        <div className="grid two">
          <div className="field">
            <label>Gift Card Number</label>
            <input
              placeholder="################"
              value={account}
              onChange={(e) => setAccount(e.target.value)}
              required
            />
          </div>
          <div className="field">
            <label>CVV</label>
            <input
              placeholder="###"
              value={cvv}
              onChange={(e) => setCvv(e.target.value)}
            />
          </div>
        </div>

        <button className="btn btn-primary" type="submit" disabled={!configured}>
          Process
        </button>
      </form>

      {responses.length > 0 && (
        <>
          <h3 className="section-title">Responses</h3>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Account</th>
                  <th>Op</th>
                  <th>Amount</th>
                  <th>Balance</th>
                  <th>Receipt</th>
                </tr>
              </thead>
              <tbody>
                {responses.map((r) => (
                  <tr key={r.id}>
                    <td className="mono">{r.account}</td>
                    <td>{r.tranType}</td>
                    <td className="mono">${r.amount}</td>
                    <td className="mono">${r.balance ?? '—'}</td>
                    <td>
                      <button
                        type="button"
                        className="btn btn-sm"
                        onClick={() => setReceipt(r)}
                      >
                        Receipt
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
