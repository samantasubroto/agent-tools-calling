# Tool calling playground

A small Python project for learning LLM tool calling with the Anthropic API.

## Setup

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then put your API key in .env
```

## Run

```sh
python main.py
python main.py "What is 17.5 + 4.25?"
```

## Files

- `tools.py`: tool functions, JSON schemas, and the name-to-function registry.
- `main.py`: the request, tool_use, tool_result loop.

## Ideas to try

- Add a tool (weather lookup, file reader, calculator with more operations).
- Make the model call two tools in one turn and inspect the output.
- Return an error from a tool and watch how the model recovers.
- Set `tool_choice` in `client.messages.create` to force or forbid a tool.
