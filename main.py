# Rios Capstone
import time # Used to track how long it takes the student to answer

def run_ap_puzzle():
    # Present the educational scenario mapped to AP standards
    print("--- Week 1: AP Standard AAP-2.E.2 & AAP-2.H.2 ---")
    print("Objective: The rover needs to check if its battery is over 20%.")
    print("Task: Write a Python if-statement checking if 'battery' is strictly greater than 20.")
    
    # Initialize performance tracking variables
    errors = 0
    start_time = time.time() # Record the exact time the puzzle starts
    
    # Infinite loop that continues until the user provides the correct answer
    while True:
        # Prompt user and strip any accidental whitespace from the beginning/end
        user_input = input("Enter your Python code: ").strip()
        
        # Basic exact-string validation (temporary solution for Week 1)
        if user_input == "if battery > 20:":
            end_time = time.time() # Record the completion time
            print(f"\nSuccess! Logic matches AP Standard.")
            
            # Calculate total time elapsed and display the performance metrics
            print(f"Time taken: {round(end_time - start_time, 2)} seconds | Errors: {errors}")
            break # Exit the while loop upon success
        else:
            errors += 1 # Increment error count for incorrect attempts
            print("Incorrect syntax or operator. Try again.\n")

# Standard Python safeguard to ensure the script runs only when executed directly
if __name__ == "__main__":
    run_ap_puzzle()
