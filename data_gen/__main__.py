"""
Regenerate the synthetic data files under data/.

Run with:
    uv run python -m data_gen
"""

from pathlib import Path

from data_gen.generate import N_WEEKS, SEED, generate_history
from thresholds import REQUIRED_COLUMNS

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
HISTORY_PATH = DATA_DIR / "pool_chemistry_history.csv"
TEMPLATE_PATH = DATA_DIR / "csv_upload_template.csv"


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)

    history = generate_history(n_weeks=N_WEEKS, seed=SEED)
    history.to_csv(HISTORY_PATH, index=False)
    print(f"Wrote {len(history)} rows ({N_WEEKS / 52:.1f} yrs) -> {HISTORY_PATH}")

    # Header-only template for users who want to upload their own readings.
    TEMPLATE_PATH.write_text(",".join(REQUIRED_COLUMNS) + "\n")
    print(f"Wrote upload template -> {TEMPLATE_PATH}")


if __name__ == "__main__":
    main()
