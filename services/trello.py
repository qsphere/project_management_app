"""Orchestration wrappers around ``clients.TrelloClient`` (no raw HTTP)."""

from __future__ import annotations

import time
from collections.abc import Callable

from clients import TrelloClient
from constants.taxonomy import UNMAPPED_SHOW
from functions.initiative_dashboard import build_initiative_dashboard
from functions.label_dashboard import build_label_dashboard

ProgressCallback = Callable[[int, int, str], None]


def connected_client(
    api_key: str, token: str, board_id: str
) -> TrelloClient | None:
    if not (api_key and token and board_id):
        return None
    return TrelloClient(api_key, token, board_id)


def load_initiative_dashboard(
    client: TrelloClient,
    *,
    lifecycle_filter: set[str] | None = None,
    group_dimension_key: str | None = None,
    taxonomy_mappings: list | None = None,
    taxonomy_filters: dict[str, set[str]] | None = None,
    unmapped_policy: str = UNMAPPED_SHOW,
    board_name: str | None = None,
) -> dict:
    labels = client.board_labels()
    cards = client.board_cards_dashboard()
    lists = client.open_lists()
    return build_initiative_dashboard(
        labels,
        cards,
        lists,
        lifecycle_filter=lifecycle_filter,
        group_dimension_key=group_dimension_key,
        taxonomy_mappings=taxonomy_mappings,
        taxonomy_filters=taxonomy_filters,
        unmapped_policy=unmapped_policy,
        board_name=board_name,
    )


def load_label_dashboard(client: TrelloClient) -> tuple[list[dict], list[dict], list[dict]]:
    labels = client.board_labels()
    cards = client.board_cards()
    lists = client.open_lists()
    return labels, cards, lists


def label_dashboard_rows(
    labels: list[dict], cards: list[dict], lists: list[dict]
) -> list[dict]:
    return build_label_dashboard(labels, cards, lists)


def load_board_labels(client: TrelloClient) -> list[dict]:
    return client.board_labels()


def create_label(client: TrelloClient, name: str, color: str | None) -> dict:
    return client.create_label(name, color)


def update_label(
    client: TrelloClient, label_id: str, *, name: str, color: str
) -> dict:
    return client.update_label(label_id, name=name, color=color)


def delete_label(client: TrelloClient, label_id: str) -> None:
    client.delete_label(label_id)


def load_cards_manage(
    client: TrelloClient,
) -> tuple[list[dict], list[dict], list[dict]]:
    cards = client.board_cards_manage()
    board_labels = client.board_labels()
    board_members = client.board_members()
    return cards, board_labels, board_members


def delete_cards(
    client: TrelloClient,
    cards: list[dict],
    *,
    delay: float,
    on_progress: ProgressCallback | None = None,
) -> int:
    """
    Delete cards sequentially. Returns the number deleted.

    ``on_progress(done, total, message)`` is called around each delete when set.
    """
    total = len(cards)
    deleted = 0
    for done, card in enumerate(cards, start=1):
        name = str(card.get("name") or card["id"])
        if on_progress is not None:
            on_progress(done - 1, total, f"Deleting {done}/{total}: {name}")
        client.delete_card(card["id"])
        deleted += 1
        if on_progress is not None:
            on_progress(done, total, f"Deleted {done}/{total}: {name}")
        if delay > 0 and done < total:
            time.sleep(delay)
    return deleted


def update_card(client: TrelloClient, card_id: str, **kwargs) -> dict:
    return client.update_card(card_id, **kwargs)


def delete_card(client: TrelloClient, card_id: str) -> None:
    client.delete_card(card_id)
