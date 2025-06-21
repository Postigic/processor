import discord
from discord.ext import commands
import time

start_time = time.time()

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def uptime(self, ctx):
        """Shows the bot's uptime."""
        seconds = int(time.time() - start_time)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)

        embed = discord.Embed(color=discord.Color.dark_grey())
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        embed.add_field(name="\n", value="\n", inline=False)
        embed.add_field(name="🕔 uptime", value=f"{hours}h {minutes}m {seconds}s", inline=False)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Utility(bot))
