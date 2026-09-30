import random

# ==============================================================================
# 1. INITIALIZATION & STATE MANAGEMENT
# ==============================================================================
# The CS Academy sandbox runs a continuous loop at roughly 10 frames per second.
app.stepsPerSecond = 10

# Starting state variables for the DDA engine
app.difficulty = 1  # All students begin at Tier 1 to establish a baseline
app.timeTicks = 0   # Tracks the number of frames elapsed per question
app.errors = 0      # Tracks the number of incorrect keystrokes per question

# ==============================================================================
# 2. CURRICULUM DATA STRUCTURE
# ==============================================================================
# The curriculum is divided into three cognitive tiers. 
# Using lists inside the dictionary allows the engine to pull random questions 
# from a tier, preventing students from memorizing patterns if the DDA algorithm
# bumps them up and down between tiers repeatedly.
app.curriculum = {
    1: [ # Tier 1: Foundational Semantics (Lowest Cognitive Load)
        {"term": "variable", "prompt": "Can you change the value a variable stores later in the code?", "ans": 'y', "correction": "True. Variables store values that can be updated or referenced later."},
        {"term": "type", "prompt": "Does a variable share the 'type' of the data it stores?", "ans": 'y', "correction": "True. If a variable holds an integer, its type is classified as int."},
        {"term": "string", "prompt": "Are strings only created using double quotes, never single?", "ans": 'n', "correction": "False. Strings can use single or double quotes."},
        {"term": "integer", "prompt": "Are integers numbers with decimal points?", "ans": 'n', "correction": "False. Integers are whole numbers; floats have decimals."},
        {"term": "float", "prompt": "Is a float a data type used for whole numbers?", "ans": 'n', "correction": "False. Floats are numbers with decimal points."},
        {"term": "booleans", "prompt": "Can a boolean evaluate to 'Maybe'?", "ans": 'n', "correction": "False. Booleans have exactly two possible values: True or False."},
        {"term": "characters", "prompt": "Is a single symbol like '!' an example of a character?", "ans": 'y', "correction": "True. Characters represent single symbols or letters."},
        {"term": "pseudocode", "prompt": "Is pseudocode syntactically correct code?", "ans": 'n', "correction": "False. Pseudocode uses normal everyday language to describe logic."}
    ],
    2: [ # Tier 2: Control Flow & Events (Medium Cognitive Load)
        {"term": "while-loop", "prompt": "Does a while-loop keep running endlessly until its condition becomes False?", "ans": 'y', "correction": "True. It evaluates its condition each time before looping."},
        {"term": "for-loop", "prompt": "Does a for-loop run until a condition evaluates to False?", "ans": 'n', "correction": "False. That's a while-loop. For-loops run a set number of times."},
        {"term": "condition", "prompt": "Can a condition evaluate to something other than True or False?", "ans": 'n', "correction": "False. Conditions are logical expressions that must be True or False."},
        {"term": "conditional", "prompt": "Do conditionals run code regardless of whether they are True or False?", "ans": 'n', "correction": "False. Code only runs depending on if the condition evaluates to True."},
        {"term": "event", "prompt": "Can moving a mouse trigger an event function call?", "ans": 'y', "correction": "True. Mouse movements and key holds are state changes (events)."}
    ],
    3: [ # Tier 3: Architecture & Scope (Highest Cognitive Load)
        {"term": "function", "prompt": "Can a function be run by 'calling' its name later in the program?", "ans": 'y', "correction": "True. Functions bundle code to be executed when called."},
        {"term": "helper function", "prompt": "Is a helper function called inside the body of another function?", "ans": 'y', "correction": "True. They help complete part of a bigger task."},
        {"term": "global variable", "prompt": "Can global variables only be accessed inside functions?", "ans": 'n', "correction": "False. They are declared outside and can be used anywhere."},
        {"term": "local variable", "prompt": "Is a local variable accessible anywhere in your entire program?", "ans": 'n', "correction": "False. It can only be used within its defined scope."},
        {"term": "parameters", "prompt": "Are parameters the actual data values passed into a function call?", "ans": 'n', "correction": "False. Arguments are the data; parameters are the variables declared."},
        {"term": "arguments", "prompt": "Are arguments the data values passed into function calls?", "ans": 'y', "correction": "True. Arguments are the values given to the function parameters."}
    ]
}

app.topics = {1: "Tier 1: Basics", 2: "Tier 2: Control Flow", 3: "Tier 3: Scope"}

# ==============================================================================
# 3. USER INTERFACE (CANVAS SETUP)
# ==============================================================================
# Persistent UI objects are instantiated once. We update their properties 
# (like .value or .fill) rather than redrawing the screen, saving memory.

app.background = 'ghostWhite'
Rect(0, 0, 400, 60, fill='slateGray')
Label("CS Principles - Dynamic Vocab Engine", 200, 30, fill='white', size=16, bold=True)

# HUD (Heads-Up Display) for real-time performance tracking
tierLabel = Label("Tier: 1", 70, 90, size=14, bold=True)
timeLabel = Label("Time: 0.0s", 200, 90, size=14)
errorLabel = Label("Errors: 0", 330, 90, size=14, fill='red')

# Puzzle Display Area
topicLabel = Label("", 200, 130, size=18, bold=True, fill='midnightBlue')
termLabel = Label("", 200, 165, size=22, bold=True, fill='crimson')
promptLabel = Label("", 200, 210, size=13)
feedbackLabel = Label("", 200, 260, size=12, fill='darkGreen')
Label("Press 'Y' for True | Press 'N' for False", 200, 320, size=14)

# ==============================================================================
# 4. SCENARIO MANAGER
# ==============================================================================
def loadScenario():
    # Reset tracking metrics for the new question
    app.timeTicks = 0
    app.errors = 0
    
    # Use the random library to select a random dictionary from the current tier's list
    puzzle = random.choice(app.curriculum[app.difficulty])
    
    # Inject the selected puzzle's data into the UI labels
    tierLabel.value = f"Tier: {app.difficulty}"
    topicLabel.value = app.topics[app.difficulty]
    termLabel.value = f"Term: {puzzle['term']}"
    promptLabel.value = puzzle["prompt"]
    
    # Store the correct answer and pedagogical feedback in app state for the event listener
    errorLabel.value = "Errors: 0"
    app.correctKey = puzzle["ans"]
    app.currentCorrection = puzzle["correction"]
    feedbackLabel.value = "" 

# ==============================================================================
# 5. DYNAMIC DIFFICULTY ADJUSTMENT (DDA) ALGORITHM
# ==============================================================================
def applyDDA():
    # Convert the frames counted during onStep() into actual seconds
    time_taken = app.timeTicks / app.stepsPerSecond
    
    # THRESHOLD 1: BOREDOM / FLOW STATE
    # If the student answers in under 5 seconds with zero mistakes, the cognitive load 
    # is too low. The algorithm increments the difficulty to prevent disengagement.
    # min(3, ...) ensures the difficulty cannot exceed the maximum tier of 3.
    if time_taken < 5.0 and app.errors == 0:
        app.difficulty = min(3, app.difficulty + 1)
        
    # THRESHOLD 2: COGNITIVE OVERLOAD / FRUSTRATION
    # If the student takes longer than 15 seconds OR makes 2 or more mistakes, the 
    # cognitive load is too high. The algorithm decrements the difficulty to provide 
    # a conceptual safety net and prevent anxiety.
    # max(1, ...) ensures the difficulty cannot drop below the foundational tier of 1.
    elif time_taken > 15.0 or app.errors >= 2:
        app.difficulty = max(1, app.difficulty - 1)
        
    # THRESHOLD 3 (IMPLICIT): OPTIMAL CHALLENGE
    # If time is between 5s - 15s, or there is exactly 1 error, the code bypasses 
    # the above if/elif blocks. The difficulty remains unchanged, keeping the student 
    # in their current state of flow.
        
    # Load a new puzzle at the newly calculated (or maintained) difficulty tier
    loadScenario()

# ==============================================================================
# 6. EVENT LISTENERS
# ==============================================================================
def onStep():
    # This built-in CS Academy function fires 10 times per second.
    # We use it as our engine's internal stopwatch.
    app.timeTicks += 1
    timeLabel.value = f"Time: {app.timeTicks / app.stepsPerSecond}s"

def onKeyPress(key):
    # Security/Sanitization: The engine only reacts to 'y' and 'n'. 
    # All other keyboard mashing is ignored, eliminating code injection risks.
    if key in ['y', 'n']:
        
        # If the answer is correct, trigger the DDA algorithm to grade the performance
        if key == app.correctKey:
            applyDDA() 
            
        # If incorrect, increment the error metric (which the DDA engine tracks) 
        # and display the specific pedagogical correction on screen.
        else:
            app.errors += 1
            errorLabel.value = f"Errors: {app.errors}"
            feedbackLabel.value = app.currentCorrection

# ==============================================================================
# 7. INITIALIZATION CALL
# ==============================================================================
# Call loadScenario once at the bottom of the script to trigger the first puzzle
loadScenario()
