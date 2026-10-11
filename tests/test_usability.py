"""Tests for the usability defects found in the Unit 6 evaluation (release v0.4.1).

Each test states a behaviour a student can see. Eleven of the 19 fail against
release v0.3.0 and all pass against v0.4.1, so they double as regression checks.
"""
import os

import pytest

from stubs import answer, wait, wrong_key

CANVAS_WIDTH = 400
LONG_PROMPT_TERMS = ["return", "while-loop", "if-elif-else", "conditional"]
FONT_PATHS = [
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",   # same metrics as Arial
    "C:/Windows/Fonts/arial.ttf",
    "/Library/Fonts/Arial.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
]
COLOURS = {
    "black": (0, 0, 0), "white": (255, 255, 255), "ghostWhite": (248, 248, 255),
    "slateGray": (112, 128, 144), "darkSlateGray": (47, 79, 79), "red": (255, 0, 0),
    "fireBrick": (178, 34, 34), "orange": (255, 165, 0), "sienna": (160, 82, 45),
    "midnightBlue": (25, 25, 112), "crimson": (220, 20, 60), "darkGreen": (0, 100, 0),
}


# ---- helpers ---------------------------------------------------------------

def prompt_lines(game):
    """The prompt as the student sees it: one label, or two when it is wrapped."""
    lines = [game.promptLabel.value]
    second = getattr(game, "promptLabel2", None)
    if second is not None and second.value:
        lines.append(second.value)
    return lines


def show_term(game, term):
    """Put a chosen term on screen through the normal loading path."""
    app = game.app
    for tier, pool in app.curriculum.items():
        if any(p["term"] == term for p in pool):
            app.difficulty = tier
    for _ in range(500):
        game.loadScenario()
        if app.lastTerm == term:
            return
    raise AssertionError(f"term {term!r} never appeared")


def contrast(foreground, background):
    def luminance(rgb):
        channels = []
        for c in rgb:
            c = c / 255.0
            channels.append(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4)
        return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]
    hi, lo = sorted((luminance(COLOURS[foreground]), luminance(COLOURS[background])), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def header_fill(game):
    """Fill colour of the header bar, the first Rect that main.py draws."""
    import stubs
    return stubs.CREATED[0].fill if getattr(stubs, "CREATED", None) else None


# ---- defect 1: long prompts were clipped at both edges of the canvas -------

@pytest.mark.parametrize("term", LONG_PROMPT_TERMS)
def test_long_prompt_is_shown_in_full_on_two_lines(game, term):
    show_term(game, term)
    entry = next(p for pool in game.app.curriculum.values() for p in pool if p["term"] == term)
    lines = prompt_lines(game)
    assert len(lines) == 2
    assert " ".join(lines) == entry["prompt"]          # no words lost


def test_short_prompt_stays_on_one_line(game):
    show_term(game, "bug")
    assert prompt_lines(game) == ["Is a bug an intended feature in a program?"]


def test_every_prompt_line_fits_the_canvas_width(game):
    PIL = pytest.importorskip("PIL.ImageFont")
    font_path = next((p for p in FONT_PATHS if os.path.exists(p)), None)
    if font_path is None:
        pytest.skip("no Arial-compatible font installed")
    font = PIL.truetype(font_path, 13)
    too_wide = []
    for pool in game.app.curriculum.values():
        for puzzle in pool:
            show_term(game, puzzle["term"])
            for line in prompt_lines(game):
                if font.getlength(line) > CANVAS_WIDTH - 20:        # 10-unit margin each side
                    too_wide.append((puzzle["term"], round(font.getlength(line))))
    assert too_wide == []


# ---- defect 2: Errors, Streak and header text were below 4.5:1 contrast ----

@pytest.mark.parametrize("label", ["tierLabel", "timeLabel", "errorLabel", "streakLabel", "topicLabel",
                                   "promptLabel", "feedbackLabel", "instrLabel", "globalTimerLabel"])
def test_label_text_meets_wcag_contrast(game, label):
    shape = getattr(game, label)
    assert contrast(shape.fill, game.app.background) >= 4.5


def test_header_title_meets_wcag_contrast(game):
    assert contrast("white", header_fill(game)) >= 4.5


# ---- defect 3: the streak flame was never drawn by the sandbox canvas ------

def test_streak_of_three_shows_a_marker_the_canvas_can_draw(game):
    for _ in range(3):
        answer(game, 8)
    assert game.streakLabel.value.isascii()             # no emoji left in the label
    assert game.streakStar.visible is True


def test_streak_marker_disappears_when_the_streak_breaks(game):
    for _ in range(3):
        answer(game, 8)
    game.onKeyPress(wrong_key(game))
    assert game.streakStar.visible is False


# ---- defect 4: capital Y and N (Caps Lock) were ignored without a message --

def test_capital_letters_are_accepted_as_answers(game):
    app = game.app
    game.onKeyPress(app.correctKey.upper())
    assert app.totalQuestions == 1
    game.onKeyPress(wrong_key(game).upper())
    assert app.errors == 1
