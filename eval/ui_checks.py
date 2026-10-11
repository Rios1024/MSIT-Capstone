"""Interface checks that support the usability review.

1. Text contrast of every label colour against its background (WCAG 2.2).
2. Rendered width of every prompt and correction against the 400-unit canvas.

Widths are measured with Liberation Sans, which has the same metrics as
Arial, the default CMU Graphics font. Requires Pillow.

Usage:  python eval/ui_checks.py
"""
import json
import os
import sys

from PIL import ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tests"))
from stubs import load_game  # noqa: E402

OUT = os.path.join(ROOT, "eval", "results", "ui_checks.json")
CANVAS_WIDTH = 400
FONT_PATHS = [
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "C:/Windows/Fonts/arial.ttf",
    "/Library/Fonts/Arial.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
]

# CSS colour names used in main.py
COLOURS = {
    "black": (0, 0, 0), "white": (255, 255, 255), "ghostWhite": (248, 248, 255),
    "slateGray": (112, 128, 144), "darkSlateGray": (47, 79, 79), "red": (255, 0, 0),
    "fireBrick": (178, 34, 34), "orange": (255, 165, 0), "sienna": (160, 82, 45),
    "midnightBlue": (25, 25, 112), "crimson": (220, 20, 60), "darkGreen": (0, 100, 0),
}

# (name shown in the report, variable in main.py); colours and sizes are read from the code
LABELS = [
    ("Tier", "tierLabel"), ("Time", "timeLabel"), ("Errors", "errorLabel"), ("Streak", "streakLabel"),
    ("Topic", "topicLabel"), ("Term", "termLabel"), ("Prompt", "promptLabel"),
    ("Correction", "feedbackLabel"), ("Instructions", "instrLabel"), ("Session timer", "globalTimerLabel"),
]


def luminance(rgb):
    def channel(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (channel(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(foreground, background):
    hi, lo = sorted((luminance(COLOURS[foreground]), luminance(COLOURS[background])), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def is_large(size_px, bold):
    """WCAG large text: 18 pt (24 px), or 14 pt (18.66 px) when bold."""
    return size_px >= 24 or (bold and size_px >= 18.66)


def find_font():
    for path in FONT_PATHS:
        if os.path.exists(path):
            return path
    raise SystemExit("No Arial-compatible font found; edit FONT_PATHS.")


def label_rows(game):
    """Text colour, background, size and weight of every label, read from main.py."""
    import stubs
    header_bar, header_title = stubs.CREATED[0], stubs.CREATED[1]
    rows = [("Header title", header_title.fill, header_bar.fill, header_title.size, header_title.bold)]
    for name, variable in LABELS:
        shape = getattr(game, variable)
        rows.append((name, shape.fill, game.app.background, shape.size, shape.bold))
    report = game.app.reportTotal
    rows.append(("Report text", report.fill, game.app.reportBg.fill, report.size, report.bold))
    return rows


def main():
    results = {"contrast": [], "overflow": {}}
    game = load_game(seed=1)
    rows = label_rows(game)

    print("1. Text contrast (WCAG 2.2 success criterion 1.4.3, level AA)")
    print("   label           colours                       size  ratio  needs  result")
    for name, fg, bg, size, bold in rows:
        ratio = contrast(fg, bg)
        needed = 3.0 if is_large(size, bold) else 4.5
        ok = ratio >= needed
        results["contrast"].append({"label": name, "text": fg, "background": bg, "size_px": size,
                                    "bold": bold, "ratio": round(ratio, 2), "required": needed, "pass": ok})
        weight = "bold" if bold else "    "
        print(f"   {name:14s}  {fg + ' on ' + bg:28s}  {size:>2d} {weight} {ratio:5.2f}  {needed:4.1f}   "
              f"{'pass' if ok else 'FAIL'}")
    failed = [c["label"] for c in results["contrast"] if not c["pass"]]
    print(f"   {len(rows) - len(failed)} of {len(rows)} labels pass; failing: {', '.join(failed) or 'none'}")

    font_path = find_font()
    wrap = getattr(game, "wrapPrompt", lambda text: (text, ""))
    print()
    print(f"2. Text width against the {CANVAS_WIDTH}-unit canvas ({os.path.basename(font_path)})")
    for field, size in (("prompt", 13), ("correction", 12)):
        font = ImageFont.truetype(font_path, size)
        rows = []
        for tier, pool in game.app.curriculum.items():
            for puzzle in pool:
                lines = [l for l in wrap(puzzle[field])] if field == "prompt" else [puzzle[field]]
                lines = [l for l in lines if l]
                rows.append((round(max(font.getlength(l) for l in lines), 1), tier, puzzle["term"], len(lines)))
        rows.sort(reverse=True)
        over = [r for r in rows if r[0] > CANVAS_WIDTH]
        two = sum(1 for r in rows if r[3] == 2)
        results["overflow"][field] = {"size_px": size, "total": len(rows), "wider_than_canvas": len(over),
                                      "shown_on_two_lines": two,
                                      "widest": [{"width": w, "tier": t, "term": term, "lines": n} for w, t, term, n in rows[:6]]}
        extra = f"; {two} are shown on two lines" if field == "prompt" else ""
        print(f"   {field}s at size {size}: {len(over)} of {len(rows)} are wider than the canvas{extra}")
        for width, tier, term, n in rows[:6]:
            flag = "CLIPPED" if width > CANVAS_WIDTH else "fits"
            print(f"     {width:6.1f}  Tier {tier}  {term:16s} {flag}  ({n} line{'s' if n > 1 else ''})")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as handle:
        json.dump(results, handle, indent=2)
    print()
    print(f"   results written to {os.path.relpath(OUT, ROOT)}")


if __name__ == "__main__":
    main()
