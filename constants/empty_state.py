"""CSS for signed-in, no-connection empty states."""

NO_CONNECTION_CSS = """
<style>
  .nc-page-sub {
    color: #6b7280;
    font-size: 0.95rem;
    margin-top: -0.35rem;
    margin-bottom: 1.25rem;
  }
  .nc-inner {
    text-align: center;
    padding: 2.5rem 1.5rem 0.75rem;
  }
  .nc-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #111827;
    margin: 0 0 0.35rem;
  }
  .nc-body {
    color: #6b7280;
    font-size: 0.95rem;
    margin: 0 0 0.85rem;
  }
  .nc-body-only {
    font-weight: 500;
    margin: 0;
    padding: 1.75rem 0 1.25rem;
  }
  div[class*="st-key-nc_add_conn_"] button {
    background-color: #0052cc !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 0.5rem !important;
    font-weight: 600 !important;
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
</style>
"""
