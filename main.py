import os
import discord
import asyncio
from discord.ext import commands
from dotenv import load_dotenv
from cogs.help import Help

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix=";", intents=intents, help_command=Help(), case_insensitive=True)

@bot.event
async def on_ready():
    print(f"\n✅ Bot is ready. Logged in as {bot.user}", end="\n\n")

    for guild in bot.guilds:
        print(f"    Connected to: {guild.name}")

    print()

    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="you"))

async def load_cogs():
    EXCEPTIONS = {"help.py"}

    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and filename not in EXCEPTIONS:
            extension = f"cogs.{filename[:-3]}"
            try:
                await bot.load_extension(extension)
                print(f"✅ Loaded {extension}")
            except Exception as e:
                print(f"❌ Failed to load {extension}: {e}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if isinstance(message.channel, discord.TextChannel) and message.channel.is_nsfw():
        return

    await bot.process_commands(message)

async def main():
    await load_cogs()
    await bot.start(os.getenv("BOT_TOKEN"))

if __name__ == "__main__":
    asyncio.run(main())
