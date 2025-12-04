from discord.ext import commands
from games.base_command_handler import BaseCommandHandler
from utils.bot_utilities import BotUtilities, NYTGame

class OwnerCog(commands.Cog, name="Owner-Only Commands"):
    # class variables
    bot: commands.Bot
    utils: BotUtilities

    # games
    connections: BaseCommandHandler
    strands: BaseCommandHandler
    wordle: BaseCommandHandler
    pips: BaseCommandHandler

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.utils = self.bot.utils
        self.connections = self.bot.connections
        self.strands = self.bot.strands
        self.wordle = self.bot.wordle
        self.pips = self.bot.pips

    #####################
    #   COMMAND SETUP   #
    #####################

    @commands.is_owner()
    @commands.command(name="remove", help="Removes one puzzle entry for a player")
    async def remove_entry(self, ctx: commands.Context, *args: str) -> None:
        [handler, handler_args] = self.get_command_handler_and_args(ctx, args)
        await handler.remove_entry(ctx, *handler_args)

    @commands.is_owner()
    @commands.command(name='add', help='Manually adds a puzzle entry for a player')
    async def add_score(self, ctx: commands.Context, *args: str) -> None:
        [handler, handler_args] = self.get_command_handler_and_args(ctx, args)
        await handler.add_score(ctx, *handler_args)

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
async def setup(bot: commands.Bot):
    await bot.add_cog(OwnerCog(bot))
