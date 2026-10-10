import os
from datetime import datetime
from dotenv import load_dotenv

print("AIP444 Fall 2026 - Lab 01")
print("git-cm: MD ASSADUZZAMAN - 122963242")
print("Run Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
print("----------------------------------------------")

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    print("Error: OPENROUTER_API_KEY not found")
    exit()