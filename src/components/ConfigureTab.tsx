import { useEffect, useMemo, useState } from 'react'
import type { MerchantConfig } from '../types'
import { createVirtualTerminal } from '../lib/gateway'
import { saveConfig } from '../lib/storage'

interface Props {
  config: MerchantConfig
  setConfig: (config: MerchantConfig) => void
  notify: (type: 'success' | 'error' | 'info', message: string) => void
}

export function ConfigureTab({ config, setConfig, notify }: Props) {
  const [draft, setDraft] = useState<MerchantConfig>(config)
  const [showSecret, setShowSecret] = useState(false)

  useEffect(() => {
    setDraft(config)
  }, [config])

  const gatewayPreview = useMemo(
    () =>
      createVirtualTerminal({
        merchantName: draft.merchantName || 'Demo Merchant',
        allowBlindUnmatchedCredit: draft.allowBlindUnmatchedCredit,
      }),
    [draft.merchantName, draft.allowBlindUnmatchedCredit],
  )

  function update<K extends keyof MerchantConfig>(key: K, value: MerchantConfig[K]) {
    setDraft((d) => ({ ...d, [key]: value }))
  }

  function onSave(e: React.FormEvent) {
    e.preventDefault()
    if (!draft.secret.trim()) {
      notify('error', 'Merchant secret is required.')
      return
    }
    if (!draft.merchantName.trim()) {
      notify('error', 'Merchant name is required.')
      return
    }
    const next = { ...draft, secret: draft.secret.trim() }
    setConfig(next)
    saveConfig(next)
    const vt = createVirtualTerminal({
      merchantName: next.merchantName,
      allowBlindUnmatchedCredit: next.allowBlindUnmatchedCredit,
    })
    notify('success', vt.message)
  }

  return (
    <div>
      <h2>Configuration</h2>
      <p className="lede">Enable your virtual terminal · PayTrace / portal.dcap style</p>
      <div className="notice">
        CornerPay sandbox only. Merchant secrets stay in browser localStorage and are never
        sent to CornerPay.NET or any live processor. Blind unmatched credit mirrors the
        standalone credit entitlement found on PayTrace VT and Datacap portal.dcap.
      </div>

      <form onSubmit={onSave}>
        <div className="grid">
          <div className="field">
            <label>Merchant Secret</label>
            <input
              type={showSecret ? 'text' : 'password'}
              placeholder="##############"
              value={draft.secret}
              onChange={(e) => update('secret', e.target.value)}
              required
            />
          </div>
        </div>
        <button
          type="button"
          className="btn btn-ghost"
          onClick={() => setShowSecret((s) => !s)}
        >
          {showSecret ? 'Hide secret' : 'Show secret'}
        </button>

        <div className="grid two" style={{ marginTop: 12 }}>
          <div className="field">
            <label>Merchant Name</label>
            <input
              value={draft.merchantName}
              onChange={(e) => update('merchantName', e.target.value)}
              required
            />
          </div>
          <div className="field">
            <label>Merchant Phone</label>
            <input
              placeholder="555-867-5309"
              value={draft.merchantPhone}
              onChange={(e) => update('merchantPhone', e.target.value)}
            />
          </div>
        </div>

        <div className="grid" style={{ marginTop: 12 }}>
          <div className="field">
            <label>Address Line 1</label>
            <input
              placeholder="123 Fake Street"
              value={draft.merchantAddress1}
              onChange={(e) => update('merchantAddress1', e.target.value)}
            />
          </div>
          <div className="field">
            <label>Address Line 2</label>
            <input
              placeholder="Suite 200"
              value={draft.merchantAddress2}
              onChange={(e) => update('merchantAddress2', e.target.value)}
            />
          </div>
        </div>

        <label className="check">
          <input
            type="checkbox"
            checked={draft.allowPartialAuth}
            onChange={(e) => update('allowPartialAuth', e.target.checked)}
          />
          Allow partial auth
        </label>

        <label className="check">
          <input
            type="checkbox"
            checked={draft.allowBlindUnmatchedCredit}
            onChange={(e) => update('allowBlindUnmatchedCredit', e.target.checked)}
          />
          Allow blind unmatched credit (no original sale RefNo)
        </label>

        <div className="gateway-card">
          <h3 className="section-title" style={{ marginTop: 8 }}>
            Gateway profile
          </h3>
          <dl className="gateway-meta">
            <div>
              <dt>Style</dt>
              <dd>PayTrace · portal.dcap</dd>
            </div>
            <div>
              <dt>VT ID</dt>
              <dd className="mono">{gatewayPreview.virtual_terminal.id}</dd>
            </div>
            <div>
              <dt>Blind unmatched credit</dt>
              <dd>
                {gatewayPreview.virtual_terminal.blind_unmatched_credit_status === 'enabled'
                  ? 'Enabled'
                  : 'Disabled'}
              </dd>
            </div>
            <div>
              <dt>Aliases</dt>
              <dd>
                {gatewayPreview.gateway.blind_unmatched_credit.aliases.slice(0, 4).join(', ')}
              </dd>
            </div>
          </dl>
        </div>

        <p className="hint">
          API URL: sandbox://cornerpay/vt · RPT URL: sandbox://cornerpay/reports · Receipt
          URL: local
        </p>

        <button className="btn btn-primary" type="submit">
          Save
        </button>
      </form>
    </div>
  )
}
