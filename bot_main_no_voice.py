import os
import logging
from dotenv import load_dotenv
from data_manager_json import DataManager
from cogs.command_handler import MCOCCommands

# Setup logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()

# Bot configuration
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
PREFIX = '!'

# Import only the core Discord components we need to avoid audioop issue
try:
    import discord
    from discord.ext import commands
except ImportError as e:
    print(f"Import error: {e}")
    print("This may be due to audioop module not being available in your Python installation.")
    exit(1)

# For this bot, we don't need voice functionality, so we'll use minimal intents
intents = discord.Intents.default()
intents.message_content = True  # Required to read message content

bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

# Initialize data manager
data_manager = DataManager()

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guilds')
    print(f'Bot is watching over {len(bot.users)} users')
    
    # Load champion data when bot starts
    try:
        print("Loading champion data...")
        data_manager.fetch_champions_from_spreadsheets()
        print(f"Loaded data for {sum(len(v) for v in data_manager.champions_data.values())} champions")
    except Exception as e:
        print(f"Error loading champion data: {e}")
        logging.error(f"Error loading champion data: {e}")

    # Add command cog
    await bot.add_cog(MCOCCommands(bot, data_manager))

@bot.command(name='help')
async def help_command(ctx):
    """Display available commands"""
    help_text = """
**MCOC Champions Bot Commands:**
`!champion <name>` - Get tier and information about a specific champion
`!pulls` - Get current recommendations for champion pulls
`!rankup` - Get general suggestions for champions to rank up
`!rankup <name>` - Get specific rank-up advice for a champion
`!tierlist` - Get the full tier list
`!refresh` - Manually refresh data from public sheets
`!help` - Show available commands
    """
    await ctx.send(help_text)

@bot.command(name='ping')
async def ping(ctx):
    """Test command to check if bot is responsive"""
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')

if __name__ == "__main__":
    if not TOKEN:
        print("Error: DISCORD_BOT_TOKEN not found in environment variables")
        exit(1)
    
    bot.run(TOKEN)