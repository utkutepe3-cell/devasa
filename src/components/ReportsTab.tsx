import { useMemo, useState } from 'react'
import type { MerchantConfig, PaymentResponse } from '../types'
import { sampleReportRows } from '../lib/processor'

interface Props {
  config: MerchantConfig
  payments: PaymentResponse[]
  gift: PaymentResponse[]
}

const REPORTS = [
  { id: 'TransactionHistory', label: 'Transaction History' },
  { id: 'DailySummary', label: 'Daily Summary' },
  { id: 'GiftActivity', label: 'Gift Activity' },
  { id: 'SampleBatch', label: 'Sample Batch Report' },
] as const

export function ReportsTab({ config, payments, gift }: Props) {
  const [selected, setSelected] = useState('')
  const [from, setFrom] = useState('')
  const [to, setTo] = useState('')
  const [rows, setRows] = useState<Record<string, string>[]>([])

  const configured = Boolean(config.secret)

  const liveRows = useMemo(() => {
    const all = [...payments, ...gift].map((p) => ({
      Date: new Date(p.processedAt).toLocaleString(),
      Type: String(p.tranType),
      Brand: p.brand,
      Amount: p.amount,
      RefNo: p.refNo,
      Status: 'Approved',
    }))
    return all
  }, [payments, gift])

  function refresh(e?: React.FormEvent) {
    e?.preventDefault()
    if (!selected) return

    if (selected === 'GiftActivity') {
      setRows(
        gift.map((p) => ({
          Date: new Date(p.processedAt).toLocaleString(),
          Op: String(p.tranType),
          Account: p.account,
          Amount: p.amount,
          Balance: p.balance ?? '',
          RefNo: p.refNo,
        })),
      )
      return
    }

    if (selected === 'DailySummary') {
      const source = liveRows.length ? liveRows : sampleReportRows()
      const total = source.reduce((sum, r) => sum + Number(r.Amount), 0)
      setRows([
        {
          Merchant: config.merchantName || 'Demo Merchant',
          Count: String(source.length),
          Total: total.toFixed(2),
          From: from || 'Today',
          To: to || 'Today',
        },
      ])
      return
    }

    if (selected === 'SampleBatch') {
      setRows(sampleReportRows())
      return
    }

    setRows(liveRows.length ? liveRows : sampleReportRows())
  }

  const headers = rows[0] ? Object.keys(rows[0]) : []

  return (
    <div>
      <h2>Reports{selected ? `: ${selected}` : ''}</h2>
      <p className="lede">Review sandbox transaction activity</p>

      {!configured && (
        <div className="notice">Configure the terminal to personalize report headers.</div>
      )}

      <div className="field" style={{ marginBottom: 12 }}>
        <label>Select a Report</label>
        <select
          value={selected}
          onChange={(e) => {
            setSelected(e.target.value)
            setRows([])
          }}
        >
          <option value="">Select a Report</option>
          {REPORTS.map((r) => (
            <option key={r.id} value={r.id}>
              {r.label}
            </option>
          ))}
        </select>
      </div>

      {selected && (
        <form onSubmit={refresh}>
          <div className="grid two">
            <div className="field">
              <label>From Date</label>
              <input type="date" value={from} onChange={(e) => setFrom(e.target.value)} />
            </div>
            <div className="field">
              <label>To Date</label>
              <input type="date" value={to} onChange={(e) => setTo(e.target.value)} />
            </div>
          </div>
          <button className="btn btn-primary" type="submit">
            Refresh
          </button>
        </form>
      )}

      {rows.length > 0 ? (
        <div className="table-wrap" style={{ marginTop: 16 }}>
          <table>
            <thead>
              <tr>
                {headers.map((h) => (
                  <th key={h}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row, i) => (
                <tr key={i}>
                  {headers.map((h) => (
                    <td key={h} className={h === 'Amount' || h === 'RefNo' ? 'mono' : undefined}>
                      {row[h]}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        selected && <div className="empty">Click Refresh to load report data.</div>
      )}
    </div>
  )
}
