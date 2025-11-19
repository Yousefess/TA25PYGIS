# Number Guessing Game Project

The Number Guessing Game is an interactive Python application that challenges users to guess a randomly generated number within a specified range. This project demonstrates core programming concepts through two distinct implementations: a web-based interface using Streamlit and a console-based version for terminal usage. The game provides an engaging way to learn about user input handling, game state management, and interactive application development.

The project delivers the following key features:

- **Random Number Generation**: The game generates a random number between 1-100 that players must guess within a limited number of attempts.
- **Interactive Gameplay**: Users receive real-time feedback on their guesses with hints to guide them toward the correct number.
- **Dual Interface Options**: A Streamlit-based web interface for modern web interaction and a console version for traditional terminal gameplay.
- **Score Tracking**: The game calculates scores based on performance, rewarding players who guess correctly with fewer attempts.
- **Game History**: Players can review their guessing history and track their progress throughout the game.

In this project, you will learn how to build interactive applications in Python, manage application state, handle user inputs, and create engaging user interfaces using both web technologies and console applications.

## Features

### Web Version (Streamlit)
- 🎯 **Interactive Web Interface**: Modern, responsive UI accessible through web browsers
- 📊 **Real-time Feedback**: Instant hints and attempt tracking
- 🏆 **Score Calculation**: Dynamic scoring system based on performance
- 📝 **Guess History**: Complete record of all attempts with visual indicators
- 🔄 **Game Management**: Easy reset and replay functionality

### Console Version
- ⚡ **Lightweight Execution**: Fast, terminal-based gameplay
- 🎮 **Classic Experience**: Traditional text-based gaming interface
- ✅ **Input Validation**: Robust error handling for user inputs
- 📈 **Progressive Hints**: Smart hint system that guides players effectively

## Requirements

To run this project, you will need:

- Python 3.7 or higher installed on your machine
- For the web version: Internet connection for initial Streamlit setup
- Required Python libraries (install via `requirements.txt`):
  - `streamlit` (for web version)
  - `random` (built-in Python module)

## Project Structure

```
Number Guesser Game/
│
├── README.md                 # Project documentation
├── requirements.txt          # Python dependencies
└── src
    ├── app.py         # Web version using Streamlit
    └── game.py          # Console-based version
```

## Installation & Setup

1. **Clone or download the project files**
2. **Install required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the web version**:
   ```bash
   streamlit run app.py
   ```
4. **Run the console version**:
   ```bash
   python game.py
   ```

## How to Play

### Web Version
1. Open the application in your web browser
2. Read the instructions in the "How to Play" section
3. Enter your guess in the number input field
4. Click "Submit Guess" to check your answer
5. Use the hints provided to adjust your next guess
6. Try to find the number within 10 attempts for maximum score
7. View your guessing history and final score
8. Click "Play Again" to start a new game

### Console Version
1. Run the Python script in your terminal
2. Follow the on-screen prompts to enter your guesses
3. Receive immediate feedback and hints
4. Track your attempts and remaining chances
5. Achieve the highest score by guessing correctly in fewer attempts

## Learning Outcomes

By exploring and extending this project, learners will be able to:

- Implement random number generation and game logic in Python
- Build interactive web applications using Streamlit
- Manage application state and session data
- Handle user inputs and validate data
- Create engaging user interfaces for games
- Understand game loop mechanics and state management
- Develop both web-based and console applications
- Implement scoring systems and game progression
- Apply software architecture principles to game development

## Technical Features

- **Session State Management**: Persistent game state across interactions
- **Input Validation**: Robust error handling for user inputs
- **Modular Code Structure**: Organized, maintainable code with separate functions
- **Responsive Design**: Adaptive UI that works on different screen sizes
- **Score Algorithm**: Mathematical scoring based on performance metrics

---

*Enjoy the game and happy coding! 🎯*