import random

def provide_hint(guess, actual_number):
    """Provide a hint based on the difference between guess and actual_number."""
    if guess < actual_number:
        return "Try a higher number! 📈"
    else:
        return "Try a lower number! 📉"

def generate_random_number(start, end):
    """Generate a random number between start and end (inclusive)."""
    return random.randint(start, end)

def get_valid_input(prompt, start, end):
    """Get a valid integer input from the user between start and end (inclusive)."""
    while True:
        try:
            user_input = int(input(prompt))
            if start <= user_input <= end:
                return user_input
            else:
                print(f"Please enter a number between {start} and {end}.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def calculate_score(initial_score, attempts, max_attempts=10):
    """Calculate score based on attempts."""
    if attempts > max_attempts:
        return 0
    return max(initial_score - (attempts * 10), 0)

def main():
    print("🎯 Welcome to the Number Guessing Game! 🎯")
    print("I'm thinking of a number between 1 and 100.")

    number_to_guess = generate_random_number(1, 100)
    initial_score = 100
    attempts = 0
    max_attempts = 10

    while attempts < max_attempts:
        attempts += 1
        remaining_attempts = max_attempts - attempts

        print(f"\n--- Attempt {attempts} (Remaining: {remaining_attempts}) ---")
        guess = get_valid_input("Enter your guess: ", 1, 100)

        if guess == number_to_guess:
            final_score = calculate_score(initial_score, attempts, max_attempts)
            print(f"\n🎉 Congratulations! You guessed it in {attempts} attempts!")
            print(f"🏆 Your final score is: {final_score}")
            break
        else:
            hint = provide_hint(guess, number_to_guess)
            print(hint)
            current_score = calculate_score(initial_score, attempts, max_attempts)
            print(f"Current score: {current_score}")
    else:
        print(f"\n💔 Game Over! The number was {number_to_guess}")
        print("Better luck next time!")

if __name__ == "__main__":
    main()