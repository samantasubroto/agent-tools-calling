"""Minimal agent: a loop where the model picks tools step by step.

Run: python agents_demo.py "your task"
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
from tools import TOOL_FUNCTIONS as BASE_FUNCTIONS
from tools import TOOL_SCHEMAS as BASE_SCHEMAS
from web_tools import WEB_TOOL_FUNCTIONS, WEB_TOOL_SCHEMAS

load_dotenv()

MODEL = os.getenv("OPENAI_MODEL", "gpt-5")
client = OpenAI()

SYSTEM_PROMPT = "You are a helpful assistant. Use tools to complete the user's task step by step. Only call a tool when it fits."
MAX_STEPS = 10

# ---- Register tools: base tools + the send_email tool -----------------------
TOOL_FUNCTIONS = {**BASE_FUNCTIONS, **WEB_TOOL_FUNCTIONS, **EMAIL_TOOL_FUNCTIONS}
TOOL_SCHEMAS = BASE_SCHEMAS + WEB_TOOL_SCHEMAS + EMAIL_TOOL_SCHEMAS

# Convert to the format OpenAI expects.
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
    """Run a tool locally. Asks the user first for tools that need approval."""
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


def chat(user_message):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    for _ in range(MAX_STEPS):  # step limit
        response = client.chat.completions.create(
            model=MODEL,
            tools=OPENAI_TOOLS,
            messages=messages,
        )
        message = response.choices[0].message
        messages.append(message)

        if not message.tool_calls:  # model decided it's done
            return message.content

        # run tools, append results
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

    return "Stopped: too many steps."


if __name__ == "__main__":
    prompt = " ".join(sys.argv[1:]) or "Get a random number and tell me the time."
    print(chat(prompt))
