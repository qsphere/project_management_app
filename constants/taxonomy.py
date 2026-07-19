"""Taxonomy dimensions, Trello source fields, and unmapped policies."""

from __future__ import annotations

SOURCE_TYPE_CARDS = "cards"
SOURCE_TYPE_LISTS = "lists"
SOURCE_TYPE_LABELS = "labels"
SOURCE_TYPE_BOARDS = "boards"
SOURCE_TYPES = (
    SOURCE_TYPE_CARDS,
    SOURCE_TYPE_LISTS,
    SOURCE_TYPE_LABELS,
    SOURCE_TYPE_BOARDS,
)
SOURCE_TYPE_LABELS_UI = {
    SOURCE_TYPE_CARDS: "Cards",
    SOURCE_TYPE_LISTS: "Lists",
    SOURCE_TYPE_LABELS: "Labels",
    SOURCE_TYPE_BOARDS: "Boards",
}

# Backward-compatible aliases used by older helpers.
SOURCE_TYPE_LIST = SOURCE_TYPE_LISTS
SOURCE_TYPE_LABEL = SOURCE_TYPE_LABELS

UNMAPPED_SHOW = "show"
UNMAPPED_EXCLUDE = "exclude"
UNMAPPED_POLICIES = (UNMAPPED_SHOW, UNMAPPED_EXCLUDE)
UNMAPPED_LABEL = "Unmapped"

TAXONOMY_JSON_VERSION = 2

DIM_STATUS = "status"
DIM_FEATURE = "feature"
DIM_INITIATIVE = "initiative"

# Completion rollups keep ARCHIVED in numerator/denominator (FR3.6–FR3.8).
ROLLUP_DIMENSIONS = frozenset({DIM_FEATURE, DIM_INITIATIVE})

DEFAULT_DIMENSIONS: tuple[dict[str, str | bool], ...] = (
    {"dimension_key": DIM_FEATURE, "name": "Feature", "is_default": True},
    {"dimension_key": DIM_INITIATIVE, "name": "Initiative", "is_default": True},
    {"dimension_key": DIM_STATUS, "name": "Status", "is_default": True},
)

# One dimension → one Trello field (raw names become values).
DEFAULT_MAPPINGS: tuple[dict[str, str], ...] = (
    {"dimension_key": DIM_FEATURE, "source_type": SOURCE_TYPE_LABELS},
    {"dimension_key": DIM_INITIATIVE, "source_type": SOURCE_TYPE_LABELS},
    {"dimension_key": DIM_STATUS, "source_type": SOURCE_TYPE_LISTS},
)
