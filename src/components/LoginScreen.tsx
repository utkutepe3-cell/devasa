import { useState } from 'react'
import { saveSession } from '../lib/storage'

interface Props {
  onEnter: (username: string) => void
}

export function LoginScreen({ onEnter }: Props) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!username.trim() || !password.trim()) {
      setError('Enter a username and password for this sandbox.')
      return
    }
    // Demo only — any credentials unlock the local sandbox. Nothing is sent.
    const name = username.trim()
    saveSession(name)
    onEnter(name)
  }

  return (
    <div className="app-shell">
      <div className="login-shell">
        <div className="brand-row" style={{ marginBottom: 14 }}>
          <div />
          <div className="demo-chip">Sandbox Demo</div>
        </div>

        <div className="login-card">
          <img
            className="brand-logo"
            src="/cornerpay-logo.png"
            alt="CornerPay"
            width={250}
            height={38}
          />
          <h1>
            CornerPay<em>.NET</em>
          </h1>
          <p className="lede">
            Welcome to the CornerPay Virtual Terminal sandbox — Datacap-style payment
            flow for demos only.
          </p>

          <div className="notice" style={{ textAlign: 'left' }}>
            Not the live Cornerstone portal. Credentials stay in your browser and are
            never submitted to CornerPay.NET.
          </div>

          <form onSubmit={onSubmit}>
            {error && (
              <div className="alert error" style={{ marginBottom: 12 }}>
                <span>{error}</span>
                <span />
              </div>
            )}
            <div className="grid">
              <div className="field">
                <label>Username</label>
                <input
                  autoComplete="username"
                  placeholder="demo-merchant"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                />
              </div>
              <div className="field">
                <label>Password</label>
                <input
                  type="password"
                  autoComplete="current-password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
            </div>
            <button className="btn btn-primary" type="submit">
              Enter Sandbox
            </button>
          </form>

          <blockquote className="quote">
            Accept payments from anyone and anywhere with less risk, more control, and
            lower rates.
          </blockquote>
        </div>

        <p className="footer-note">
          Inspired by Cornerstone Merchant Services CornerPay.NET · UI patterned after
          Datacap Virtual Terminal tabs · Demo only
        </p>
      </div>
    </div>
  )
}
