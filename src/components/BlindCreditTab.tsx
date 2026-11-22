import { useState } from 'react'
import type {
  BlindCreditReason,
  MerchantConfig,
  PaymentResponse,
} from '../types'
import { BLIND_CREDIT_REASONS } from '../types'
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

export function BlindCreditTab({
  config,
  responses,
  setResponses,
  notify,
  setBusy,
}: Props) {
  const configured = Boolean(config.secret)
  const enabled = config.allowBlindUnmatchedCredit
  const [amount, setAmount] = useState('')
  const [account, setAccount] = useState('')
  const [expiration, setExpiration] = useState('')
  const [cvv, setCvv] = useState('')
  const [zip, setZip] = useState('')
  const [reason, setReason] = useState<BlindCreditReason>('customer_request')
  const [reasonNote, setReasonNote] = useState('')
  const [confirmed, setConfirmed] = useState(false)
  const [receipt, setReceipt] = useState<PaymentResponse | null>(null)

  const blindCredits = responses.filter((r) => r.tranType === 'BlindCredit')

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!configured) {
      notify('error', 'Configure the terminal before processing credits.')
      return
    }
    if (!enabled) {
      notify(
        'error',
        'Blind unmatched credit is off. Turn it on under Configure (PayTrace / portal.dcap entitlement).',
      )
      return
    }
    if (!confirmed) {
      notify('error', 'Confirm authorization for this unmatched credit before submitting.')
      return
    }

    setBusy(true)
    try {
      const result = await processPayment({
        amount,
        account,
        saleType: 'Credit',
        tranType: 'BlindCredit',
        cvv,
        expiration,
        zip,
        mode: 'Manual',
        allowBlindUnmatchedCredit: enabled,
        reason,
        reasonNote: reasonNote.trim() || undefined,
      })

      if (!result.ok) {
        notify('error', result.message)
        return
      }

      const next = [result.response, ...responses]
      setResponses(next)
      savePayments(next)
      notify(
        'success',
        `Blind unmatched credit approved — Ref ${result.response.refNo}`,
      )
      setAmount('')
      setAccount('')
      setExpiration('')
      setCvv('')
      setZip('')
      setReasonNote('')
      setConfirmed(false)
      setReceipt(result.response)
    } catch (err) {
      notify('error', err instanceof Error ? err.message : 'Blind credit failed.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div>
      <h2>Blind Unmatched Credit</h2>
      <p className="lede">
        Standalone credit with no original sale — PayTrace / portal.dcap style
      </p>

      <div className="notice notice-credit">
        Issues a credit to the card without a matching transaction ID (also called
        unmatched refund, open credit, or independent credit). High-risk entitlement;
        keep audit reasons filled in for every demo run.
      </div>

      {!configured && (
        <div className="notice">
          Configure a merchant secret on the Configure tab before processing.
        </div>
      )}

      {!enabled && (
        <div className="notice notice-warn">
          Blind unmatched credit is <strong>disabled</strong> for this merchant profile.
          Enable “Allow blind unmatched credit” on Configure to use this tab.
        </div>
      )}

      <form onSubmit={onSubmit}>
        <div className="grid">
          <div className="amount-wrap">
            <div className="field amount">
              <label>Credit Amount</label>
              <input
                inputMode="decimal"
                placeholder="0.00"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                required
                disabled={!enabled}
              />
            </div>
          </div>
        </div>

        <div className="grid two" style={{ marginTop: 12 }}>
          <div className="field">
            <label>Card Number</label>
            <input
              placeholder="################"
              value={account}
              onChange={(e) => setAccount(e.target.value)}
              required
              disabled={!enabled}
            />
          </div>
          <div className="field">
            <label>Expiration (MMYY)</label>
            <input
              placeholder="1231"
              value={expiration}
              onChange={(e) => setExpiration(e.target.value)}
              required
              disabled={!enabled}
            />
          </div>
        </div>

        <div className="grid two" style={{ marginTop: 12 }}>
          <div className="field">
            <label>CVV</label>
            <input
              placeholder="###"
              value={cvv}
              onChange={(e) => setCvv(e.target.value)}
              disabled={!enabled}
            />
          </div>
          <div className="field">
            <label>Zip</label>
            <input
              placeholder="#####"
              value={zip}
              onChange={(e) => setZip(e.target.value)}
              disabled={!enabled}
            />
          </div>
        </div>

        <div className="grid two" style={{ marginTop: 12 }}>
          <div className="field">
            <label>Reason</label>
            <select
              value={reason}
              onChange={(e) => setReason(e.target.value as BlindCreditReason)}
              disabled={!enabled}
            >
              {BLIND_CREDIT_REASONS.map((r) => (
                <option key={r.value} value={r.value}>
                  {r.label}
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label>Notes (optional)</label>
            <input
              placeholder="Internal audit note"
              value={reasonNote}
              onChange={(e) => setReasonNote(e.target.value)}
              disabled={!enabled}
            />
          </div>
        </div>

        <label className="check" style={{ marginTop: 14 }}>
          <input
            type="checkbox"
            checked={confirmed}
            onChange={(e) => setConfirmed(e.target.checked)}
            disabled={!enabled}
          />
          I authorize this unmatched credit without an original sale reference
        </label>

        <button
          className="btn btn-primary"
          type="submit"
          disabled={!configured || !enabled}
        >
          Process Blind Credit
        </button>
        <p className="hint">
          Demo: 4111111111111111 · cards ending in 0000 decline · no live processor
          calls
        </p>
      </form>

      {blindCredits.length > 0 && (
        <>
          <h3 className="section-title">Blind credit responses</h3>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Account</th>
                  <th>Amount</th>
                  <th>Reason</th>
                  <th>RefNo</th>
                  <th>Receipt</th>
                </tr>
              </thead>
              <tbody>
                {blindCredits.map((r) => (
                  <tr key={r.id}>
                    <td className="mono">{r.account}</td>
                    <td className="mono">${r.amount}</td>
                    <td>{r.reason ?? '—'}</td>
                    <td className="mono">{r.refNo}</td>
                    <td>
                      <button
                        type="button"
                        className="btn btn-sm"
                        onClick={() => setReceipt(r)}
                      >
                        Credit Receipt
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
