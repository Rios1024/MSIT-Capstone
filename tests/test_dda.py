"""Unit tests for the Dynamic CS Vocabulary Engine (main.py).

Black-box tests call the pure functions with inputs and check only outputs.
White-box tests drive the event handlers and inspect the engine's state.
"""
import pytest

FLAME = "\U0001F525"


# ------------------------------------------------------------------ helpers
def wait(engine, seconds):
    """Advance the sandbox clock by calling onStep() ten times a second."""
    for _ in range(int(seconds * engine.app.stepsPerSecond)):
        engine.onStep()


def wrong_key(engine):
    return "n" if engine.app.correctKey == "y" else "y"


def answer(engine, seconds=8, first_try=True):
    """Answer the current question, optionally after one wrong key press."""
    wait(engine, seconds)
    if not first_try:
        engine.onKeyPress(wrong_key(engine))
    engine.onKeyPress(engine.app.correctKey)


def start_at_tier(engine, tier):
    engine.app.difficulty = tier
    engine.loadScenario()


# =========================================================== BLACK-BOX TESTS
@pytest.mark.parametrize(
    "tier, streak, misses, seconds, errors, expected",
    [
        (1, 1, 0, 4.9, 0, (2, "flow")),       # just under the 5 s flow limit
        (1, 1, 0, 5.0, 0, (1, "steady")),     # boundary: exactly 5 s holds
        (2, 1, 0, 15.0, 0, (2, "steady")),    # boundary: exactly 15 s holds
        (2, 1, 0, 15.1, 0, (1, "overload")),  # just over the 15 s limit
        (2, 0, 1, 3.0, 1, (2, "steady")),     # one corrected miss holds
        (2, 0, 2, 3.0, 1, (1, "overload")),   # second miss in a row demotes
        (2, 0, 1, 3.0, 2, (1, "overload")),   # two wrong presses demote
        (1, 3, 0, 8.0, 0, (2, "streak")),     # third first-try answer promotes
        (1, 4, 0, 8.0, 0, (1, "steady")),     # fourth does not promote again
        (1, 6, 0, 8.0, 0, (2, "streak")),     # every third answer promotes
        (2, 3, 0, 20.0, 0, (1, "overload")),  # a slow streak never promotes
        (3, 3, 0, 2.0, 0, (3, "streak")),     # capped at the top tier
        (1, 0, 2, 20.0, 2, (1, "overload")),  # floored at the bottom tier
    ],
)
def test_next_difficulty_rules(engine, tier, streak, misses, seconds, errors, expected):
    assert engine.nextDifficulty(tier, streak, misses, seconds, errors) == expected


@pytest.mark.parametrize(
    "streak, misses, errors, expected",
    [
        (0, 0, 0, (1, 0)),  # first-try answer starts a streak
        (2, 1, 0, (3, 0)),  # first-try answer clears the miss count
        (4, 0, 1, (0, 1)),  # corrected answer breaks the streak
        (0, 1, 2, (0, 2)),  # misses accumulate
    ],
)
def test_update_streaks(engine, streak, misses, errors, expected):
    assert engine.updateStreaks(streak, misses, errors) == expected


@pytest.mark.parametrize(
    "first_try, total, expected",
    [(0, 0, 0), (2, 3, 66), (5, 5, 100), (0, 4, 0)],
)
def test_calc_accuracy(engine, first_try, total, expected):
    assert engine.calcAccuracy(first_try, total) == expected


@pytest.mark.parametrize(
    "ticks, expected",
    [(0, 180), (9, 180), (10, 179), (1799, 1), (1800, 0), (5000, 0)],
)
def test_seconds_remaining(engine, ticks, expected):
    assert engine.secondsRemaining(ticks, 10) == expected


def test_pick_puzzle_never_repeats_last_term(engine):
    pool = [{"term": "a"}, {"term": "b"}, {"term": "c"}]
    last = None
    for _ in range(200):
        puzzle = engine.pickPuzzle(pool, last)
        assert puzzle["term"] != last
        last = puzzle["term"]


def test_pick_puzzle_single_item_pool(engine):
    only = {"term": "solo"}
    assert engine.pickPuzzle([only], "solo") is only


def test_streak_text_flame_is_valid_unicode(engine):
    assert engine.streakText(2) == "Streak: 2"
    assert engine.streakText(3) == f"Streak: 3 {FLAME}"
    engine.streakText(3).encode("utf-8")  # raised UnicodeEncodeError before the fix


def test_curriculum_is_well_formed(engine):
    terms = []
    for tier in (1, 2, 3):
        pool = engine.app.curriculum[tier]
        assert len(pool) >= 2          # needed to avoid back-to-back repeats
        assert tier in engine.app.topics
        for puzzle in pool:
            assert set(puzzle) == {"term", "prompt", "ans", "correction"}
            assert puzzle["ans"] in ("y", "n")
            terms.append(puzzle["term"])
    assert len(terms) == len(set(terms))  # no duplicate terms


# =========================================================== WHITE-BOX TESTS
def test_first_scenario_is_loaded(engine):
    assert engine.app.difficulty == 1
    assert engine.app.correctKey in ("y", "n")
    assert engine.tierLabel.value == "Tier: 1"
    assert engine.globalTimerLabel.value == "Session Time Left: 180s"


def test_other_keys_are_ignored(engine):
    term = engine.termLabel.value
    for key in ("space", "a", "enter", "1"):
        engine.onKeyPress(key)
    assert engine.app.errors == 0
    assert engine.app.totalQuestions == 0
    assert engine.termLabel.value == term


def test_wrong_key_shows_correction_and_breaks_streak(engine):
    engine.app.currentStreak = 2
    engine.onKeyPress(wrong_key(engine))
    assert engine.app.errors == 1
    assert engine.app.currentStreak == 0
    assert engine.errorLabel.value == "Errors: 1"
    assert engine.feedbackLabel.value == engine.app.currentCorrection
    assert engine.app.totalQuestions == 0  # the question is still open


def test_first_try_answer_updates_accuracy_counters(engine):
    answer(engine, seconds=8)
    answer(engine, seconds=8, first_try=False)
    assert engine.app.totalQuestions == 2
    assert engine.app.firstTryCorrect == 1


def test_three_streak_promotes_and_shows_flame(engine):
    for _ in range(3):
        answer(engine, seconds=8)
    assert engine.app.difficulty == 2
    assert engine.app.lastReason == "streak"
    assert engine.streakLabel.value == f"Streak: 3 {FLAME}"


def test_fast_first_try_answer_promotes(engine):
    answer(engine, seconds=2)
    assert engine.app.difficulty == 2
    assert engine.app.lastReason == "flow"


def test_two_first_try_misses_in_a_row_demote(engine):
    start_at_tier(engine, 3)
    answer(engine, seconds=2, first_try=False)
    assert engine.app.difficulty == 3
    answer(engine, seconds=2, first_try=False)
    assert engine.app.difficulty == 2
    assert engine.app.missStreak == 0  # fresh start at the easier tier


def test_student_who_always_misses_falls_to_tier_one(engine):
    start_at_tier(engine, 3)
    for _ in range(12):
        answer(engine, seconds=2, first_try=False)
    assert engine.app.difficulty == 1
    assert engine.app.firstTryCorrect == 0


def test_slow_correct_answers_never_promote(engine):
    for _ in range(3):
        answer(engine, seconds=20)
    assert engine.app.difficulty == 1
    assert engine.app.currentStreak == 0


def test_no_term_is_shown_twice_in_a_row(engine):
    start_at_tier(engine, 2)
    previous = engine.termLabel.value
    for _ in range(60):
        engine.app.difficulty = 2
        engine.loadScenario()
        assert engine.termLabel.value != previous
        previous = engine.termLabel.value


def test_highest_tier_survives_a_demotion(engine):
    answer(engine, seconds=2)   # 1 -> 2 (flow)
    answer(engine, seconds=20)  # 2 -> 1 (overload)
    assert engine.app.difficulty == 1
    assert engine.app.highestTier == 2


def test_session_ends_after_three_minutes(engine):
    wait(engine, 179.9)
    assert engine.app.isGameOver is False
    engine.onStep()
    assert engine.app.isGameOver is True
    assert engine.app.reportUI.visible is True
    assert engine.app.gameUI.visible is False


def test_input_and_clock_stop_after_game_over(engine):
    wait(engine, 180)
    ticks = engine.app.globalTimeTicks
    engine.onKeyPress(engine.app.correctKey)
    engine.onStep()
    assert engine.app.totalQuestions == 0
    assert engine.app.globalTimeTicks == ticks


def test_report_shows_session_statistics(engine):
    answer(engine, seconds=8)
    answer(engine, seconds=8)
    answer(engine, seconds=8, first_try=False)
    wait(engine, 180)
    assert engine.app.reportTotal.value == "Questions Answered: 3"
    assert engine.app.reportAcc.value == "First-Try Accuracy: 66%"
    assert engine.app.reportPeak.value == "Highest Tier Reached: 1"
