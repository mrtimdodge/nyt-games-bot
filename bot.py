import os, discord, asyncio
from discord.ext import commands
from games.connections import ConnectionsCommandHandler
from games.pips import PipsCommandHandler
from games.strands import StrandsCommandHandler
from games.wordle import WordleCommandHandler
from utils.bot_utilities import BotUtilities
from utils.help_handler import HelpMenuHandler

def load_env_file(path: str | None = None, override: bool = False) -> None:
    """
    Load KEY=VALUE lines from a .env file into os.environ.
    - path: path to .env (defaults to repo root next to this file)
    - override: if True, overwrite existing environment variables
    """
    if path is None:
        path = os.path.join(os.path.dirname(__file__), ".env")
    try:
        with open(path, "r", encoding="utf-8") as fh:
            for raw in fh:
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if override or key not in os.environ:
                    os.environ[key] = val
    except FileNotFoundError:
        # no .env present — that's fine
        pass

# load .env (won't override real environment vars unless override=True)
load_env_file()

# turn off logging for webdriver manager
os.environ['WDM_LOG_LEVEL'] = '0'

# parse environment variables
token = os.getenv('DISCORD_TOKEN')
discord_env = os.getenv('DISCORD_ENV')
guild_id = os.getenv('GUILD_ID')

# build Discord client
intents = discord.Intents.all()
intents.members = True
client = discord.Client(intents=intents)
activity = discord.Game(name="?help")

# set up the bot
bot = commands.Bot(command_prefix='?', intents=intents, activity=activity, help_command=None)
bot.guild_id = int(guild_id) if guild_id.isnumeric() else -1
bot.utils = BotUtilities(client, bot)
bot.help_menu = HelpMenuHandler()

# create games
bot.connections = ConnectionsCommandHandler(bot.utils)
bot.strands = StrandsCommandHandler(bot.utils)
bot.wordle = WordleCommandHandler(bot.utils)
bot.pips = PipsCommandHandler(bot.utils)

# load the cogs
async def main():
    try:
        async with bot:
            for extension in ['cogs.members', 'cogs.owner']:
                try:
                    await bot.load_extension(extension)
                except Exception as e:
                    print(f"Failed to load extension '{extension}'.\n{e}")
            await bot.start(token, reconnect=True)
    except asyncio.exceptions.CancelledError as e:
        print('\nCaught user exit, exiting...')


# load the database when ready
@bot.event
async def on_ready():
    try:
        bot.connections.connect()
        bot.strands.connect()
        bot.wordle.connect()
        bot.pips.connect()
        print("Database loaded & successfully logged in.")
    except Exception as e:
        print(f"Failed to load database: {e}")

# run the bot
asyncio.run(main())
