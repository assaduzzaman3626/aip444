import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

print("AIP444 Fall 2026 - Lab 01")
print("git-cm: MD ASSADUZZAMAN - 122963242")
print("Run Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
print("----------------------------------------------")

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    print("Error: OPENROUTER_API_KEY not found")
    exit()

import subprocess

# Get staged Git changes

result = subprocess.run(
    ["git", "diff", "--staged"],
    capture_output=True,
    text=True,
    encoding="utf-8"
)
diff = result.stdout.strip()

if not diff:
    print("❌ No staged changes found")
    exit()

print(f"✅ Diff found: {len(diff)} characters")

# Connect to OpenRouter AI
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key
)

# Choose an AI model
MODEL_1 = "google/gemma-3-27b-it"
MODEL_2 = "meta-llama/llama-3.3-70b-instruct"

DEFAULT_MODEL = MODEL_1

# Check if creative mode is enabled
is_creative = "--creative" in sys.argv

if is_creative:
    temperature = 1.2
    system_prompt = (
        "You are a funny cowboy from the Wild West. "
        "Write a Git commit message using cowboy slang and Gitmoji. "
        "Make it creative but accurately describe the code changes. "
        "Return only the commit message."
    )
    models = [MODEL_1, MODEL_2]
else:
    temperature = 0.1
    system_prompt = (
        "Write a Git commit message using Conventional Commits. "
        "Example: feat: add login functionality. "
        "Describe the staged code changes accurately. "
        "Return only the commit message."
    )
    models = [DEFAULT_MODEL]

# Generate commit messages
for model in models:
    print(f"\nAsking AI model: {model}")

    try:
        response = client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": diff
                }
            ]
        )

        print("AI Generated Commit Message:")
        print(response.choices[0].message.content)

    except Exception as error:
        print(f"Error: {error}")

# Lab 01: Creative mode testing completed
