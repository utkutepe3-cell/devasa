import type { MerchantConfig, PaymentResponse } from '../types'

interface Props {
  open: boolean
  onClose: () => void
  config: MerchantConfig
  response: PaymentResponse | null
}

export function ReceiptModal({ open, onClose, config, response }: Props) {
  if (!open || !response) return null

  const when = new Date(response.processedAt).toLocaleString()

  return (
    <div className="overlay" role="dialog" aria-modal="true" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="receipt" id="print-receipt">
          <div className="center">
            <div>*{config.merchantName || 'CornerPay Demo Merchant'}*</div>
            {config.merchantAddress1 && <div>{config.merchantAddress1}</div>}
            {config.merchantAddress2 && <div>{config.merchantAddress2}</div>}
            {config.merchantPhone && <div>{config.merchantPhone}</div>}
            <hr />
          </div>
          <div>{when}</div>
          <div>
            {response.brand === 'Gift'
              ? `GIFT ${String(response.tranType).toUpperCase()} $${response.amount}`
              : `CREDIT ${String(response.tranType).toUpperCase()} $${response.amount}`}
          </div>
          <div>{response.account} XX/XX</div>
          {response.balance && <div>BALANCE: ${response.balance}</div>}
          <div>APP: {response.authCode}</div>
          <div>REF: {response.refNo}</div>
          {response.brand !== 'Gift' && (
            <>
              <hr />
              <div>
                I AGREE TO PAY ABOVE TOTAL AMOUNT ACCORDING TO CARD ISSUER AGREEMENT
              </div>
              <div style={{ marginTop: 16 }}>X ________________</div>
            </>
          )}
        </div>
        <div className="modal-actions">
          <button className="btn btn-sm" type="button" onClick={() => window.print()}>
            Print
          </button>
          <button className="btn btn-danger" type="button" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  )
}
