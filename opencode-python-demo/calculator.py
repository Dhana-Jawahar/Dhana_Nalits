def get_number(prompt):
    """Ask the user for a number and return it as a float."""
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Please enter a valid number.")


def main():
    """Add two numbers entered by the user."""
    first = get_number("Enter the first number: ")
    second = get_number("Enter the second number: ")
    total = first + second
    print(f"The sum of {first} and {second} is {total}.")


if __name__ == "__main__":
    main()
