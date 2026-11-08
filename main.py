"""Minimal tool-calling loop using the OpenAI API.

Flow:
1. Send the user message plus tool schemas to the model.
2. If the response has tool_calls, run each requested tool locally.
3. Send the results back as "tool" role messages.
4. Repeat until the model answers with plain text.
"""

import json
import os
import sys

from dotenv import load_dotenv
from openai import OpenAI

from email_tools import (
    EMAIL_TOOL_FUNCTIONS,
    EMAIL_TOOL_SCHEMAS,
    REQUIRES_CONFIRMATION,
)
from tools import TOOL_FUNCTIONS as _BASE_FUNCTIONS
from tools import TOOL_SCHEMAS as _BASE_SCHEMAS
from web_tools import WEB_TOOL_FUNCTIONS, WEB_TOOL_SCHEMAS

TOOL_FUNCTIONS = {**_BASE_FUNCTIONS, **WEB_TOOL_FUNCTIONS, **EMAIL_TOOL_FUNCTIONS}
TOOL_SCHEMAS = _BASE_SCHEMAS + WEB_TOOL_SCHEMAS + EMAIL_TOOL_SCHEMAS

load_dotenv()

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
client = OpenAI()  # reads OPENAI_API_KEY from the environment

# tools.py uses the Anthropic-style schema ("input_schema").
# OpenAI expects {"type": "function", "function": {..., "parameters": ...}}.
OPENAI_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": t["name"],
            "description": t["description"],
            "parameters": t["input_schema"],
        },
    }
    for t in TOOL_SCHEMAS
]


def run_tool(name: str, tool_input: dict) -> str:
    """Run a tool locally and return its output as a string."""
    func = TOOL_FUNCTIONS.get(name)
    if func is None:
        return f"Unknown tool: {name}"
    if name in REQUIRES_CONFIRMATION:
        print(f"\n--- '{name}' wants to run with: ---")
        for key, value in tool_input.items():
            print(f"{key}: {value}")
        print("-----------------------------------")
        answer = input("Allow? [y/N] ").strip().lower()
        if answer != "y":
            return "The user declined to run this tool."
    try:
        return str(func(**tool_input))
    except Exception as exc:  # report errors back to the model
        return f"Error: {exc}"


def chat(user_message: str) -> str:
    messages = [{"role": "user", "content": user_message}]

    while True:
        response = client.chat.completions.create(
            model=MODEL,
            tools=OPENAI_TOOLS,
            messages=messages,
        )
        message = response.choices[0].message
        messages.append(message)

        if not message.tool_calls:
            return message.content or ""

        for call in message.tool_calls:
            args = json.loads(call.function.arguments or "{}")
            print(f"[tool call] {call.function.name}({args})")
            output = run_tool(call.function.name, args)
            print(f"[tool result] {output}")
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": output,
                }
            )


if __name__ == "__main__":
    prompt = " ".join(sys.argv[1:]) or "What is 1234 + 5678, and what time is it now?"
    print(chat(prompt))
