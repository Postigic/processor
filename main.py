import os
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
from dotenv import load_dotenv
from cogs.help import Help

load_dotenv()

app = Flask('')

@app.route('/')
def home():
    return "I'm alive!"

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=";", intents=intents, help_command=Help())

@bot.event
async def on_ready():
    print(f"Bot is ready. Logged in as {bot.user}")

@bot.event
async def on_message(message):
    # if message.author == bot.user:
    #     return

    # if bot.user.mentioned_in(message):
    #     await message.reply(f"what do you want, my prefix is ;")

    await bot.process_commands(message)

async def main():
    await bot.load_extension("cogs.fun")
    await bot.load_extension("cogs.utility")
    await bot.load_extension("cogs.url_store")
    keep_alive()
    await bot.start(os.getenv("BOT_TOKEN"))

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())