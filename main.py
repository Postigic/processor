import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from cogs.help import Help

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix=";", intents=intents, help_command=Help())

@bot.event
async def on_ready():
    print(f"Bot is ready. Logged in as {bot.user}")

    for guild in bot.guilds:
        print(f"Connected to: {guild.name}")

@bot.event
async def on_message(message):
    await bot.process_commands(message)

async def main():
    await bot.load_extension("cogs.fun")
    await bot.load_extension("cogs.utility")
    await bot.load_extension("cogs.url_store")
    await bot.start(os.getenv("BOT_TOKEN"))

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
