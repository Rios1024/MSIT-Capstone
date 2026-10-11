"""Charts for the evaluation report, drawn from the JSON files in results/.

Requires matplotlib.   Usage:  python eval/charts.py
"""
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "eval", "results")
sys.path.insert(0, os.path.join(ROOT, "eval"))
from browser_timing import key_latencies, replay  # noqa: E402

BLUE, ORANGE = "#2a78d6", "#eb6834"       # categorical slots 1 and 2
INK, SECONDARY, MUTED, GRID = "#0b0b0b", "#52514e", "#898781", "#e1e0d9"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": GRID,
    "axes.labelcolor": SECONDARY, "xtick.color": SECONDARY, "ytick.color": SECONDARY,
    "axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 200,
    "savefig.facecolor": "white", "axes.facecolor": "white",
})


def load(name):
    with open(os.path.join(RESULTS, name), encoding="utf-8") as handle:
        return json.load(handle)


def soften(ax):
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(length=0)
    ax.spines["left"].set_visible(False)


def placement():
    """Share of questions served at the simulated learner's own tier."""
    learners = load("simulation.json")["learners"]
    fig, ax = plt.subplots(figsize=(6.4, 3.5))
    width = 0.3
    for offset, version, colour, label in ((-0.16, "v0.2.0", BLUE, "v0.2.0 (prototype)"),
                                           (0.16, "current", ORANGE, "current rules (v0.3.0 onward)")):
        xs = [m + offset for m in (1, 2, 3)]
        values = [learners[str(m)][version]["on_target_pct"] for m in (1, 2, 3)]
        ax.bar(xs, values, width=width, color=colour, label=label)
        for x, value in zip(xs, values):
            ax.text(x, value + 1.5, f"{value:.1f}%", ha="center", va="bottom", color=INK, fontsize=9)
    ax.set_xticks([1, 2, 3], ["Tier 1 learner", "Tier 2 learner", "Tier 3 learner"])
    ax.set_ylim(0, 100)
    ax.set_yticks(range(0, 101, 25), [f"{v}%" for v in range(0, 101, 25)])
    ax.set_ylabel("Questions served at the learner's tier")
    ax.set_title("Simulated sessions: questions at the right tier", loc="left", color=INK, fontsize=11, pad=22)
    ax.legend(frameon=False, ncols=2, loc="lower left", bbox_to_anchor=(0, 1.0), fontsize=9,
              handlelength=1.2, borderaxespad=0.2)
    soften(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(RESULTS, "fig_placement.png"))
    plt.close(fig)


def latency():
    """Key press to updated display, every measured press."""
    data = load("browser_measurements.json")
    first = [ms for key, ms in key_latencies(data["session_1"]) if key in ("y", "n") and ms is not None]
    values = first + data["session_2_key_to_display_ms"]
    fig, ax = plt.subplots(figsize=(6.4, 3.2))
    ax.axhline(100, color=MUTED, linewidth=1)
    ax.text(len(values) + 0.4, 102, "0.1 s: feels instantaneous (Nielsen, 1993)", ha="right", va="bottom",
            color=SECONDARY, fontsize=9)
    ax.scatter(range(1, len(values) + 1), values, s=34, color=BLUE, edgecolor="white", linewidth=1.2, zorder=3)
    ax.axvline(len(first) + 0.5, color=GRID, linewidth=1)
    ax.text(len(first) / 2 + 0.5, 26, "session 1: scripted play", ha="center", color=SECONDARY, fontsize=9)
    ax.text(len(first) + len(data["session_2_key_to_display_ms"]) / 2 + 0.5, 26, "session 2: rapid keys",
            ha="center", color=SECONDARY, fontsize=9)
    ax.set_ylim(0, 120)
    ax.set_xlim(0, len(values) + 1)
    ax.set_xlabel("Key press (in order)")
    ax.set_ylabel("Milliseconds")
    ax.set_title("Key press to updated display in the CS Academy sandbox", loc="left", color=INK, fontsize=11)
    soften(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(RESULTS, "fig_latency.png"))
    plt.close(fig)


def session_tiers():
    """Tier after each answer in the recorded browser session."""
    rows = replay(load("browser_measurements.json")["session_1"])
    xs = [0] + [r["q"] for r in rows]
    tiers = [1] + [r["tier_after"] for r in rows]
    fig, ax = plt.subplots(figsize=(6.4, 3.2))
    ax.step(xs, tiers, where="post", color=BLUE, linewidth=2)
    ax.scatter(xs[1:], tiers[1:], s=40, color=BLUE, edgecolor="white", linewidth=1.4, zorder=3)
    notes = {4: ("streak of 3", 0.22), 8: ("1.3 s answer", 0.22), 9: ("23.7 s answer", -0.34),
             11: ("2 misses in a row", -0.34)}
    for r in rows:
        if r["q"] in notes:
            text, dy = notes[r["q"]]
            ax.text(r["q"], r["tier_after"] + dy, text, ha="center", color=INK, fontsize=9)
    ax.set_xticks(range(0, len(rows) + 1, 2))
    ax.set_yticks([1, 2, 3], ["Tier 1", "Tier 2", "Tier 3"])
    ax.set_ylim(0.5, 3.6)
    ax.set_xlim(-0.3, len(rows) + 0.6)
    ax.set_xlabel("Questions answered")
    ax.set_title("Difficulty tier during the recorded v0.4.1 system test session", loc="left", color=INK, fontsize=11)
    soften(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(RESULTS, "fig_session_tiers.png"))
    plt.close(fig)


if __name__ == "__main__":
    placement()
    latency()
    session_tiers()
    print("charts written to eval/results/")
