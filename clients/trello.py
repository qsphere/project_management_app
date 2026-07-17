"""Trello REST client — sole external HTTP surface for this app."""

from __future__ import annotations

from clients.http import TrelloHttp
from clients.trello_board import TrelloBoardMixin
from clients.trello_cards import TrelloCardsMixin
from clients.trello_labels import TrelloLabelsMixin


class TrelloClient(TrelloBoardMixin, TrelloLabelsMixin, TrelloCardsMixin, TrelloHttp):
    """All Trello calls go through this client (``_get`` / ``_post`` / ``_put`` / ``_delete``)."""


__all__ = ["TrelloClient"]
