"""Lifecycle status buckets and pie palette."""

# Fallback palette for generic name→count breakdowns (non-lifecycle).
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

LIFECYCLE_OPEN = "OPEN"
LIFECYCLE_CLOSED = "CLOSED"
LIFECYCLE_ARCHIVED = "ARCHIVED"

LIFECYCLE_ORDER = (LIFECYCLE_OPEN, LIFECYCLE_CLOSED, LIFECYCLE_ARCHIVED)
LIFECYCLE_COLORS = {
    LIFECYCLE_OPEN: "#7DD3FC",
    LIFECYCLE_CLOSED: "#34D399",
    LIFECYCLE_ARCHIVED: "#9CA3AF",
}
