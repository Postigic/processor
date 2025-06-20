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
            !roll → rolls a 6-sided die
            !roll 20 → rolls a 20-sided die
        """
        embed = discord.Embed(color=discord.Color.red())
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        embed.add_field(name="\n", value="\n", inline=False)
        embed.add_field(name="🎲 you rolled a...", value=f"{random.randint(1, sides)} (1-{sides})", inline=False)

        await ctx.send(embed=embed)

    @commands.command()
    async def ask(self, ctx, *, question):
        """Answers a yes or no question.

        Usage:
            !ask Will I win the lottery?
            !ask Should I eat pizza?
        """
        embed = discord.Embed(color=discord.Color.purple())
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        embed.add_field(name="\n", value="\n", inline=False)
        embed.add_field(name="👀 uhh...", value=random.choice(self.responses), inline=False)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Fun(bot))
