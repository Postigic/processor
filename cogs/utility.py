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
        embed.add_field(name="🕔 uptime", value=f"{hours}h {minutes}m {seconds}s", inline=False)

        await ctx.send(embed=embed)

    @commands.command()
    async def avatar(self, ctx, user: discord.Member = None):
        """Shows a user's avatar"""
        user = user or ctx.author

        embed = discord.Embed(color=discord.Color.blue())
        embed.set_author(name=f"{user.name}'s Avatar")
        embed.set_image(url=user.avatar.url)

        await ctx.send(embed=embed)

    @commands.command()
    async def server_info(self, ctx):
        """Shows server information"""
        guild = ctx.guild
        embed = discord.Embed(color=discord.Color.blue())
        embed.set_author(name=guild.name, icon_url=guild.icon.url if guild.icon else None)
        
        bots = sum(member.bot for member in guild.members)
        humans = guild.member_count - bots
        
        embed.add_field(name="👑 Owner", value=guild.owner.mention, inline=True)
        embed.add_field(name="📆 Created", value=guild.created_at.strftime("%b %d, %Y"), inline=True)
        embed.add_field(name="🌍 Locale", value=guild.preferred_locale.value.replace('_', '-').title(), inline=True)
        embed.add_field(name="👥 Members", value=f"{humans} humans\n{bots} bots", inline=True)
        embed.add_field(name="💬 Channels", value=f"{len(guild.text_channels)} text\n{len(guild.voice_channels)} voice", inline=True)
        embed.add_field(name="🎚️ Roles", value=len(guild.roles), inline=True)

        embed.set_footer(text=f"Server ID: {guild.id}")
        
        if guild.banner:
            embed.set_image(url=guild.banner.url)
            
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Utility(bot))
