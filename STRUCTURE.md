# MCOC Champions Discord Bot - Project Structure

## Directory Structure
```
ChampionsDiscordBot/
├── bot_main.py                 # Main bot application entry point
├── requirements.txt            # Python dependencies
├── config.py                   # Configuration settings
├── .env.example               # Example environment variables file
├── README.md                  # Project overview
├── SETUP.md                   # Setup instructions
├── plan.md                    # Implementation plan
├── champion_model.py          # Data classes for champion information
├── data_manager.py            # Public Google Sheets web scraping and data processing
├── cogs/                      # Discord bot cogs (commands)
│   ├── __init__.py
│   └── command_handler.py     # Command processing and response formatting
├── utils/                     # Utility functions
│   ├── __init__.py
│   └── champion_utils.py      # Champion name normalization and matching utilities
├── data/                      # Data files (if any)
│   └── __init__.py
├── tests/                     # Test files
│   ├── __init__.py
│   └── test_data_manager.py   # Unit tests
```

## Architecture Overview

### Core Components

1. **`bot_main.py`**: The entry point of the application that initializes the Discord bot, sets up intents, loads champion data, and registers the command cog.

2. **`data_manager.py`**: Handles web scraping of public Google Sheets, data retrieval, processing, and caching. It manages data from both spreadsheet sources and provides methods to query the data.

3. **`champion_model.py`**: Contains data class definitions for champions and recommendations, providing a structured way to handle champion information.

4. **`cogs/command_handler.py`**: Implements the Discord commands and their logic, including champion lookup, recommendations, and formatting responses for Discord.

5. **`utils/champion_utils.py`**: Contains utility functions for champion name normalization, fuzzy matching, and other helper functions.

### Data Flow

1. At startup, `bot_main.py` initializes `DataManager` and loads champion data from public Google Sheets via web scraping
2. When a user issues a command, `MCOCCommands` cog processes the request
3. The command handler uses `DataManager` to retrieve relevant champion data
4. Results are formatted appropriately for Discord and sent as responses

### Key Features Implemented

- **Web Scraping Integration**: Automatic fetching and processing of champion data from both public spreadsheet sources
- **Champion Lookup**: Search and retrieve information about any champion by name
- **Pull Recommendations**: Suggestions on which champions to focus on pulling for
- **Rank-Up Recommendations**: Guidance on which champions to prioritize for advancement
- **Fuzzy Matching**: Improved name matching for champion lookups
- **Modular Design**: Clean separation of concerns with dedicated modules for different functionality

### Configuration and Security

- Environment variables for sensitive information like bot tokens
- No API credentials needed - uses public sheet access
- Structured configuration settings for easy customization
- Proper error handling and logging