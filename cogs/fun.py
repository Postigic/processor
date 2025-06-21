import discord
from discord.ext import commands
import random

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.responses = [
            "yes", 
            "no", 
            "perhaps", 
            "totally!",
            "hell no!!!", 
            "sigh ask me later vro i'm tired",
            "yeah", 
            "dunno", 
            "prob", 
            "yup", 
            "nah", 
            "maybe",
            "i think so",
            "hell yeah!!!"
        ]

    @commands.command()
    async def roll(self, ctx, sides: int = 6):
        """Rolls a dice.

        Usage:
            ;roll → rolls a 6-sided die
            ;roll 20 → rolls a 20-sided die
        """
        embed = discord.Embed(color=discord.Color.red())
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        embed.add_field(name="🎲 you rolled a...", value=f"{random.randint(1, sides)} (1-{sides})", inline=False)

        await ctx.send(embed=embed)

    @commands.command()
    async def ask(self, ctx, *, question):
        """Answers a yes or no question.

        Usage:
            ;ask Will I win the lottery?
            ;ask Should I eat pizza?
        """
        embed = discord.Embed(color=discord.Color.purple())
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        embed.add_field(name="👀 uhh...", value=random.choice(self.responses), inline=False)

        await ctx.send(embed=embed)

    @commands.command()
    async def flip(self, ctx):
        """Flips a coin."""
        embed = discord.Embed(color=discord.Color.gold())
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        result = "heads" if random.choice([True, False]) else "tails"
        embed.add_field(name="🪙 you flipped...", value=result, inline=False)

        await ctx.send(embed=embed)

    @commands.command()
    async def choose(self, ctx, *choices: str):
        """Chooses between multiple options.

        Usage:
            ;choose pizza burger salad
        """
        if len(choices) < 2:
            await ctx.send("vro you gotta give me at least 2 choices to choose from!!!")
            return

        embed = discord.Embed(color=discord.Color.green())
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        chosen = random.choice(choices)
        embed.add_field(name="🤔 hmm... i choose:", value=chosen, inline=False)

        await ctx.send(embed=embed)

    @commands.command()
    async def mock(self, ctx, *, text: str):
        """Mocks your message."""
        mocked = "".join(
            c.upper() if random.random() > 0.5 else c.lower() for c in text
        )

        embed = discord.Embed(color=discord.Color.orange())
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        embed.add_field(name="🗣️ mIMimIMiMImi...", value=mocked, inline=False)

        await ctx.send(embed=embed)

    @commands.command()
    async def reverse(self, ctx, *, text: str):
        """Reverses your message."""
        reversed_text = text[::-1]
        embed = discord.Embed(color=discord.Color.dark_teal())
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        embed.add_field(name="🔄 desrever:", value=reversed_text, inline=False)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Fun(bot))
