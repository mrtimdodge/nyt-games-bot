import os
import discord, traceback
from discord.ext import commands
from games.base_command_handler import BaseCommandHandler
from utils.bot_utilities import BotUtilities, NYTGame
from utils.help_handler import HelpMenuHandler

class MembersCog(commands.Cog, name="Normal Members Commands"):
    # class variables
    bot: commands.Bot
    utils: BotUtilities
    help_menu: HelpMenuHandler

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
        self.build_help_menu()

        self.connections = self.bot.connections
        self.strands = self.bot.strands
        self.wordle = self.bot.wordle
        self.pips = self.bot.pips

        self._mysql_db_name = os.environ.get('PIPS_MYSQL_DB_NAME', "pips")

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
                        if(self.confirm_entries):
                            await message.add_reaction('✅')
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
                usage = "`?ranks (today|weekly|10-day|all-time)`\n`?ranks <MM/DD/YYYY>`\n`?ranks <puzzle #>`", \
                notes = "- `?ranks` will default to `?ranks weekly`.\n- When using MM/DD/YYYY format, the date must be a Sunday. If the channel does not have the game type in its name, the command will need the game type specified as the first argument.",)
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
