"""CSS for the Labels page and label create/edit dialogs."""

LABELS_CSS = """
<style>
  .labels-kicker {
    color: #6b7280;
    font-size: 0.95rem;
    margin-top: -0.35rem;
    margin-bottom: 1.1rem;
  }
  .labels-metric-label {
    color: #6b7280;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin: 0 0 0.15rem;
  }
  .labels-metric-value {
    color: #111827;
    font-size: 1.85rem;
    font-weight: 700;
    line-height: 1.1;
    margin: 0 0 1.1rem;
  }
  .labels-row-name {
    display: flex;
    align-items: center;
    gap: 0.65rem;
    color: #111827;
    font-weight: 600;
  }
  .labels-swatch {
    width: 1.1rem;
    height: 1.1rem;
    border-radius: 0.3rem;
    border: 1px solid rgba(15, 23, 42, 0.12);
    flex-shrink: 0;
  }
  .labels-row-cards {
    color: #111827;
    font-weight: 600;
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
  div.st-key-labels_new_btn button,
  div.st-key-label_dialog_save button {
    background-color: #0052cc !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 0.5rem !important;
    font-weight: 600 !important;
  }
  div.st-key-label_dialog_cancel button {
    background-color: #ffffff !important;
    color: #111827 !important;
    border: 1.5px solid #d1d5db !important;
    border-radius: 0.5rem !important;
    font-weight: 600 !important;
  }
  div.st-key-label_dialog_delete button {
    background-color: #ffffff !important;
    color: #dc2626 !important;
    border: 1.5px solid #d1d5db !important;
    border-radius: 0.5rem !important;
    font-weight: 600 !important;
  }
  div[class*="st-key-label_edit_"] button,
  div[class*="st-key-label_del_"] button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: #6b7280 !important;
    min-height: 2rem !important;
    padding: 0.2rem 0.35rem !important;
  }
  div[class*="st-key-label_del_"] button { color: #dc2626 !important; }
  div.st-key-label_apps_info button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: #9ca3af !important;
    min-height: 1.5rem !important;
    padding: 0 !important;
  }
  div.st-key-label_apps_info button:hover { color: #6b7280 !important; }
</style>
"""
