import os
import subprocess


def is_safe_filename(filename):
    """Return True only for a simple filename with no folder parts.

    This blocks directory traversal ("..") and any path separators so the
    program can never be tricked into writing outside the current folder.
    """
    if "/" in filename or "\\" in filename:
        return False
    if filename in (".", ".."):
        return False
    if os.path.isabs(filename):
        return False
    if ".." in filename:
        return False
    return True


def build_ai_prompt(user_prompt):
    """Wrap the user's request with instructions for the OpenCode agent.

    The user's original wording is kept unchanged; we only add instructions
    that tell the agent to use the age-based-poetry skill.
    """
    instructions = (
        "Use the age-based-poetry skill to write the poem or song described below.\n"
        "Follow that skill to choose the writing style, vocabulary, structure, "
        "and rhyme scheme for the age group mentioned in the request.\n\n"
        "Return ONLY the finished poem or song in Markdown. Start with a single "
        "H1 title (for example: # My Title). Do not add explanations, notes, or "
        "code fences, and do not create or edit any files.\n\n"
        "User request: "
    )
    return instructions + user_prompt


def clean_output(text):
    """Drop any stray preamble before the first Markdown heading.

    The agent sometimes prints a short status line before the poem. We keep
    everything from the first line that starts with "# " so the saved file
    begins with the title.
    """
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.lstrip().startswith("# "):
            return "\n".join(lines[index:]).strip()
    # No heading found, so return the text unchanged.
    return text.strip()


def generate_poem(user_prompt):
    """Run the OpenCode CLI and return the poem text.

    Raises RuntimeError with a friendly message if OpenCode is missing,
    fails, or returns nothing.
    """
    ai_prompt = build_ai_prompt(user_prompt)

    # Arguments are passed as a list, so the prompt is sent as one safe
    # argument. shell=True is NOT used, which prevents shell injection.
    command = ["opencode", "run", ai_prompt]

    try:
        # Capture stdout (the poem) and stderr (error messages) as text.
        result = subprocess.run(command, capture_output=True, text=True)
    except FileNotFoundError:
        # The 'opencode' command is not installed or not on the PATH.
        raise RuntimeError(
            "Could not find the 'opencode' command. Please install OpenCode "
            "and make sure it is on your PATH."
        )
    except OSError as error:
        # Any other problem starting the program (for example, no permission).
        raise RuntimeError("Could not start OpenCode: " + str(error))

    # A non-zero exit code means OpenCode reported an error.
    if result.returncode != 0:
        details = result.stderr.strip() or "OpenCode exited with an error."
        raise RuntimeError("OpenCode failed: " + details)

    # Make sure we actually received some text back.
    poem = clean_output(result.stdout)
    if not poem:
        raise RuntimeError("OpenCode returned no text.")

    return poem


def ask_prompt():
    """Keep asking until the user enters a non-empty poem prompt."""
    while True:
        user_prompt = input("Enter your poem prompt: ").strip()
        if user_prompt:
            return user_prompt
        print("Prompt cannot be empty. Please try again.")


def ask_filename():
    """Keep asking until the user enters a valid, safe filename."""
    while True:
        filename = input("Enter the output filename: ").strip()
        if not filename:
            print("Filename cannot be empty. Please try again.")
            continue
        if not is_safe_filename(filename):
            print("Please use a simple filename with no folders or slashes.")
            continue
        # Add the .md extension if the user did not provide it.
        if not filename.lower().endswith(".md"):
            filename = filename + ".md"
        return filename


def main():
    print("=== Poem and Song Generator ===")

    # Collect the two inputs from the user.
    user_prompt = ask_prompt()
    filename = ask_filename()

    # Build the full path inside the current project directory.
    output_path = os.path.join(os.getcwd(), filename)

    # Never overwrite an existing file without the user's permission.
    if os.path.exists(output_path):
        answer = input("'" + filename + "' already exists. Overwrite? (y/n): ")
        if answer.strip().lower() != "y":
            print("Cancelled. Nothing was written.")
            return

    # Ask OpenCode to generate the poem. On failure we stop here and do
    # NOT write any file, so no error text is ever saved.
    print("Asking OpenCode to write your poem...")
    try:
        poem = generate_poem(user_prompt)
    except RuntimeError as error:
        print("Error: " + str(error))
        return

    # Only write the file after a successful generation.
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(poem + "\n")

    # Confirm success and show the filename the user asked for.
    print("Success! Poem saved to " + filename)


if __name__ == "__main__":
    main()
