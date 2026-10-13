import random


def main():
    # Pick a random whole number between 1 and 10 (both included).
    secret_number = random.randint(1, 10)

    # Give the player at most 3 tries.
    max_attempts = 3

    print("Welcome to the Number Guessing Game!")
    print("I'm thinking of a number between 1 and 10.")
    print(f"You have {max_attempts} attempts to guess it.")

    # Loop once per attempt, from 1 up to max_attempts.
    for attempt in range(1, max_attempts + 1):
        # Read the player's guess from the keyboard.
        raw_guess = input(f"Attempt {attempt}/{max_attempts} - Enter your guess: ")

        # Make sure the input is a number; skip the attempt if it isn't.
        if not raw_guess.strip().isdigit():
            print("Please enter a whole number.")
            continue

        guess = int(raw_guess)

        # Compare the guess with the secret number.
        if guess < secret_number:
            print("Too low!")
        elif guess > secret_number:
            print("Too high!")
        else:
            # Correct guess: celebrate and end the game.
            print(f"Correct! You guessed it in {attempt} attempt(s).")
            break
    else:
        # This runs only if the loop finished without a correct guess.
        print(f"Out of attempts! The number was {secret_number}.")

    # Friendly closing message in every case.
    print("Thanks for playing! Goodbye.")


# Run the game only when this file is executed directly.
if __name__ == "__main__":
    main()
