from __future__ import annotations

from constants.status import ARCHIVE_RE, BLOCKED_RE, DONE_RE, PROGRESS_RE


def classify_list_status(list_name: str, *, closed: bool = False) -> str:
    """Map a Trello list name (and closed flag) to a dashboard status bucket."""
    if closed:
        return "Archived"
    name = (list_name or "").strip()
    if ARCHIVE_RE.search(name):
        return "Archived"
    if DONE_RE.search(name):
        return "Done"
    if BLOCKED_RE.search(name):
        return "Blocked"
    if PROGRESS_RE.search(name):
        return "In Progress"
    return "To Do"
