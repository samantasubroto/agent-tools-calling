"""Tool implementations and their JSON schemas.

To add a tool: write a function, add a schema to TOOL_SCHEMAS,
and register the function in TOOL_FUNCTIONS.
"""

import random
from datetime import datetime, timezone


def get_current_time(timezone_name: str = "UTC") -> str:
    """Return the current time in ISO format (UTC only in this demo)."""
    return datetime.now(timezone.utc).isoformat()


def add(a: float, b: float) -> float:
    return a + b


def random_number_generation() -> int:
    """Return a random integer from 1 to 100 (inclusive)."""
    return random.randint(1, 100)


# What the model sees: name, description, and input schema.
TOOL_SCHEMAS = [
    {
        "name": "get_current_time",
        "description": "Get the current date and time in ISO 8601 format.",
        "input_schema": {
            "type": "object",
            "properties": {
                "timezone_name": {
                    "type": "string",
                    "description": "Timezone name. Only 'UTC' is supported.",
                }
            },
            "required": [],
        },
    },
    {
        "name": "add",
        "description": "Add two numbers and return the sum.",
        "input_schema": {
            "type": "object",
            "properties": {
                "a": {"type": "number", "description": "First number"},
                "b": {"type": "number", "description": "Second number"},
            },
            "required": ["a", "b"],
        },
    },
    {
        "name": "random_number_generation",
        "description": "Generate a random integer from 1 to 100 (inclusive).",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
]

# What your code runs when the model asks for a tool.
TOOL_FUNCTIONS = {
    "get_current_time": get_current_time,
    "add": add,
    "random_number_generation": random_number_generation,
}
