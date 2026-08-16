"""
Shared chemistry thresholds — the single source of truth for what counts as
"good" (green), "watch" (yellow), or "bad / needs immediate attention" (red).

Both `data_gen/generate.py` (so synthetic history plausibly drifts around
real bands) and the `tabs/` UI modules (so cards and charts are colored
consistently) import from here. Nothing else should hardcode a chemistry
range — change a band once, and the generator and the UI both pick it up.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Parameter:
    """One tracked chemistry parameter and its green/yellow/red bands."""

    key: str  # column name in the CSV / DataFrame
    label: str  # human-readable name for display
    unit: str
    green: tuple[float, float]  # ideal range, inclusive
    yellow_low: tuple[float, float] | None  # low-side watch band, or None if N/A
    yellow_high: tuple[float, float] | None  # high-side watch band, or None if N/A
    # Anything below yellow_low[0] (or green[0] if no yellow_low) is red-low.
    # Anything above yellow_high[1] (or green[1] if no yellow_high) is red-high.


# Order here is display order across the whole app.
PARAMETERS: list[Parameter] = [
    Parameter(
        key="Free_Chlorine_ppm",
        label="Free Chlorine",
        unit="ppm",
        green=(3.0, 5.0),
        yellow_low=(1.0, 3.0),
        yellow_high=(5.0, 8.0),
    ),
    Parameter(
        key="Combined_Chlorine_ppm",
        label="Combined Chlorine",
        unit="ppm",
        green=(0.0, 0.5),
        yellow_low=None,
        yellow_high=(0.5, 1.0),
    ),
    Parameter(
        key="pH",
        label="pH",
        unit="",
        green=(7.4, 7.6),
        yellow_low=(7.2, 7.4),
        yellow_high=(7.6, 7.8),
    ),
    Parameter(
        key="Cyanuric_Acid_ppm",
        label="Cyanuric Acid (CYA)",
        unit="ppm",
        green=(30.0, 50.0),
        yellow_low=(10.0, 30.0),
        yellow_high=(50.0, 90.0),
    ),
    Parameter(
        key="Calcium_Hardness_ppm",
        label="Calcium Hardness",
        unit="ppm",
        green=(200.0, 400.0),
        yellow_low=(100.0, 200.0),
        yellow_high=(400.0, 500.0),
    ),
    Parameter(
        key="Phosphates_ppb",
        label="Phosphates",
        unit="ppb",
        green=(0.0, 100.0),
        yellow_low=None,
        yellow_high=(100.0, 500.0),
    ),
]

# Context-only column: shown in the UI but never color-graded.
CONTEXT_COLUMNS = ["Water_Temperature_F"]

DATE_COLUMN = "Date"

# All columns a valid history CSV must have (upload validation checks this).
REQUIRED_COLUMNS = [DATE_COLUMN] + [p.key for p in PARAMETERS] + CONTEXT_COLUMNS

STATUS_COLORS = {
    "green": "#0ca30c",
    "yellow": "#fab219",
    "red": "#d03b3b",
}

STATUS_LABELS = {
    "green": "Good",
    "yellow": "Watch",
    "red": "Needs attention",
}


def classify(param: Parameter, value: float) -> str:
    """Return 'green' | 'yellow' | 'red' for a single reading."""
    if value is None:
        return "red"

    g_lo, g_hi = param.green
    if g_lo <= value <= g_hi:
        return "green"

    if param.yellow_low and param.yellow_low[0] <= value < param.yellow_low[1]:
        return "yellow"
    if param.yellow_high and param.yellow_high[0] < value <= param.yellow_high[1]:
        return "yellow"

    return "red"


def get_parameter(key: str) -> Parameter:
    for p in PARAMETERS:
        if p.key == key:
            return p
    raise KeyError(f"Unknown parameter: {key}")
