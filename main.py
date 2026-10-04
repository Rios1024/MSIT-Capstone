###=============================================================================
# Roger Rios, Capstone Project
###=============================================================================
import random

# ==============================================================================
# 1. INITIALIZATION & STATE MANAGEMENT
# ==============================================================================
app.stepsPerSecond = 10
app.isGameOver = False

# Session Tracking (3-Minute Limit)
app.globalTimeTicks = 0
app.sessionLimitTicks = 1800 # 3 minutes * 60 seconds * 10 ticks/sec

# Performance & DDA State
app.difficulty = 1
app.timeTicks = 0
app.errors = 0
app.currentStreak = 0        # Tracks consecutive correct first-try answers
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
globalTimerLabel = Label("Session Time: 180s", 200, 380, size=14, bold=True)

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
# 4. ENGINE LOGIC & DDA ALGORITHM
# ==============================================================================
def loadScenario():
    app.timeTicks = 0
    app.errors = 0
    puzzle = random.choice(app.curriculum[app.difficulty])
    
    tierLabel.value = f"Tier: {app.difficulty}"
    topicLabel.value = app.topics[app.difficulty]
    termLabel.value = f"Term: {puzzle['term']}"
    promptLabel.value = puzzle["prompt"]
    
    errorLabel.value = "Errors: 0"
    streakLabel.value = f"Streak: {app.currentStreak} \uD83D\uDD25" if app.currentStreak >= 3 else f"Streak: {app.currentStreak}"
    
    app.correctKey = puzzle["ans"]
    app.currentCorrection = puzzle["correction"]
    feedbackLabel.value = "" 

def applyDDA():
    time_taken = app.timeTicks / app.stepsPerSecond
    
    # DDA Feature 1: Rapid Promotion via Streak Multiplier
    if app.currentStreak >= 3:
        app.difficulty = min(3, app.difficulty + 1)
        app.currentStreak = 0 # Reset streak upon promotion to prevent runaway scaling
        
    # DDA Feature 2: Flow State Recognition
    elif time_taken < 5.0 and app.errors == 0:
        app.difficulty = min(3, app.difficulty + 1)
        
    # DDA Feature 3: Cognitive Overload Mitigation
    elif time_taken > 15.0 or app.errors >= 2:
        app.difficulty = max(1, app.difficulty - 1)
        
    # Track highest tier for the final report
    if app.difficulty > app.highestTier:
        app.highestTier = app.difficulty
        
    loadScenario()

def triggerReport():
    app.isGameOver = True
    app.gameUI.visible = False
    
    # Calculate statistics
    app.reportTotal.value = f"Questions Answered: {app.totalQuestions}"
    accuracy = int((app.firstTryCorrect / max(1, app.totalQuestions)) * 100)
    app.reportAcc.value = f"First-Try Accuracy: {accuracy}%"
    app.reportPeak.value = f"Highest Tier Reached: {app.highestTier}"
    
    app.reportUI.visible = True

# ==============================================================================
# 5. EVENT LISTENERS
# ==============================================================================
def onStep():
    if app.isGameOver:
        return
        
    app.timeTicks += 1
    app.globalTimeTicks += 1
    
    timeLabel.value = f"Time: {app.timeTicks / app.stepsPerSecond}s"
    
    # Update global countdown
    seconds_remaining = max(0, 180 - (app.globalTimeTicks // 10))
    globalTimerLabel.value = f"Session Time Left: {seconds_remaining}s"
    
    if app.globalTimeTicks >= app.sessionLimitTicks:
        triggerReport()

def onKeyPress(key):
    if app.isGameOver or key not in ['y', 'n']:
        return
        
    if key == app.correctKey:
        if app.errors == 0:
            app.firstTryCorrect += 1
            app.currentStreak += 1
        else:
            app.currentStreak = 0 
            
        app.totalQuestions += 1
        applyDDA() 
    else:
        app.errors += 1
        app.currentStreak = 0 # Break streak on error
        errorLabel.value = f"Errors: {app.errors}"
        streakLabel.value = f"Streak: {app.currentStreak}"
        feedbackLabel.value = app.currentCorrection

loadScenario()
