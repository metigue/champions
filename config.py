# MCOC Discord Bot Configuration

# Discord bot settings
DISCORD_BOT_TOKEN = ""  # Your Discord bot token
COMMAND_PREFIX = "!"

# Google Sheet URLs (CSV export format)
# To update: Get the sheet ID from the URL and use format:
# https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}
SHEET_URLS = {
    "battlegrounds": "https://docs.google.com/spreadsheets/d/111Xo45fxQxDzlWjjtvu1KqdNea0hHeRDdpbTrgIDS4A/export?format=csv&gid=0",
    "pve": "https://docs.google.com/spreadsheets/d/1C-jcb0zED4VoSZ26lVTW7KKyE17u3Cj1kPZdqn8MAnU/export?format=csv&gid=0",
    "pvp": "https://docs.google.com/spreadsheets/d/1fZ4nZeBZJjmPRSyWC1LY9XubfI3pPyJeYP2Aw9KVgJU/export?format=csv&gid=0",
}

# Data refresh settings
AUTO_REFRESH_INTERVAL_HOURS = 6  # How often to automatically refresh data from public sheets