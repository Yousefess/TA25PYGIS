import streamlit as st
import random


def initialize_game():
    """Initialize game state"""
    if 'number_to_guess' not in st.session_state:
        st.session_state.number_to_guess = random.randint(1, 100)
    if 'attempts' not in st.session_state:
        st.session_state.attempts = 0
    if 'game_over' not in st.session_state:
        st.session_state.game_over = False
    if 'guess_history' not in st.session_state:
        st.session_state.guess_history = []


def calculate_score(attempts):
    """Calculate score"""
    return max(100 - (attempts * 10), 0)


def reset_game():
    """Reset the game"""
    st.session_state.number_to_guess = random.randint(1, 100)
    st.session_state.attempts = 0
    st.session_state.game_over = False
    st.session_state.guess_history = []


def main():
    st.set_page_config(page_title="Number Guessing Game", page_icon="🎯")

    # Initialize game
    initialize_game()

    # Title
    st.title("🎯 Number Guessing Game")
    st.write("I'm thinking of a number between 1 and 100. Can you guess it?")

    # Game information
    st.sidebar.header("Game Info")
    st.sidebar.write(f"Attempts: {st.session_state.attempts}/10")
    st.sidebar.write(f"Remaining: {10 - st.session_state.attempts}")

    # Reset button
    if st.sidebar.button("New Game"):
        reset_game()

    # Main game area
    if not st.session_state.game_over and st.session_state.attempts < 10:
        # Guess input
        guess = st.number_input("Enter your guess:",
                                min_value=1, max_value=100, step=1)

        if st.button("Submit Guess"):
            st.session_state.attempts += 1
            st.session_state.guess_history.append(guess)

            # Check guess
            if guess == st.session_state.number_to_guess:
                st.session_state.game_over = True
                st.success("🎉 Congratulations! You guessed it!")
                st.balloons()
            else:
                # Provide hint
                if guess < st.session_state.number_to_guess:
                    st.info("📈 Try a higher number!")
                else:
                    st.info("📉 Try a lower number!")

                # Show attempts info
                st.write(f"Attempts used: {st.session_state.attempts}/10")

    # Game over conditions
    if st.session_state.attempts >= 10 and not st.session_state.game_over:
        st.session_state.game_over = True
        st.error(
            f"💔 Game Over! The number was {st.session_state.number_to_guess}")

    # Display results when game is over
    if st.session_state.game_over:
        score = calculate_score(st.session_state.attempts)
        st.write(f"**Final Score:** {score}")
        st.write(f"**Total Attempts:** {st.session_state.attempts}")

        if st.button("Play Again"):
            reset_game()
            st.rerun()

    # Guess history
    if st.session_state.guess_history:
        st.subheader("Your Guesses:")
        for i, g in enumerate(st.session_state.guess_history, 1):
            if g == st.session_state.number_to_guess:
                st.write(f"Attempt {i}: {g} ✅")
            else:
                st.write(f"Attempt {i}: {g}")

    # Instructions
    with st.expander("How to Play"):
        st.write("""
        1. I'll think of a random number between 1-100
        2. You have up to 10 attempts to guess it
        3. After each guess, I'll tell you if you need to go higher or lower
        4. Your score starts at 100 and decreases by 10 points per attempt
        5. Try to find the number with the fewest attempts!
        """)


if __name__ == "__main__":
    main()
