import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True

class AntiRaidBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                await self.load_extension(f"cogs.{filename[:-3]}")
                print(f"[COG LOADED] {filename}")
        
        await self.tree.sync()

    async def on_ready(self):
        print(f"Anti-Raid Shield is online as {self.user}")

bot = AntiRaidBot()
bot.run(TOKEN)
