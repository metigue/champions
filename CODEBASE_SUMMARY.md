# MCOC Champions Discord Bot - Codebase Overview

This document provides a high-level overview of the MCOC Champions Discord Bot codebase. The bot is designed to provide recommendations and information about champions in the mobile game Marvel Contest of Champions, based on data from public Google Sheets. The bot can provide general rank-up advice, specific information about a champion, and help users pick the best champions for Battlegrounds.

## Architecture and Components

### Core Components
- `bot_main.py`: Main bot application and entry point
- `champion_model.py`: Data classes for champion information
- `data_manager_json.py`: Data manager using JSON database
- `data_manager.py`: Data manager for live Google Sheet scraping
- `build_database.py`: Builds the JSON database from Google Sheets
- `cogs/command_handler.py`: Command processing and response formatting
- `champions_database.json`: JSON database containing champion data
- `requirements.txt`: Python dependencies

### Data Processing Flow
1. The bot fetches data from public Google Sheets
2. The data is processed and stored in the JSON database
3. Commands query the database and return formatted responses

## Key Methods Documentation

### build_database.py
- `build_champion_database()`: Main function that fetches data from both Google Sheets and builds the comprehensive JSON database
  - Fetches Champion Tier List and Battlegrounds Tier List sheets
  - Processes champion data with proper ranking assignment using column-based ranking system
  - Creates champion entries with class, rank, tier, and battlegrounds data
  - Implements fuzzy matching for champion names that vary between sheets
  - Handles special characters like apostrophes and periods in champion names
  - Assigns rankings following the spreadsheet column-based numbering system with proper off-by-one error fix
  - Properly parses class headers and data rows including header row champions

### champion_model.py
- `Champion` dataclass: Represents a champion with all relevant information
  - `name`: String - Champion's name (e.g., "Spider-Man (Supreme)")
  - `class_`: String - Champion's class (Mystic, Science, Skill, Mutant, Tech, Cosmic)
  - `rank`: Integer - Champion's position in their class ranking (e.g., Skill #14)
  - `tier`: String - Champion's tier category (e.g., "Pretty Good", "Phenomenal")
  - `rating`: Float - Battlegrounds rating (0-10, optional)
  - `battlegrounds_type`: String - Battlegrounds type (Attackers, Defenders, Dual Threat)
  - `symbols`: List[str] - Emoji symbols with special meanings
  - `source`: String - Either "champion_tier_list", "battlegrounds_only", or "combined"

### data_manager_json.py
- `DataManager` class: Handles loading and searching champion data from JSON file
  - `__init__()`: Loads the JSON database file and creates index for fast lookups
  - `get_champion_by_name(name: str)`: Finds champions by name with fuzzy matching
    - Handles champion names with variations across both sheets
    - Returns Champion objects that match the search query

### cogs/command_handler.py
- `CommandHandler` class: Processes commands and generates responses
  - `get_champion_rankup_info(name: str)`: Generates detailed rankup information for a single champion
    - Formats output with name, battlegrounds rating/type, class ranking, and special notes
    - Uses the new ranking system with "Class Ranking: Class #N" format
  - `get_rankup_recommendations(champion_names: str)`: Compares multiple champions and recommends the best for rank-up
    - Calculates scores based on battlegrounds ratings and class rankings
    - Factors in both battlegrounds rating and ranking position for recommendations
    - Properly formats responses with proper rankings and ratings
  - `pick_champions_for_battlegrounds(count: int, champion_names: str)`: Selects the best N champions for battlegrounds
    - Ranks champions based on battlegrounds ratings (with bonuses for Dual Threat)
    - Factors in class rankings for tie-breaking
    - Returns top N champions based on battlegrounds effectiveness

## Known Issues and Important Fixes

### Parsing Special Character Names
Previously, champions with special characters like Mr. Knight (period) and Chee'ilth (apostrophe) were not being parsed correctly. Fixed by ensuring proper emoji stripping and name processing.

### Ranking Off-by-One Error
Previously, champions were being assigned ranks incorrectly due to incorrect row counting in the column-based ranking algorithm. Fixed by ensuring both counting and assignment passes use the same row range (starting at the class header row).

### Multi-Sheet Champion Matching
Champions with different names across sheets (e.g., "Spider-Man (Supreme)" in champion tier list vs "Spidey Supreme" in battlegrounds sheet) are now properly matched using fuzzy matching with known name variations.

### Missing Champions at End of Columns
Previously, champions in the header row for each class were being skipped during ranking assignment. Fixed by ensuring the algorithm processes the class header row as well as subsequent data rows.

## File-by-File Breakdown

- `data_manager.py`: Fetches and parses champion data from multiple Google Sheets, including the main tier list and Battlegrounds-specific data.
- `champion_model.py`: Defines the `Champion` and `ChampionRecommendation` data classes, providing a structured way to store champion information and recommendations.
- `build_database.py`: A script that fetches data from the Google Sheets, processes it, and builds the `champions_database.json` file, which serves as the local database for the application.
- `bot_main.py`: The main entry point for the Discord bot, responsible for initializing the bot, loading data, and registering command handlers.
- `bot_main_no_voice.py`: An alternative entry point for the bot that attempts to avoid importing voice-related features.
- `config.py`: Contains basic configuration settings for the Discord bot, such as the bot token, command prefix, and data refresh interval.
- `cogs/command_handler.py`: Implements the core logic for the bot's commands, such as `rankup` and `pick`, and includes the `MCOCCommands` cog that registers these commands with the bot.
- `utils/champion_utils.py`: Provides utility functions for normalizing and fuzzy-matching champion names to ensure consistent lookups.
- `data_manager_json.py`: A data manager that loads champion data from the `champions_database.json` file, providing a way to access the data without re-fetching from the Google Sheets.
- `requirements.txt`: Lists the Python packages required for the project.
- `Dockerfile`: Contains instructions for building a Docker image for the bot.
- `.gitignore`: Specifies which files and directories to ignore in Git version control.
- `README.md`: Provides an overview of the project and instructions for setting it up.
- `SETUP.md`: A document detailing the setup process.
- `STATUS_SUMMARY.md`: A document summarizing the status of the project.
- `STRUCTURE.md`: A document outlining the structure of the project.
- `todo.md`: A todo list for the project.
- `test_*.py`: Various test files for different parts of the application.
- `debug_*.py`: Various debug scripts for testing specific functionalities.
- `check_*.py`: Various scripts for checking specific data points.
- `show_top_by_class.py`: A script to display the top champions by class.
- `examine_new_sheet.py`: A script to examine the new spreadsheet.
- `list_of_champions.txt`: A plain text file listing champion names.
- `clean_pick_function.txt`: A text file containing a cleaned version of the pick function.
- `full_build.txt`: A text file with the full build output.
- `build_debug.txt`: A text file with debug output from the build process.
- `science_debug.txt`: A text file with debug output related to the science class.
- `debug_output.txt`: A text file with general debug output.
- `build_output.txt`: A text file with the build output.
- `test_output.txt`: A text file with test output.
- `plan.md`: A markdown file with the project plan.
- `.env.example`: An example environment file.
- `QWEN.md`: A markdown file with some notes.

## Key Commands and Workflows

This section explains how to perform common tasks like updating the champion database and running tests.

### Updating the Champion Database

The champion data is sourced from public Google Sheets and stored in the `champions_database.json` file. To update this database with new information, you need to run the `build_database.py` script.

**To update from new Google Sheets URLs:**

1.  **Modify `build_database.py`**: Open the `build_database.py` file and replace the URLs in the `champion_tier_list_url` and `battlegrounds_tier_list_url` variables with the new Google Sheets URLs.

    ```python
    # URLs for the spreadsheets
    champion_tier_list_url = "https://docs.google.com/spreadsheets/d/NEW_CHAMPION_TIER_LIST_ID/export?format=csv&gid=0"
    battlegrounds_tier_list_url = "https://docs.google.com/spreadsheets/d/NEW_BATTLEGROUNDS_TIER_LIST_ID/export?format=csv&gid=0"
    ```

2.  **Run the script**: Execute the following command in your terminal to rebuild the database.

    ```bash
    python3 build_database.py
    ```

    This will fetch the data from the new URLs, process it, and overwrite the `champions_database.json` file.

### Running Tests

The project includes a `tests` directory with various test files. These tests are designed to be run as standalone scripts.

To run a test, you need to set the `PYTHONPATH` to the root of the project so that the test files can find the other modules.

**Example:**

```bash
PYTHONPATH=. python3 tests/test_data_manager.py
```

You can run other test files in a similar way.

### Note on the Python Environment

This project includes a virtual environment in the `venv_alt` directory. While activating this virtual environment (`source venv_alt/bin/activate`) is recommended, it may not resolve all dependency issues in every environment.

Specifically, running scripts that import `discord.py` (such as `test_rankup_command.py`) may fail with a `ModuleNotFoundError: No module named 'audioop'`. This is an issue with the Python environment and its installation of the `discord.py` library, not a bug in the project's code.