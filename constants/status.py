"""Status buckets, list palette, and list-name heuristics."""

import re

# Fallback palette when pie slices are board list names (not fixed status buckets).
LIST_PALETTE = (
    "#7DD3FC",
    "#FB923C",
    "#34D399",
    "#F87171",
    "#A78BFA",
    "#FBBF24",
    "#2DD4BF",
    "#F472B6",
    "#60A5FA",
    "#9CA3AF",
    "#C084FC",
    "#4ADE80",
)

# Kept for classify_list_status / burndown completion heuristics.
STATUS_ORDER = ("To Do", "In Progress", "Done", "Blocked", "Archived")
STATUS_COLORS = {
    "To Do": "#7DD3FC",
    "In Progress": "#FB923C",
    "Done": "#34D399",
    "Blocked": "#F87171",
    "Archived": "#9CA3AF",
}

DONE_RE = re.compile(
    r"\b(done|complete|completed|closed|shipped|finished|fatto)\b", re.I
)
BLOCKED_RE = re.compile(r"\b(block|blocked|waiting|on hold|stuck)\b", re.I)
PROGRESS_RE = re.compile(
    r"\b(progress|doing|wip|active|review|qa|testing|in progress)\b", re.I
)
ARCHIVE_RE = re.compile(r"\b(archive|archived)\b", re.I)
