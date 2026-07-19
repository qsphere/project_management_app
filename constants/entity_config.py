"""Default dashboard entity configurations (Initiative / Status)."""

from __future__ import annotations

MAPS_TO_LISTS = "Lists"
MAPS_TO_LABELS = "Labels"
MAPS_TO_OPTIONS = (MAPS_TO_LISTS, MAPS_TO_LABELS)

ENTITY_KEYS = ("initiative", "status")

# Domain default: labels = initiatives. Status pies use lifecycleStatus.
DEFAULT_ENTITY_CONFIGS: tuple[dict[str, str], ...] = (
    {
        "entity_key": "initiative",
        "name": "Initiative",
        "description": (
            "A top-level effort grouping related tasks toward a shared goal."
        ),
        "maps_to": MAPS_TO_LABELS,
    },
    {
        "entity_key": "status",
        "name": "Status",
        "description": (
            "Task lifecycle: OPEN, CLOSED, or ARCHIVED "
            "(from closed / dueComplete; recomputed on sync)."
        ),
        "maps_to": MAPS_TO_LISTS,
    },
)
