###=============================================================================
# Roger Rios, Capstone Project
###=============================================================================
import random

# ==============================================================================
# 1. INITIALIZATION & STATE MANAGEMENT
# ==============================================================================
app.stepsPerSecond = 10
app.isGameOver = False

# DDA tuning constants (named so the rules and the unit tests share one source)
MIN_TIER = 1
MAX_TIER = 3
FAST_SECONDS = 5.0       # Faster than this with no errors = flow state
SLOW_SECONDS = 15.0      # Slower than this = cognitive overload
STREAK_TO_PROMOTE = 3    # Every 3rd consecutive first-try answer promotes
MISSES_TO_DEMOTE = 2     # 2 consecutive first-try misses demote
SESSION_SECONDS = 180    # 3-minute session

# Session Tracking (3-Minute Limit)
app.globalTimeTicks = 0
app.sessionLimitTicks = SESSION_SECONDS * app.stepsPerSecond

# Performance & DDA State
app.difficulty = 1
app.timeTicks = 0
app.errors = 0
app.currentStreak = 0        # Consecutive correct first-try answers
app.missStreak = 0           # Consecutive questions missed on the first try
app.lastTerm = None          # Last term shown, so it is not repeated back-to-back
app.lastReason = 'steady'    # Why the DDA engine made its last decision
app.totalQuestions = 0       # Total questions answered
app.firstTryCorrect = 0      # Accuracy tracking
app.highestTier = 1          # Peak difficulty reached

# ==============================================================================
# 2. EXPANDED CURRICULUM DATA STRUCTURE
# ==============================================================================
app.curriculum = {
    1: [ # Tier 1: Foundational Semantics
        {"term": "variable", "prompt": "Can you change the value a variable stores later in the code?", "ans": 'y', "correction": "True. Variables store values that can be updated or referenced later."},
        {"term": "type", "prompt": "Does a variable share the 'type' of the data it stores?", "ans": 'y', "correction": "True. If a variable holds an integer, its type is classified as int."},
        {"term": "string", "prompt": "Are strings only created using double quotes, never single?", "ans": 'n', "correction": "False. Strings can use single or double quotes."},
        {"term": "integer", "prompt": "Are integers numbers with decimal points?", "ans": 'n', "correction": "False. Integers are whole numbers; floats have decimals."},
        {"term": "float", "prompt": "Is a float a data type used for whole numbers?", "ans": 'n', "correction": "False. Floats are numbers with decimal points."},
        {"term": "booleans", "prompt": "Can a boolean evaluate to 'Maybe'?", "ans": 'n', "correction": "False. Booleans have exactly two possible values: True or False."},
        {"term": "characters", "prompt": "Is a single symbol like '!' an example of a character?", "ans": 'y', "correction": "True. Characters represent single symbols or letters."},
        {"term": "pseudocode", "prompt": "Is pseudocode syntactically correct code?", "ans": 'n', "correction": "False. Pseudocode uses normal everyday language to describe logic."},
        {"term": "syntax", "prompt": "Does syntax refer to the strict rules of how code must be written?", "ans": 'y', "correction": "True. Syntax is the grammar of the programming language."},
        {"term": "bug", "prompt": "Is a bug an intended feature in a program?", "ans": 'n', "correction": "False. A bug is an error or flaw in the code."}
    ],
    2: [ # Tier 2: Control Flow & Events
        {"term": "while-loop", "prompt": "Does a while-loop keep running endlessly until its condition becomes False?", "ans": 'y', "correction": "True. It evaluates its condition each time before looping."},
        {"term": "for-loop", "prompt": "Does a for-loop run until a condition evaluates to False?", "ans": 'n', "correction": "False. That's a while-loop. For-loops run a set number of times."},
        {"term": "condition", "prompt": "Can a condition evaluate to something other than True or False?", "ans": 'n', "correction": "False. Conditions are logical expressions that must be True or False."},
        {"term": "conditional", "prompt": "Do conditionals run code regardless of whether they are True or False?", "ans": 'n', "correction": "False. Code only runs depending on if the condition evaluates to True."},
        {"term": "event", "prompt": "Can moving a mouse trigger an event function call?", "ans": 'y', "correction": "True. Mouse movements and key holds are state changes (events)."},
        {"term": "if-elif-else", "prompt": "Does an 'elif' statement allow you to check multiple conditions in sequence?", "ans": 'y', "correction": "True. It stands for 'else if' and chains conditionals."}
    ],
    3: [ # Tier 3: Architecture & Scope
        {"term": "function", "prompt": "Can a function be run by 'calling' its name later in the program?", "ans": 'y', "correction": "True. Functions bundle code to be executed when called."},
        {"term": "helper function", "prompt": "Is a helper function called inside the body of another function?", "ans": 'y', "correction": "True. They help complete part of a bigger task."},
        {"term": "global variable", "prompt": "Can global variables only be accessed inside functions?", "ans": 'n', "correction": "False. They are declared outside and can be used anywhere."},
        {"term": "local variable", "prompt": "Is a local variable accessible anywhere in your entire program?", "ans": 'n', "correction": "False. It can only be used within its defined scope."},
        {"term": "parameters", "prompt": "Are parameters the actual data values passed into a function call?", "ans": 'n', "correction": "False. Arguments are the data; parameters are the variables declared."},
        {"term": "arguments", "prompt": "Are arguments the data values passed into function calls?", "ans": 'y', "correction": "True. Arguments are the values given to the function parameters."},
        {"term": "return", "prompt": "Does a 'return' statement pass a value back to where the function was called?", "ans": 'y', "correction": "True. It outputs data from the function back to the main program."}
    ]
}

app.topics = {1: "Tier 1: Basics", 2: "Tier 2: Control Flow", 3: "Tier 3: Scope"}

# ==============================================================================
# 3. USER INTERFACE GROUPS
# ==============================================================================
app.background = 'ghostWhite'

# Persistent Header
Rect(0, 0, 400, 60, fill='slateGray')
Label("CS Principles - Dynamic Vocab Engine", 200, 30, fill='white', size=16, bold=True)

# Game UI Group
tierLabel = Label("Tier: 1", 70, 90, size=14, bold=True)
timeLabel = Label("Time: 0.0s", 200, 90, size=14)
errorLabel = Label("Errors: 0", 330, 90, size=14, fill='red')
streakLabel = Label("Streak: 0", 200, 110, size=12, fill='orange', bold=True)
globalTimerLabel = Label(f"Session Time Left: {SESSION_SECONDS}s", 200, 380, size=14, bold=True)

topicLabel = Label("", 200, 140, size=18, bold=True, fill='midnightBlue')
termLabel = Label("", 200, 175, size=22, bold=True, fill='crimson')
promptLabel = Label("", 200, 220, size=13)
feedbackLabel = Label("", 200, 270, size=12, fill='darkGreen')
instrLabel = Label("Press 'Y' for True | Press 'N' for False", 200, 340, size=14)

app.gameUI = Group(tierLabel, timeLabel, errorLabel, streakLabel, globalTimerLabel, topicLabel, termLabel, promptLabel, feedbackLabel, instrLabel)

# Report UI Group (Hidden initially)
app.reportBg = Rect(50, 80, 300, 240, fill='white', border='black')
app.reportTitle = Label("SESSION COMPLETE", 200, 110, size=20, bold=True)
app.reportTotal = Label("Questions Answered: 0", 200, 160, size=16)
app.reportAcc = Label("First-Try Accuracy: 0%", 200, 200, size=16)
app.reportPeak = Label("Highest Tier Reached: 1", 200, 240, size=16)
app.reportInstr = Label("Refresh browser to replay.", 200, 290, size=14, italic=True)

app.reportUI = Group(app.reportBg, app.reportTitle, app.reportTotal, app.reportAcc, app.reportPeak, app.reportInstr)
app.reportUI.visible = False

# ==============================================================================
# 4. PURE DDA LOGIC (no graphics calls, so each rule can be unit tested)
# ==============================================================================
def updateStreaks(streak, missStreak, errors):
    """Run once per completed question. Returns (streak, missStreak).
    A first-try answer extends the streak; a corrected answer counts as a miss."""
    if errors == 0:
        return streak + 1, 0
    return 0, missStreak + 1

def nextDifficulty(tier, streak, missStreak, seconds, errors):
    """Decide the next tier. Returns (newTier, reason).
    Overload is checked first so a slow or missed answer can never promote."""
    # Rule 1: Cognitive Overload Mitigation
    if seconds > SLOW_SECONDS or errors >= 2 or missStreak >= MISSES_TO_DEMOTE:
        return max(MIN_TIER, tier - 1), 'overload'

    # Rule 2: Promotion on every 3rd consecutive first-try answer
    if streak > 0 and streak % STREAK_TO_PROMOTE == 0:
        return min(MAX_TIER, tier + 1), 'streak'

    # Rule 3: Flow State Recognition
    if errors == 0 and seconds < FAST_SECONDS:
        return min(MAX_TIER, tier + 1), 'flow'

    # Rule 4: Optimal challenge, hold the tier
    return tier, 'steady'

def pickPuzzle(pool, lastTerm):
    """Random puzzle from the tier pool, never the term that was just shown."""
    choices = [p for p in pool if p["term"] != lastTerm]
    if len(choices) == 0:    # A one-item pool has no alternative
        choices = pool
    return random.choice(choices)

def calcAccuracy(firstTryCorrect, totalQuestions):
    """First-try accuracy as a whole percent; 0 when nothing was answered."""
    if totalQuestions == 0:
        return 0
    return int(firstTryCorrect * 100 / totalQuestions)

def secondsRemaining(globalTicks, stepsPerSecond):
    """Whole seconds left in the session, never below zero."""
    return max(0, SESSION_SECONDS - globalTicks // stepsPerSecond)
# Work in progress
def streakText(streak):
    """Streak label text; the flame appears from a 3-answer streak onward."""
    if streak >= STREAK_TO_PROMOTE:
        return f"Streak: {streak} \U0001F525" 
    return f"Streak: {streak}"

# ==============================================================================
# 5. ENGINE STATE & UI UPDATES
# ==============================================================================
def loadScenario():
    app.timeTicks = 0
    app.errors = 0
    puzzle = pickPuzzle(app.curriculum[app.difficulty], app.lastTerm)
    app.lastTerm = puzzle["term"]

    tierLabel.value = f"Tier: {app.difficulty}"
    topicLabel.value = app.topics[app.difficulty]
    termLabel.value = f"Term: {puzzle['term']}"
    promptLabel.value = puzzle["prompt"]

    errorLabel.value = "Errors: 0"
    streakLabel.value = streakText(app.currentStreak)

    app.correctKey = puzzle["ans"]
    app.currentCorrection = puzzle["correction"]
    feedbackLabel.value = ""

def applyDDA():
    time_taken = app.timeTicks / app.stepsPerSecond

    app.currentStreak, app.missStreak = updateStreaks(app.currentStreak, app.missStreak, app.errors)
    app.difficulty, app.lastReason = nextDifficulty(
        app.difficulty, app.currentStreak, app.missStreak, time_taken, app.errors)

    # An overload decision starts the student fresh at the easier tier
    if app.lastReason == 'overload':
        app.currentStreak = 0
        app.missStreak = 0

    # Track highest tier for the final report
    if app.difficulty > app.highestTier:
        app.highestTier = app.difficulty

    loadScenario()

def triggerReport():
    app.isGameOver = True
    app.gameUI.visible = False

    # Calculate statistics
    app.reportTotal.value = f"Questions Answered: {app.totalQuestions}"
    accuracy = calcAccuracy(app.firstTryCorrect, app.totalQuestions)
    app.reportAcc.value = f"First-Try Accuracy: {accuracy}%"
    app.reportPeak.value = f"Highest Tier Reached: {app.highestTier}"

    app.reportUI.visible = True

# ==============================================================================
# 6. EVENT LISTENERS
# ==============================================================================
def onStep():
    if app.isGameOver:
        return

    app.timeTicks += 1
    app.globalTimeTicks += 1

    timeLabel.value = f"Time: {app.timeTicks / app.stepsPerSecond}s"

    # Update global countdown
    seconds_remaining = secondsRemaining(app.globalTimeTicks, app.stepsPerSecond)
    globalTimerLabel.value = f"Session Time Left: {seconds_remaining}s"

    if app.globalTimeTicks >= app.sessionLimitTicks:
        triggerReport()

def onKeyPress(key):
    # Only 'y' and 'n' are accepted; every other key is ignored
    if app.isGameOver or key not in ['y', 'n']:
        return

    if key == app.correctKey:
        if app.errors == 0:
            app.firstTryCorrect += 1

        app.totalQuestions += 1
        applyDDA()    # Streaks and the tier are updated inside the DDA engine
    else:
        app.errors += 1
        app.currentStreak = 0 # Break streak on error
        errorLabel.value = f"Errors: {app.errors}"
        streakLabel.value = streakText(app.currentStreak)
        feedbackLabel.value = app.currentCorrection

loadScenario()
