# MCP Weather & System Time Server

[Français 🇫🇷](./README.fr.md)

A simple Python Model Context Protocol (MCP) server exposing 3 tools for AI assistants:

| Tool | Description |
|---|---|
| `get_current_weather` | Current weather for a city (temperature, wind, humidity, visibility) |
| `get_forecast` | Forecast up to 5 days in 3-hour slots |
| `get_system_time` | Local system date/time and timezone info from your PC |

## Requirements

- Python 3.11+
- A free [OpenWeatherMap API key](https://openweathermap.org/api)

## Installation

```bash
# 1) Go to project folder
cd meteo

# 2) Create virtual environment
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # Linux/macOS

# 3) Install dependencies
pip install -r requirements.txt

# 4) Configure environment variable
copy .env.example .env
# Then edit .env and replace your_api_key_here
```

## Run MCP server

```bash
python server.py
```

The server runs over stdio (default), which is the expected mode for most MCP clients.

## Connect from an MCP client

Use this in your MCP client config (Claude Desktop / Cursor / OpenCode, etc.):

```json
{
  "mcpServers": {
    "weather-time": {
      "command": "python",
      "args": ["C:\\Users\\MZayim\\Desktop\\Projet\\ia GENERAL\\meteo\\server.py"],
      "env": {
        "OPENWEATHERMAP_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

> Update the absolute path to `server.py` for your machine.

## Example prompts

- “What’s the weather in Paris?” → `get_current_weather(city="Paris")`
- “Give me a 3-day forecast for Lyon” → `get_forecast(city="Lyon", days=3)`
- “What time is it on this PC?” → `get_system_time()`

## Security notes

- Do **not** commit your `.env` file.
- Use `.env.example` as template only.
- Rotate any token/secret that was ever pasted in chat, logs, or screenshots.

## Project structure

```text
meteo/
├── server.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── README.fr.md
```
