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
        result = random.randint(1, sides)
        await ctx.send(f"🎲 you rolled a {result} (1-{sides})")

    @commands.command()
    async def ask(self, ctx, *, question):
        """Answers a yes or no question.

        Usage:
            !ask Will I win the lottery?
            !ask Should I eat pizza?
        """
        await ctx.send(f"🎱 {random.choice(self.responses)}")

async def setup(bot):
    await bot.add_cog(Fun(bot))
