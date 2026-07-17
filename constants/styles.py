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
  div.st-key-auth_header_manage_account button {
    background-color: #ffffff !important;
    color: #111827 !important;
    border: 1.5px solid #d1d5db !important;
    border-radius: 0.5rem !important;
    font-weight: 600 !important;
    box-shadow: none !important;
  }
  div.st-key-auth_header_sign_up button:hover,
  div.st-key-auth_header_manage_account button:hover {
    background-color: #f9fafb !important;
    border-color: #9ca3af !important;
  }
  /* Account modal action buttons */
  div.st-key-account_sign_out button {
    background-color: #ffffff !important;
    color: #111827 !important;
    border: 1.5px solid #d1d5db !important;
    border-radius: 0.5rem !important;
    font-weight: 600 !important;
    box-shadow: none !important;
  }
  div.st-key-account_delete_btn button {
    background-color: #ffffff !important;
    color: #dc2626 !important;
    border: 1.5px solid #d1d5db !important;
    border-radius: 0.5rem !important;
    font-weight: 600 !important;
    box-shadow: none !important;
  }
  div.st-key-account_delete_btn button:hover {
    background-color: #fef2f2 !important;
    border-color: #fca5a5 !important;
  }
</style>
"""

CONNECTIONS_CSS = """
<style>
  .connections-kicker {
    color: #6b7280;
    font-size: 0.95rem;
    margin-top: -0.35rem;
    margin-bottom: 1.25rem;
  }
  .connections-kicker a { color: #0052cc; text-decoration: none; font-weight: 600; }
  .connections-kicker a:hover { text-decoration: underline; }
  .conn-count {
    color: #374151;
    font-size: 0.95rem;
    font-weight: 600;
    margin: 0.25rem 0 0.85rem;
  }
  .conn-empty {
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    background: #f9fafb;
    color: #6b7280;
    font-weight: 600;
    text-align: center;
    padding: 2.75rem 1rem;
  }
  .conn-card-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #111827;
    margin: 0 0 0.35rem;
  }
  .conn-card-meta {
    color: #6b7280;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.02em;
    margin: 0;
  }
  .app-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    margin-top: 2.5rem;
    padding-top: 1rem;
    border-top: 1px solid #e5e7eb;
    color: #6b7280;
    font-size: 0.85rem;
  }
  .app-footer-links { display: flex; gap: 1.1rem; align-items: center; }
  .app-footer a { color: #4b5563; text-decoration: none; font-weight: 600; }
  .app-footer a:hover { color: #111827; }
  div[data-testid="stDialog"] label p {
    color: #6b7280 !important;
    font-size: 0.72rem !important;
    font-weight: 650 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
  }
  div.st-key-conn_add_btn button,
  div.st-key-conn_dialog_save button {
    background-color: #0052cc !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 0.5rem !important;
    font-weight: 600 !important;
  }
  div.st-key-conn_dialog_cancel button {
    background-color: #ffffff !important;
    color: #111827 !important;
    border: 1.5px solid #d1d5db !important;
    border-radius: 0.5rem !important;
    font-weight: 600 !important;
  }
  div[class*="st-key-conn_card_del_"] button {
    background-color: #ffffff !important;
    color: #dc2626 !important;
    border: 1.5px solid #fca5a5 !important;
    border-radius: 0.5rem !important;
    font-weight: 600 !important;
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