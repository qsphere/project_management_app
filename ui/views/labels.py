from __future__ import annotations

import streamlit as st

from ui.component.label_crud import render_label_crud
from ui.component.label_overview import render_label_overview
from clients import TrelloClient


def render_labels_page(client: TrelloClient) -> None:
    render_label_overview(client)
    render_label_crud(client)
