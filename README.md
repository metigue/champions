# MCOC Champions Discord Bot

A Discord bot designed to provide recommendations and insights for MARVEL Contest of Champions (MCoC) players based on community-created tier lists and champion data.

## Overview

This Discord bot helps players in your MCOC alliance make informed decisions about:
- Which champions to pull for
- Champion rankings and tier lists
- Recommendations on which champions to rank up
- Champion effectiveness for different game modes

The bot pulls data from public community tier lists to provide up-to-date recommendations based on the current meta.

## Features

- **Champion Tier Lookup**: Query any champion to see their current tier ranking
- **Pull Recommendations**: Get advice on which champions to pull for based on current meta
- **Rank Up Suggestions**: Recommendations on which champions to prioritize for advancement
- **Meta Insights**: Information about current game meta and champion effectiveness
- **Category Filtering**: View champions by type (Cosmic, Mutant, Tech, etc.)
- **Champion Comparison**: Compare multiple champions to determine best rank-up choice

## Setup

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Discord account and ability to create a bot

### Installation

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd ChampionsDiscordBot
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Discord Bot Setup

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Create a bot for your application
4. Copy the bot token and save it for later
5. Under "OAuth2" > "URL Generator", select:
   - Scopes: `bot`
   - Bot Permissions: `Send Messages`, `Read Message History`
6. Use the generated URL to invite your bot to your server

### Environment Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file with your bot token:
   ```
   DISCORD_BOT_TOKEN=your_actual_bot_token_here
   ```

## Running the Bot

1. Make sure your virtual environment is activated:
   ```bash
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

2. Build the champion database:
   ```bash
   python build_database.py
   ```

3. Run the bot:
   ```bash
   python bot_main.py
   ```

## Commands

- `!champion <name>` - Get tier and information about a specific champion
- `!pulls` - Get current recommendations for champion pulls
- `!rankup` - Get suggestions for champions to rank up
- `!rankup <name1>, <name2>, <name3>` - Compare multiple champions and get recommendations
- `!tierlist` - Get the full tier list
- `!refresh` - Manually refresh data from public sheets
- `!help` - Show available commands

## Champion Comparison Feature

The `!rankup` command now supports comparing multiple champions at once. Simply provide comma-separated names:
```
!rankup doctor doom, nico minoru, gwenpool
```

The bot will calculate scores based on:
- Battlegrounds rating (or 5 if none)
- Champion type (Attacker=+1, Dual Threat=+2, Defender=0)
- Class ranking (50 - rank number, minimum 5)

It will then provide appropriate recommendations based on the score differences.

## Development

The bot is organized into the following modules:

- `bot_main.py` - Main bot application and entry point
- `build_database.py` - Builds the JSON database from Google Sheets
- `data_manager_json.py` - Handles JSON database loading
- `champion_model.py` - Data classes for champion information
- `cogs/command_handler.py` - Command processing and response formatting
- `config.py` - Configuration settings
- `requirements.txt` - Python dependencies