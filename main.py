import os
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
from help import Help

app = Flask('')

@app.route('/')
def home():
    return "I'm alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=";", intents=intents, help_command=Help())

@bot.event
async def on_ready():
    print(f"Bot is ready. Logged in as {bot.user}")
    await bot.load_extension("fun")
    await bot.load_extension("utility")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user.mentioned_in(message):
        await message.channel.send(f"what do you want {message.author.mention}, my prefix is ;")

    await bot.process_commands(message)

keep_alive()
bot.run(os.getenv("BOT_TOKEN"))
