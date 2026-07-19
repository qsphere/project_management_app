"""Footer for Settings and related pages."""
from __future__ import annotations

import streamlit as st

from constants.links import GITHUB_URL, PRIVACY_POLICY_URL


def render_page_footer() -> None:
    st.markdown(
        f"""
        <div class="app-footer">
          <span>© 2026 Initiative Dashboard</span>
          <span class="app-footer-links">
            <a href="{PRIVACY_POLICY_URL}" target="_blank" rel="noopener">Privacy Policy</a>
            <a href="{GITHUB_URL}" target="_blank" rel="noopener">
              <span class="app-footer-gh">GitHub</span>
            </a>
          </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
