import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
from cogs.Data.database_handler import DatabaseHandler

cwd = os.getcwd()
os.chdir(cwd)
load_dotenv(dotenv_path='config')

intents = discord.Intents().all()
database_handler = DatabaseHandler('database.db')


class FanBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.version = "BÊTA"

    async def setup_hook(self):
        await self.load_extension(f"cogs.admin")
        await self.load_extension(f"cogs.moderation")
        await self.load_extension(f"cogs.economy")
        await self.load_extension(f"cogs.politic")
        await self.load_extension(f"cogs.user_interaction")

        await fanbot.tree.sync(guild=discord.Object(id=976578012592111646))

    async def on_ready(self):
        print(f"{self.user.display_name} has connected. (version: {self.version})")

    async def on_member_join(self, member: discord.Member):
        database_handler.add_member_to_db(user_id=member.id)
        database_handler.create_account(user_id=member.id)

    async def on_member_remove(self, member: discord.Member):
        database_handler.remove_member_to_db(user_id=member.id)
        database_handler.delete_account(user_id=member.id)


fanbot = FanBot()

fanbot.remove_command("help")

fanbot.run(os.getenv("TOKEN"))
