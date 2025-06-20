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
        await ctx.send(f"uptime: {hours}h {minutes}m {seconds}s")

async def setup(bot):
    await bot.add_cog(Utility(bot))
