# ask.py - Week 3 homework: my first API call, run from Cursor's terminal.
# Run it with: python ask.py
# The key is asked with getpass, so it is hidden and NEVER stored in this file.
from getpass import getpass

from google import genai

api_key = getpass("Paste your API key and press Enter: ")
client = genai.Client(api_key=api_key)


def ask(question):
    """Send one question to Gemini and return the answer as a string."""
    interaction = client.interactions.create(
        model="gemini-3.8-flash",
        input=question,
    )
    return interaction.output_text


print(ask("Name three items a food bank should always have in stock."))
