"""Unit tests for the Dynamic CS Vocabulary Engine (main.py).

Black-box tests call the pure functions and compare outputs with the stated
rules. White-box tests drive onKeyPress() and onStep() and inspect state.
"""
import pytest

from stubs import answer, wait, wrong_key


# =============================================================================
# Black-box tests: pure functions
# =============================================================================

@pytest.mark.parametrize("tier, streak, missStreak, seconds, errors, expected", [
    (1, 1, 0, 4.9, 0, (2, "flow")),        # just under the 5 s flow boundary
    (1, 1, 0, 5.0, 0, (1, "steady")),      # exactly 5 s is not flow
    (2, 1, 0, 15.0, 0, (2, "steady")),     # exactly 15 s is not overload
    (2, 1, 0, 15.1, 0, (1, "overload")),   # just over the 15 s boundary
    (2, 0, 1, 3.0, 1, (2, "steady")),      # one miss holds the tier
    (2, 0, 2, 3.0, 1, (1, "overload")),    # two first-try misses in a row
    (2, 0, 1, 3.0, 2, (1, "overload")),    # two wrong presses on one question
    (1, 3, 0, 8.0, 0, (2, "streak")),      # third consecutive first-try answer
    (1, 4, 0, 8.0, 0, (1, "steady")),      # fourth does not promote again
    (1, 6, 0, 8.0, 0, (2, "streak")),      # sixth promotes again
    (2, 3, 0, 20.0, 0, (1, "overload")),   # overload outranks a streak
    (3, 3, 0, 2.0, 0, (3, "streak")),      # promotion is capped at Tier 3
    (1, 0, 2, 20.0, 2, (1, "overload")),   # demotion is floored at Tier 1
])
def test_next_difficulty_rules(game, tier, streak, missStreak, seconds, errors, expected):
    assert game.nextDifficulty(tier, streak, missStreak, seconds, errors) == expected


@pytest.mark.parametrize("streak, missStreak, errors, expected", [
    (0, 0, 0, (1, 0)),
    (2, 1, 0, (3, 0)),
    (4, 0, 1, (0, 1)),
    (0, 1, 2, (0, 2)),
])
def test_update_streaks(game, streak, missStreak, errors, expected):
    assert game.updateStreaks(streak, missStreak, errors) == expected


@pytest.mark.parametrize("correct, total, percent", [
    (0, 0, 0),
    (2, 3, 66),
    (5, 5, 100),
    (0, 4, 0),
])
def test_calc_accuracy(game, correct, total, percent):
    assert game.calcAccuracy(correct, total) == percent


@pytest.mark.parametrize("ticks, seconds", [
    (0, 180),
    (9, 180),
    (10, 179),
    (1799, 1),
    (1800, 0),
    (5000, 0),
])
def test_seconds_remaining(game, ticks, seconds):
    assert game.secondsRemaining(ticks, 10) == seconds


def test_pick_puzzle_never_repeats_last_term(game):
    pool = game.app.curriculum[2]
    last = None
    for _ in range(2000):
        puzzle = game.pickPuzzle(pool, last)
        assert puzzle["term"] != last
        last = puzzle["term"]


def test_pick_puzzle_single_item_pool(game):
    pool = [{"term": "only"}]
    assert game.pickPuzzle(pool, "only") == {"term": "only"}


def test_streak_text_is_plain_text(game):
    assert game.streakText(2) == "Streak: 2"
    assert game.streakText(3) == "Streak: 3"
    assert game.streakText(3).isascii()    # the canvas does not draw emoji
    assert (game.showStreakStar(2), game.showStreakStar(3)) == (False, True)


@pytest.mark.parametrize("text, expected", [
    ("Is a bug an intended feature in a program?", ("Is a bug an intended feature in a program?", "")),
    ("ab " * 21 + "a", ("ab " * 21 + "a", "")),                   # 64 characters: exactly at the limit
    ("ab " * 21 + "ab", ("ab " * 10 + "ab", "ab " * 10 + "ab")),    # 65 characters: one over the limit
    ("aaaa bbbb " * 6 + "cccc dddd", ("aaaa bbbb aaaa bbbb aaaa bbbb aaaa", "bbbb aaaa bbbb aaaa bbbb cccc dddd")),
])
def test_wrap_prompt(game, text, expected):
    assert game.wrapPrompt(text) == expected


@pytest.mark.parametrize("key, expected", [("Y", "y"), ("N", "n"), ("y", "y"), ("space", "space"), ("A", "A")])
def test_normalize_key(game, key, expected):
    assert game.normalizeKey(key) == expected


def test_curriculum_is_well_formed(game):
    assert sorted(game.app.curriculum) == [1, 2, 3]
    for tier, pool in game.app.curriculum.items():
        assert len(pool) >= 2, "each tier needs two terms to avoid repeats"
        assert tier in game.app.topics
        terms = [p["term"] for p in pool]
        assert len(terms) == len(set(terms))
        for puzzle in pool:
            assert puzzle["ans"] in ("y", "n")
            assert puzzle["prompt"].endswith("?")
            assert len(puzzle["prompt"]) <= 2 * game.MAX_PROMPT_CHARS
            assert all(len(line) <= game.MAX_PROMPT_CHARS for line in game.wrapPrompt(puzzle["prompt"]))
            expected_word = "True." if puzzle["ans"] == "y" else "False."
            assert puzzle["correction"].startswith(expected_word)


# =============================================================================
# White-box tests: event handlers and internal state
# =============================================================================

def test_first_scenario_is_loaded(game):
    app = game.app
    assert app.difficulty == 1
    assert app.correctKey in ("y", "n")
    assert game.tierLabel.value == "Tier: 1"
    assert game.topicLabel.value == "Tier 1: Basics"
    assert game.termLabel.value == f"Term: {app.lastTerm}"
    assert game.globalTimerLabel.value == "Session Time Left: 180s"
    assert app.reportUI.visible is False


def test_other_keys_are_ignored(game):
    app = game.app
    before = (app.totalQuestions, app.errors, game.termLabel.value)
    for key in ["a", "space", "enter", "A", "1", "left"]:
        game.onKeyPress(key)
    assert (app.totalQuestions, app.errors, game.termLabel.value) == before


def test_wrong_key_shows_correction_and_breaks_streak(game):
    app = game.app
    answer(game, 8)
    answer(game, 8)
    assert app.currentStreak == 2
    game.onKeyPress(wrong_key(game))
    assert app.errors == 1
    assert app.currentStreak == 0
    assert game.errorLabel.value == "Errors: 1"
    assert game.streakLabel.value == "Streak: 0"
    assert game.feedbackLabel.value == app.currentCorrection
    assert app.totalQuestions == 2    # the question is still open


def test_first_try_answer_updates_accuracy_counters(game):
    app = game.app
    answer(game, 8)
    answer(game, 8, wrong_first=1)
    assert app.totalQuestions == 2
    assert app.firstTryCorrect == 1
    assert app.missStreak == 1


def test_three_streak_promotes_and_shows_star(game):
    app = game.app
    for _ in range(2):
        answer(game, 8)
    assert game.streakStar.visible is False
    answer(game, 8)
    assert app.difficulty == 2
    assert app.lastReason == "streak"
    assert app.currentStreak == 3
    assert game.streakLabel.value == "Streak: 3"
    assert game.streakStar.visible is True
    assert game.tierLabel.value == "Tier: 2"


def test_fast_first_try_answer_promotes(game):
    app = game.app
    answer(game, 2)
    assert app.difficulty == 2
    assert app.lastReason == "flow"


def test_two_first_try_misses_in_a_row_demote(game):
    app = game.app
    app.difficulty = 3
    answer(game, 8, wrong_first=1)
    assert app.difficulty == 3
    answer(game, 8, wrong_first=1)
    assert app.difficulty == 2
    assert app.lastReason == "overload"
    assert (app.currentStreak, app.missStreak) == (0, 0)


def test_student_who_always_misses_falls_to_tier_one(game):
    app = game.app
    app.difficulty = 3
    tiers = []
    for _ in range(12):
        answer(game, 8, wrong_first=1)
        tiers.append(app.difficulty)
    assert tiers[:4] == [3, 2, 2, 1]
    assert set(tiers[4:]) == {1}


def test_slow_correct_answers_never_promote(game):
    app = game.app
    app.difficulty = 2
    tiers = []
    for _ in range(6):
        answer(game, 20)
        tiers.append(app.difficulty)
    assert tiers == [1, 1, 1, 1, 1, 1]


def test_no_term_is_shown_twice_in_a_row(game):
    previous = game.termLabel.value
    for _ in range(200):
        answer(game, 0.5)    # stays well inside the session
        game.app.globalTimeTicks = 0
        assert game.termLabel.value != previous
        previous = game.termLabel.value


def test_highest_tier_survives_a_demotion(game):
    app = game.app
    for _ in range(3):
        answer(game, 8)
    assert app.highestTier == 2
    answer(game, 20)
    assert app.difficulty == 1
    assert app.highestTier == 2


def test_session_ends_after_three_minutes(game):
    app = game.app
    wait(game, 179.9)
    assert app.isGameOver is False
    assert game.globalTimerLabel.value == "Session Time Left: 1s"
    wait(game, 0.1)
    assert app.isGameOver is True
    assert game.globalTimerLabel.value == "Session Time Left: 0s"
    assert app.reportUI.visible is True
    assert app.gameUI.visible is False


def test_input_and_clock_stop_after_game_over(game):
    app = game.app
    wait(game, 180)
    ticks, total = app.globalTimeTicks, app.totalQuestions
    game.onStep()
    game.onKeyPress(app.correctKey)
    assert (app.globalTimeTicks, app.totalQuestions) == (ticks, total)


def test_report_shows_session_statistics(game):
    app = game.app
    answer(game, 8)
    answer(game, 8, wrong_first=1)
    answer(game, 8)
    wait(game, 180)
    assert app.reportTotal.value == "Questions Answered: 3"
    assert app.reportAcc.value == "First-Try Accuracy: 66%"
    assert app.reportPeak.value == "Highest Tier Reached: 1"
