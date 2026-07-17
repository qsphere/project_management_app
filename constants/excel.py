"""Excel column aliases and template headers."""

COLUMN_ALIASES = {
    "name": {"name", "title", "task", "card", "card_name"},
    "description": {"description", "desc", "details", "body"},
    "list": {"list", "list_name", "column", "status"},
    "labels": {"labels", "label", "tags", "tag"},
    "assignee": {
        "assignee",
        "assignees",
        "member",
        "members",
        "assigned_to",
        "assign",
    },
    "due": {"due", "due_date", "deadline", "date"},
    "start": {"start", "start_date"},
    "pos": {"pos", "position"},
}

TEMPLATE_COLUMNS = (
    "Name",
    "Description",
    "List",
    "Labels",
    "Assignee",
    "Due",
    "Start",
    "Position",
)
