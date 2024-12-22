import discord
import os
from discord import app_commands
from discord.ui import View, Button
from discord import ButtonStyle
from dotenv import load_dotenv, find_dotenv
from game import ShutTheBoxGame, GameState
from helpers import box_ascii

load_dotenv(dotenv_path=find_dotenv())

class RollButton(Button):
    def __init__(self, game: ShutTheBoxGame):
        super().__init__(style=ButtonStyle.blurple, label="Roll the dice!", disabled=False)
        self.game = game

    async def callback(self, interaction: discord.Interaction):
        self.game.handle_roll()
        roll = self.game.get_die_remaining()

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



class BotClient(discord.Client):
    def __init__(self, *, intents, **options):
        super().__init__(intents=intents, **options)
        self.tree = app_commands.CommandTree(self)

        @self.tree.command(
            name="shutthebox",
            description="Play Shut the Box",
        )
        @app_commands.describe(num_die='The number of dice to play with')
        @app_commands.describe(die_faces='The number of faces on each die')
        async def init_game(interaction: discord.Interaction, num_die: int, die_faces: int):
            new_game = ShutTheBoxGame(die_faces, num_die)
            view = View()
            view.add_item(RollButton(game=new_game))
            await interaction.response.send_message(
f"""{interaction.user} is playing with {num_die}d{die_faces}""",
                    view=view
                )


    async def on_ready(self):
        await self.tree.sync()
        print(f'Logged on as {self.user}!')

    async def on_message(self, message: discord.Message):
        pass

intents = discord.Intents.default()
intents.message_content = True

client = BotClient(intents=intents)
client.run(os.getenv('BOT_TOKEN', ''))


# https://discord.com/oauth2/authorize?client_id=1320431680196186122&permissions=309237713920&scope=bot