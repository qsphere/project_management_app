NAV_CSS = """
<style>
  div[data-testid="stButtonGroup"] button,
  div[data-testid="stButtonGroup"] [data-testid="stMarkdownContainer"] p,
  div[data-testid="stRadio"] label p {
    color: #111827 !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    opacity: 1 !important;
    visibility: visible !important;
  }
  /* Outlined auth header buttons — full border, white fill */
  div.st-key-auth_header_sign_up button,
  div.st-key-auth_header_sign_out button {
    background-color: #ffffff !important;
    color: #111827 !important;
    border: 1.5px solid #d1d5db !important;
    border-radius: 0.5rem !important;
    font-weight: 600 !important;
    box-shadow: none !important;
  }
  div.st-key-auth_header_sign_up button:hover,
  div.st-key-auth_header_sign_out button:hover {
    background-color: #f9fafb !important;
    border-color: #9ca3af !important;
  }
</style>
"""

DASHBOARD_CSS = """
<style>
  .block-container { padding-top: 3.5rem; padding-bottom: 2rem; }
  div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff;
    border: 1px solid #e8eaed;
    border-radius: 14px;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
  }
  .dash-kicker {
    color: #6b7280;
    font-size: 0.92rem;
    margin-top: -0.35rem;
    margin-bottom: 1.1rem;
  }
  .dash-asof {
    display: inline-block;
    background: #f3f4f6;
    color: #374151;
    font-size: 0.82rem;
    font-weight: 600;
    padding: 0.35rem 0.75rem;
    border-radius: 999px;
  }
  .dash-card-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #111827;
    margin: 0;
  }
  .dash-card-sub {
    color: #6b7280;
    font-size: 0.85rem;
    margin: 0.15rem 0 0.75rem;
  }
  .dash-badge {
    display: inline-block;
    font-size: 0.75rem;
    font-weight: 700;
    padding: 0.28rem 0.65rem;
    border-radius: 999px;
  }
  .dash-badge-ok { background: #d1fae5; color: #065f46; }
  .dash-badge-risk { background: #ffedd5; color: #9a3412; }
  .dash-status-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem;
    font-size: 0.88rem;
    margin: 0.22rem 0;
  }
  .dash-status-left {
    display: flex;
    align-items: center;
    gap: 0.45rem;
    color: #374151;
  }
  .dash-dot {
    width: 9px;
    height: 9px;
    border-radius: 50%;
    display: inline-block;
  }
  .dash-status-pct { color: #111827; font-weight: 700; }
  .dash-mini-label {
    color: #9ca3af;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    margin: 0.85rem 0 0.15rem;
  }
</style>
"""