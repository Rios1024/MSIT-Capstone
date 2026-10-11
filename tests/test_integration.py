"""Integration tests for the Dynamic CS Vocabulary Engine (Unit 6).

These tests exercise the modules together, through the same two entry points
CS Academy calls (onKeyPress and onStep), and check the hand-offs between
the curriculum data, the DDA engine, the state manager and the interface.
"""
import random

from stubs import answer, wait, wrong_key


def pool_terms(game, tier):
    return {p["term"] for p in game.app.curriculum[tier]}


def shown_term(game):
    return game.termLabel.value.replace("Term: ", "", 1)


def assert_ui_matches_state(game):
    """Interface <-> state manager: every label mirrors the engine state."""
    app = game.app
    assert game.tierLabel.value == f"Tier: {app.difficulty}"
    assert game.topicLabel.value == app.topics[app.difficulty]
    assert game.errorLabel.value == f"Errors: {app.errors}"
    assert game.streakLabel.value == game.streakText(app.currentStreak)
    # Data layer <-> interface: the term on screen comes from the active tier
    assert shown_term(game) in pool_terms(game, app.difficulty)
    assert shown_term(game) == app.lastTerm
    assert 1 <= app.difficulty <= 3
    assert app.highestTier >= app.difficulty


def test_key_press_flows_through_every_module(game):
    """One correct key press reaches the engine, the data layer and the UI."""
    app = game.app
    first_term = shown_term(game)
    answer(game, 3.0)                      # fast first-try answer
    assert app.totalQuestions == 1         # event listener -> state
    assert app.lastReason == "flow"        # state -> DDA engine
    assert app.difficulty == 2             # DDA engine -> state
    assert shown_term(game) in pool_terms(game, 2)    # state -> data layer
    assert shown_term(game) != first_term
    assert game.timeLabel.value == "Time: 3.0s"       # last tick drawn
    assert app.timeTicks == 0              # question clock restarted
    assert_ui_matches_state(game)


def test_climb_then_fall_keeps_ui_and_engine_in_step(game):
    """Promotion to Tier 3 and demotion back to Tier 1, label by label."""
    app = game.app
    tiers = []
    for _ in range(6):                     # steady student: streak promotions
        answer(game, 8.0)
        assert_ui_matches_state(game)
        tiers.append(app.difficulty)
    assert tiers == [1, 1, 2, 2, 2, 3]
    for _ in range(4):                     # then two pairs of first-try misses
        answer(game, 8.0, wrong_first=1)
        assert_ui_matches_state(game)
        tiers.append(app.difficulty)
    assert tiers[6:] == [3, 2, 2, 1]
    assert app.highestTier == 3


def test_wrong_key_feedback_comes_from_the_same_curriculum_entry(game):
    """Data layer -> interface: the correction shown belongs to the term shown."""
    app = game.app
    for _ in range(25):
        term = shown_term(game)
        entry = next(p for p in app.curriculum[app.difficulty] if p["term"] == term)
        assert game.promptLabel.value == entry["prompt"]
        assert app.correctKey == entry["ans"]
        game.onKeyPress(wrong_key(game))
        assert game.feedbackLabel.value == entry["correction"]
        game.onKeyPress(app.correctKey)
        assert game.feedbackLabel.value == ""     # cleared for the next term
        app.globalTimeTicks = 0


def test_full_session_report_matches_engine_counters(game):
    """A scripted three-minute session, checked against an independent tally."""
    app = game.app
    rng = random.Random(6)
    asked = first_try = 0
    peak = 1
    while not app.isGameOver:
        seconds = rng.choice([2.0, 4.0, 7.0, 9.0, 16.0])
        misses = rng.choice([0, 0, 0, 1, 2])
        wait(game, seconds)
        if app.isGameOver:
            break
        for _ in range(misses):
            game.onKeyPress(wrong_key(game))
        game.onKeyPress(app.correctKey)
        asked += 1
        first_try += (misses == 0)
        peak = max(peak, app.difficulty)
        assert_ui_matches_state(game)
    assert app.globalTimeTicks == 1800
    assert app.reportUI.visible and not app.gameUI.visible
    assert app.reportTotal.value == f"Questions Answered: {asked}"
    assert app.reportAcc.value == f"First-Try Accuracy: {int(first_try * 100 / asked)}%"
    assert app.reportPeak.value == f"Highest Tier Reached: {peak}"


def test_timer_labels_track_the_step_clock(game):
    """Step clock -> interface: both timers are redrawn on every tick."""
    answer(game, 8.0)
    wait(game, 2.5)
    assert game.timeLabel.value == "Time: 2.5s"
    assert game.globalTimerLabel.value == "Session Time Left: 170s"


def test_random_input_never_breaks_the_system(game):
    """Robustness: 20,000 random events, valid and invalid, raise no error
    and never leave the interface out of step with the engine."""
    app = game.app
    rng = random.Random(2026)
    keys = ["y", "n", "y", "n", "a", "space", "enter", "Y", "left", "7", ""]
    for _ in range(20000):
        if rng.random() < 0.7:
            game.onStep()
        else:
            game.onKeyPress(rng.choice(keys))
        if app.isGameOver:
            assert app.reportUI.visible
            # start another session the way a browser refresh would
            app.isGameOver = False
            app.globalTimeTicks = 0
            app.reportUI.visible = False
            app.gameUI.visible = True
        assert_ui_matches_state(game)
