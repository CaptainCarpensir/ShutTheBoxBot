import logging.handlers
import os

import discord
from discord import ButtonStyle
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button
from dotenv import load_dotenv

from game import ShutTheBoxGame, GameState
from helpers import box_ascii

load_dotenv()  # you shouldn't need to use find_dotenv, if it isn't passed it runs find automatically
logger = logging.getLogger("discord.bot")
logger.setLevel(os.getenv("log_level", default="NOTSET"))


class ShutTheBoxCog(commands.Cog):
    def __init__(self, *, bot):
        logger.info(f"Loaded Cog: {self.__cog_name__}")

    @app_commands.command(name="startshutthebox", description="Play Shut the Box")
    @app_commands.describe(num_die='The number of dice to play with')
    @app_commands.describe(die_faces='The number of faces on each die')
    @app_commands.rename(num_die="number_of_die")
    @app_commands.rename(die_faces="number_of_faces")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=False)
    async def init_game(self, interaction: discord.Interaction, num_die: int, die_faces: int):
        logger.debug(f"Start Shut the Box game with {num_die}d{die_faces} by {interaction.user}")
        new_game = ShutTheBoxGame(die_faces, num_die)
        view = View()
        view.add_item(RollButton(game=new_game))
        await interaction.response.send_message(f"{interaction.user} is playing with {num_die}d{die_faces}", view=view)


class RollButton(Button):
    def __init__(self, game: ShutTheBoxGame):
        super().__init__(style=ButtonStyle.blurple, label="Roll the dice!", disabled=False)
        self.game = game

    async def callback(self, interaction: discord.Interaction):
        self.game.handle_roll()
        roll = self.game.get_die_remaining()

        logger.debug(f"{roll=}")
        logger.debug(f"{self.game.get_possible_flips()=}")
        logger.debug(f"{self.game.sums_table.sums_dict}")

        match self.game.get_game_state():
            case GameState.FLIP_BOXES:
                view = View()
                for choice in self.game.get_possible_flips():
                    view.add_item(ShutButton(self.game, choice))
                await interaction.response.send_message(
                    content=f"Rolled {roll}. Choose a box to shut.\n{box_ascii(self.game.get_boxes_closed())}",
                    view=view
                )
            case GameState.LOSE:
                await interaction.response.send_message(f"Rolled {roll}. You lost!")
        self.view.stop()


class ShutButton(Button):
    def __init__(self, game: ShutTheBoxGame, num: int):
        super().__init__(style=ButtonStyle.blurple, label=f"{num}", disabled=False)
        self.game = game
        self.num = num

    async def callback(self, interaction: discord.Interaction):
        self.game.handle_flip(self.num)

        logger.debug(f"Flipped num: {self.num}")
        logger.debug((self.game.get_boxes_closed()))
        # logger.debug(box_ascii(self.game.get_boxes_closed()))
        logger.debug(f"{self.game.get_die_remaining()=}")
        logger.debug(f"{self.game.get_game_state()=}")

        rem = self.game.get_die_remaining()
        ascii_rem = box_ascii(self.game.get_boxes_closed())

        match self.game.get_game_state():

            case GameState.ROLL:
                view = View()
                view.add_item(RollButton(game=self.game))
                await interaction.response.send_message(
                    content=f"Closed box {self.num}. Roll again!\n{ascii_rem}",
                    view=view
                )
            case GameState.FLIP_BOXES:
                view = View()
                for choice in self.game.get_possible_flips():
                    view.add_item(ShutButton(self.game, choice))
                await interaction.response.send_message(
                    content=f"Closed box {self.num}. Keep going!\n{ascii_rem}",
                    view=view
                )
            case GameState.WIN:
                await interaction.response.send_message(f"You closed all the boxes! You win!\n{ascii_rem}")
            case GameState.LOSE:
                await interaction.response.send_message(f"{rem} remaining. You lost!\n{ascii_rem}")

        self.view.stop()


class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents, command_prefix="we don't use this but it is required")

    async def on_ready(self):
        logger.info(f"Logged in as {self.user}, ID: {self.user.id}")

    async def setup_hook(self):
        await self.add_cog(ShutTheBoxCog(bot=self))
        synced = await self.tree.sync()
        logger.info(f"Synced commands: {[x.name for x in synced]}")


bot: commands.Bot = Bot()
bot.run(os.getenv("BOT_TOKEN"))
