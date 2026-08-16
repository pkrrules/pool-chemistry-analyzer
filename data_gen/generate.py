"""
Synthetic pool-chemistry history generator.

Produces one weekly reading per row for a single pool over a configurable
span (default: 260 weeks = 5 years). Unlike a naive "random value per row"
generator, each parameter is simulated as a mean-reverting random walk so
that consecutive weeks drift plausibly instead of jumping around — plus a
few real-world patterns layered on top:

- Water temperature follows a seasonal cycle (warmer -> more chlorine
  demand), which nudges Free Chlorine's target down in summer.
- A handful of random "neglect stretches" (3-6 weeks) push chlorine down,
  combined chlorine and pH up, and phosphates up — simulating a pool owner
  skipping maintenance for a while.
- Cyanuric Acid and Calcium Hardness only ever go up on their own (nothing
  chemical lowers them); periodic "partial drain & refill" events reset
  them back down, matching how these are actually managed.
- Phosphates occasionally get a "treatment event" (phosphate remover) that
  snaps a high reading back down.

Every band referenced here comes from thresholds.py, so the generator and
the UI never disagree about what a "target"/"neglected" value looks like.
"""

from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pandas as pd

from thresholds import DATE_COLUMN, PARAMETERS, get_parameter

SEED = 42
N_WEEKS = 260  # 5 years of weekly readings


def _mean_reverting_walk(
    rng: np.random.Generator,
    n: int,
    target: np.ndarray,
    sigma: float,
    theta: float,
    x0: float,
    lo: float,
    hi: float,
) -> np.ndarray:
    """AR(1)-style walk: x[t] = x[t-1] + theta*(target[t]-x[t-1]) + noise."""
    x = np.empty(n)
    x[0] = x0
    for t in range(1, n):
        x[t] = x[t - 1] + theta * (target[t] - x[t - 1]) + rng.normal(0, sigma)
    return np.clip(x, lo, hi)


def _neglect_windows(rng: np.random.Generator, n: int) -> np.ndarray:
    """Boolean mask marking a handful of random 3-6 week neglect stretches."""
    mask = np.zeros(n, dtype=bool)
    n_stretches = rng.integers(6, 10)
    for _ in range(n_stretches):
        start = rng.integers(0, max(n - 6, 1))
        length = rng.integers(3, 7)
        mask[start : start + length] = True
    return mask


def _drain_events(rng: np.random.Generator, n: int, min_gap: int = 52, max_gap: int = 90) -> np.ndarray:
    """Boolean mask marking weeks where a partial drain & refill happens."""
    mask = np.zeros(n, dtype=bool)
    week = int(rng.integers(min_gap, max_gap))
    while week < n:
        mask[week] = True
        week += int(rng.integers(min_gap, max_gap))
    return mask


def generate_history(
    n_weeks: int = N_WEEKS,
    seed: int = SEED,
    end_date: date | None = None,
) -> pd.DataFrame:
    """Return a DataFrame of `n_weeks` synthetic weekly readings, oldest first."""
    rng = np.random.default_rng(seed)
    end_date = end_date or date.today()
    start_date = end_date - timedelta(weeks=n_weeks - 1)
    dates = [start_date + timedelta(weeks=i) for i in range(n_weeks)]
    day_of_year = np.array([d.timetuple().tm_yday for d in dates])

    neglect = _neglect_windows(rng, n_weeks)

    # ── Water temperature: seasonal sine wave, peak mid-summer ────────────
    seasonal = np.sin(2 * np.pi * (day_of_year / 365.25 - 0.38))
    water_temp = 78 + 13 * seasonal + rng.normal(0, 2, n_weeks)
    water_temp = np.clip(water_temp, 60, 95)

    # ── Free Chlorine: mean-reverts to green band center, dips in neglect,
    #    target dips slightly further in hot weather (higher demand) ──────
    fc_param = get_parameter("Free_Chlorine_ppm")
    fc_target = np.full(n_weeks, sum(fc_param.green) / 2)
    fc_target -= 0.02 * np.clip(water_temp - 78, 0, None)  # hotter -> lower target
    fc_target[neglect] = 0.6
    free_chlorine = _mean_reverting_walk(
        rng, n_weeks, fc_target, sigma=0.45, theta=0.35, x0=fc_target[0], lo=0.0, hi=12.0
    )

    # ── Combined Chlorine: low baseline, builds up (chloramines) when
    #    neglected — Total = Free + Combined ────────────────────────────
    cc_param = get_parameter("Combined_Chlorine_ppm")
    cc_target = np.full(n_weeks, cc_param.green[1] * 0.4)
    cc_target[neglect] = 1.3
    combined_chlorine = _mean_reverting_walk(
        rng, n_weeks, cc_target, sigma=0.12, theta=0.30, x0=cc_target[0], lo=0.0, hi=3.0
    )

    # ── pH: mean-reverts to green center, drifts up when neglected ────────
    ph_param = get_parameter("pH")
    ph_target = np.full(n_weeks, sum(ph_param.green) / 2)
    ph_target[neglect] = 7.9
    ph = _mean_reverting_walk(
        rng, n_weeks, ph_target, sigma=0.06, theta=0.25, x0=ph_target[0], lo=6.2, hi=8.4
    )

    # ── Cyanuric Acid: only ever creeps UP (stabilized chlorine adds it),
    #    reset down by periodic partial drains ───────────────────────────
    cya = np.empty(n_weeks)
    cya[0] = 38.0
    drains_cya = _drain_events(rng, n_weeks, 60, 100)
    for t in range(1, n_weeks):
        cya[t] = cya[t - 1] + rng.normal(0.25, 0.15)
        if drains_cya[t]:
            cya[t] *= 0.55
    cya = np.clip(cya, 0, 180)

    # ── Calcium Hardness: slow upward creep (evaporation/fill water),
    #    reset down by the same style of periodic drain ───────────────────
    calcium = np.empty(n_weeks)
    calcium[0] = 280.0
    drains_ch = _drain_events(rng, n_weeks, 45, 85)
    for t in range(1, n_weeks):
        calcium[t] = calcium[t - 1] + rng.normal(1.2, 1.0)
        if drains_ch[t]:
            calcium[t] *= 0.65
    calcium = np.clip(calcium, 50, 650)

    # ── Phosphates: mean-reverts low, spikes during neglect, occasionally
    #    "treated" (phosphate remover) which snaps a high reading down ────
    phos_target = np.full(n_weeks, 50.0)
    phos_target[neglect] = 650.0
    phosphates = np.empty(n_weeks)
    phosphates[0] = 40.0
    for t in range(1, n_weeks):
        phosphates[t] = phosphates[t - 1] + 0.35 * (phos_target[t] - phosphates[t - 1]) + rng.normal(0, 35)
        if phosphates[t] > 400 and rng.random() < 0.35:
            phosphates[t] *= 0.15  # phosphate remover applied
    phosphates = np.clip(phosphates, 0, 3200)

    df = pd.DataFrame(
        {
            DATE_COLUMN: dates,
            "Free_Chlorine_ppm": free_chlorine.round(1),
            "Combined_Chlorine_ppm": combined_chlorine.round(2),
            "pH": ph.round(2),
            "Cyanuric_Acid_ppm": cya.round(0).astype(int),
            "Calcium_Hardness_ppm": calcium.round(0).astype(int),
            "Phosphates_ppb": phosphates.round(0).astype(int),
            "Water_Temperature_F": water_temp.round(0).astype(int),
        }
    )

    # Sanity check against thresholds.py so the generator can't silently
    # drift out of sync with the bands the UI grades against.
    assert list(df.columns) == [DATE_COLUMN] + [p.key for p in PARAMETERS] + ["Water_Temperature_F"]

    return df
