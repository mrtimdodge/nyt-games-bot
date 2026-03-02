import os
import re
import random
import calendar
import discord, traceback
from datetime import time, timezone
from discord.ext import commands, tasks
from games.base_command_handler import BaseCommandHandler
from utils.bot_utilities import BotUtilities, NYTGame
from utils.giphy_handler import GiphyHandler
from utils.help_handler import HelpMenuHandler

# GIFs to send when someone solves Wordle in 2 guesses (random pick)
WORDLE_TWO_GUESS_GIFS = [
    "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExdjFvZWx4bzZkYzNxNmdoN3NraHRzNjA4aDR2ZXV0NDRhMThhYW5veiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/toKE0zZrzkjuLKBucs/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExdjFvZWx4bzZkYzNxNmdoN3NraHRzNjA4aDR2ZXV0NDRhMThhYW5veiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/yjXBxGI0Fm8UTfDRb2/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExOTJlMGd1eWR0ZDFlMWgxMGZkcWF5amszNXQyemdhdG02bDV3ZTJ1eSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/9PaFsBEVO4EOKok7de/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExOTJlMGd1eWR0ZDFlMWgxMGZkcWF5amszNXQyemdhdG02bDV3ZTJ1eSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/QVSn2cJoSqaTvgfQ2D/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExdjFvZWx4bzZkYzNxNmdoN3NraHRzNjA4aDR2ZXV0NDRhMThhYW5veiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/26gsqQxPQXHBiBEUU/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExdjFvZWx4bzZkYzNxNmdoN3NraHRzNjA4aDR2ZXV0NDRhMThhYW5veiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/AE7Qa6j57XuRzeMkgh/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExdjFvZWx4bzZkYzNxNmdoN3NraHRzNjA4aDR2ZXV0NDRhMThhYW5veiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/Su6sx7xA8AAK6mK9jD/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExdjFvZWx4bzZkYzNxNmdoN3NraHRzNjA4aDR2ZXV0NDRhMThhYW5veiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/u00BUvSb3L5cIQHhjw/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3ZzdxajBtZW8zZ3YzODV6dDl3djh5eTEwdWg3NW84Y3JvN216N290bCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/l0HlJHvYDbt0dbURi/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3cHR6aTc1a3Nld3c4Yzcza2c2YWt1eWxycW5lZHYxNnRndnp5Z2t2aCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/TLAgg2jUF3LXZHMXc5/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3OTEwZDJmNTcxeGVyaDh6ZGp5em0zN3JtbXdqaWh5dDY3b2I2bDl3aCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/xTiN0h0Kh5gH7yQYUw/giphy.gif"
]

# GIF to send when someone solves Wordle in 1 guess (tags @everyone)
WORDLE_ONE_GUESS_GIF = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNWFrcTIzc280ajh1czI5eGhsZ2diOWE5NmNqdTM5YWtjbG10M3doeiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/JRF85A7Bcl2YU/giphy.gif"  # Add Giphy GIF URL here

# 11pm EST = 04:00 UTC
_11PM_EST = time(hour=4, minute=0, tzinfo=timezone.utc)


class _ChannelProxy:
    """Minimal proxy so a TextChannel can be passed where commands.Context is expected."""
    def __init__(self, channel: discord.TextChannel):
        self.channel = channel

    async def send(self, *args, **kwargs):
        return await self.channel.send(*args, **kwargs)

    async def reply(self, *args, **kwargs):
        return await self.channel.send(*args, **kwargs)


class MembersCog(commands.Cog, name="Normal Members Commands"):
    # class variables
    bot: commands.Bot
    utils: BotUtilities
    help_menu: HelpMenuHandler
    giphy_handler: GiphyHandler

    # games
    connections: BaseCommandHandler
    strands: BaseCommandHandler
    wordle: BaseCommandHandler
    pips: BaseCommandHandler

    confirm_entries: bool = os.environ.get('CONFIRM_ENTRIES', 'False').lower() in ('true', '1', 't')

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.utils = self.bot.utils
        self.help_menu = self.bot.help_menu
        self.giphy_handler = self.bot.giphy_handler
        self.build_help_menu()

        self.connections = self.bot.connections
        self.strands = self.bot.strands
        self.wordle = self.bot.wordle
        self.pips = self.bot.pips

        self._mysql_db_name = os.environ.get('PIPS_MYSQL_DB_NAME', "pips")
        self.monthly_results_task.start()

    def cog_unload(self):
        self.monthly_results_task.cancel()

    #####################
    #   SCHEDULED TASKS #
    #####################

    @tasks.loop(time=_11PM_EST)
    async def monthly_results_task(self):
        today = self.utils.get_todays_date()
        if today.day != calendar.monthrange(today.year, today.month)[1]:
            return

        month_name = today.strftime('%B %Y')
        guild = self.bot.get_guild(self.bot.guild_id)
        if guild is None:
            return

        nyt_channel_id = os.environ.get('NYT_GAMES_CHANNEL')
        shared_channel = None
        if nyt_channel_id and nyt_channel_id.isnumeric():
            shared_channel = guild.get_channel(int(nyt_channel_id))

        for game_name, handler in [
            ('wordle', self.wordle),
            ('connections', self.connections),
            ('strands', self.strands),
            ('pips', self.pips),
        ]:
            if shared_channel is not None:
                channel = shared_channel
            else:
                channel = discord.utils.find(
                    lambda ch, g=game_name: g in ch.name.lower(),
                    guild.text_channels
                )
            if channel is not None:
                await channel.send(f"**📊 Final Monthly Results ({game_name.title()}): {month_name}!**")
                await handler.get_ranks(_ChannelProxy(channel), 'month')

    @monthly_results_task.before_loop
    async def before_monthly_results_task(self):
        await self.bot.wait_until_ready()

    #####################
    #   COMMAND SETUP   #
    #####################

    @commands.guild_only()
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        try:
            if message.author.id != self.bot.user.id and message.content.count("\n") >= 1:
                # parse non-puzzle lines from message
                user_id = str(message.author.id)
                first_line = message.content.splitlines()[0].strip()
                first_two_lines = '\n'.join(message.content.splitlines()[:2])
                # add entry to either Wordle or Connections
                if 'Wordle' in first_line and self.utils.is_wordle_submission(first_line):
                    content = '\n'.join(message.content.splitlines()[1:])
                    if self.wordle.add_entry(user_id, first_line, content):
                        if(self.confirm_entries):
                            await message.add_reaction('✅')
                        score_match = re.search(r'(\d)\/6', first_line)
                        if score_match:
                            score = int(score_match.group(1))
                            if score == 2 and WORDLE_TWO_GUESS_GIFS:
                                gif_url = random.choice(WORDLE_TWO_GUESS_GIFS)
                                await message.channel.send(f"{message.author.mention}\n{gif_url}")
                            elif score == 1 and WORDLE_ONE_GUESS_GIF:
                                await message.channel.send(f"@everyone {message.author.mention}\n{WORDLE_ONE_GUESS_GIF}")
                    else:
                        await message.add_reaction('❌')
                elif 'Connections' in first_line and self.utils.is_connections_submission(first_two_lines):
                    content = '\n'.join(message.content.splitlines()[2:])
                    if self.connections.add_entry(user_id, first_two_lines, content):
                        if(self.confirm_entries):
                            await message.add_reaction('✅')
                    else:
                        await message.add_reaction('❌')
                elif 'Strands' in first_line and self.utils.is_strands_submission(first_two_lines):
                    content = '\n'.join(message.content.splitlines()[2:])
                    if self.strands.add_entry(user_id, first_two_lines, content):
                        if(self.confirm_entries):
                            await message.add_reaction('✅')
                    else:
                        await message.add_reaction('❌')
                elif 'Pips' in first_line and self.utils.is_pips_submission(first_line):
                    content = '\n'.join(message.content.splitlines()[1:])
                    if self.pips.add_entry(user_id, first_line, content):
                        puzzle_id_title = re.findall(r'[\d,]+', first_line)
                        puzzle_id = int(str(puzzle_id_title[0]).replace(',', ''))
                        if(self.confirm_entries):
                            await message.add_reaction('✅')
                        if(await self.pips.is_triple_cookie(user_id, puzzle_id)):
                            self.giphy_handler.start()
                            link = await self.giphy_handler.random_request(tag="cookie monster @sesamestreet")
                            await message.channel.send(f"{message.author.mention} \n {link}")
                            await self.giphy_handler.close()
                    else:
                        await message.add_reaction('❌')
        except Exception as e:
            print(f"Caught exception: {e}")
            traceback.print_exception(e)

    @commands.guild_only()
    @commands.command(name="help")
    async def help(self, ctx: commands.Context, *args: str) -> None:
        if len(args) == 0:
            await ctx.reply(self.help_menu.get_all())
        elif len(args) == 1:
            await ctx.reply(self.help_menu.get_message(args[0]))
        else:
            await ctx.reply("Couldn't understand command. Try `?help <command>`.")

    @commands.guild_only()
    @commands.command(name='ranks', help='Show ranks of players in the server')
    async def get_ranks(self, ctx: commands.Context, *args: str) -> None:
        try:
            if len(args) >= 1 and args[0] == 'all':
                remaining_args = args[1:]
                for handler in [self.wordle, self.connections, self.strands, self.pips]:
                    await handler.get_ranks(ctx, *remaining_args)
            else:
                [handler, handler_args] = self.get_command_handler_and_args(ctx, args)
                await handler.get_ranks(ctx, *handler_args)
        except Exception as e:
            print(f"Caught exception: {e}")
            traceback.print_exception(e)

    @commands.guild_only()
    @commands.command(name='missing', help='Show all players missing an entry for a puzzle')
    async def get_missing(self, ctx: commands.Context, *args: str) -> None:
        try:
            [handler, handler_args] = self.get_command_handler_and_args(ctx, args)
            await handler.get_missing(ctx, *handler_args)
        except Exception as e:
            print(f"Caught exception: {e}")
            traceback.print_exception(e)

    @commands.guild_only()
    @commands.command(name='entries', help='Show all recorded entries for a player')
    async def get_entries(self, ctx: commands.Context, *args: str) -> None:
        try:
            [handler, handler_args] = self.get_command_handler_and_args(ctx, args)
            await handler.get_entries(ctx, *handler_args)
        except Exception as e:
            print(f"Caught exception: {e}")
            traceback.print_exception(e)

    @commands.guild_only()
    @commands.command(name="view", help="Show player's entry for a given puzzle number")
    async def get_entry(self, ctx: commands.Context, *args: str) -> None:
        try:
            [handler, handler_args] = self.get_command_handler_and_args(ctx, args)
            await handler.get_entry(ctx, *handler_args)
        except Exception as e:
            print(f"Caught exception: {e}")
            traceback.print_exception(e)

    @commands.guild_only()
    @commands.command(name="stats", help="Show basic stats for a player")
    async def get_stats(self, ctx: commands.Context, *args: str) -> None:
        try:
            [handler, handler_args] = self.get_command_handler_and_args(ctx, args)
            await handler.get_stats(ctx, *handler_args)
        except Exception as e:
            print(f"Caught exception: {e}")
            traceback.print_exception(e)

    ######################
    #   HELPER METHODS   #
    ######################

    def get_command_handler_and_args(self, ctx: commands.Context, args: tuple[str]) -> tuple[BaseCommandHandler, tuple[str]]:
            match self.utils.get_game_from_channel(ctx.message):
                case NYTGame.CONNECTIONS:
                    return self.connections, args
                case NYTGame.STRANDS:
                    return self.strands, args
                case NYTGame.WORDLE:
                    return self.wordle, args
                case NYTGame.PIPS:
                    return self.pips, args
                case NYTGame.UNKNOWN:
                    match self.utils.get_game_from_command(*args):
                        case NYTGame.CONNECTIONS:
                            return self.connections, args[1:]
                        case NYTGame.STRANDS:
                            return self.strands, args[1:]
                        case NYTGame.WORDLE:
                            return self.wordle, args[1:]
                        case NYTGame.PIPS:
                            return self.pips, args[1:]
            return None, ()

    def build_help_menu(self) -> None:
        self.help_menu.add('ranks', \
                explanation = "View the leaderboard over time or for a specific puzzle.", \
                usage = "`?ranks (today|weekly|10-day|all-time)`\n`?ranks <MM/DD/YYYY>`\n`?ranks <puzzle #>`\n`?ranks all [<time period>]`", \
                notes = "- `?ranks` will default to `?ranks weekly`.\n- `?ranks all` shows leaderboards for all games.\n- When using MM/DD/YYYY format, the date must be a Sunday. If the channel does not have the game type in its name, the command will need the game type specified as the first argument.",)
        self.help_menu.add('missing', \
                explanation = "View and mention all players who have not yet submitted a puzzle.", \
                usage = "`?missing [<puzzle #>]`", \
                notes = "`?missing` will default to today's puzzle. If the channel does not have the game type in its name, the command will need the game type specified as the first argument.")
        self.help_menu.add('entries', \
                explanation = "View a list of all submitted entries for a player.", \
                usage = "`?entries [<player>]`", \
                notes = "If the channel does not have the game type in its name, the command will need the game type specified as the first argument."
            )
        self.help_menu.add('stats', \
                explanation = "View more details stats on one or players.", \
                usage = "`?stats <player1> [<player2> ...]`", \
                notes = "`?stats` will default to just query for the calling user. If the channel does not have the game type in its name, the command will need the game type specified as the first argument.")
        self.help_menu.add('view', \
                explanation = "View specific details of one or more entries.", \
                usage = "`?view [<player>] <puzzle #1> [<puzzle #2> ...]` ", \
                notes = "If the channel does not have the game type in its name, the command will need the game type specified as the first argument."
            )
        self.help_menu.add('add', \
                explanation = "Manually add an entry to the database.", \
                usage = "`?add [<player>] <entry>`", \
                owner_only=True, \
                notes = "If the channel does not have the game type in its name, the command will need the game type specified as the first argument."
            )
        self.help_menu.add('remove', \
                explanation = "Remove an entry from the database.", \
                usage = "`?remove [<player>] <puzzle #>`", \
                owner_only=True, \
                notes = "If the channel does not have the game type in its name, the command will need the game type specified as the first argument."
            )

async def setup(bot: commands.Bot):
    await bot.add_cog(MembersCog(bot))
