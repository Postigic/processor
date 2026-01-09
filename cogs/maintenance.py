import discord
from discord.ext import commands

class Maintenance(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="reload")
    @commands.is_owner()
    async def reload_cog(self, ctx, cog: str):
        """Reloads a specified cog."""
        if not (ctx.author.guild_permissions.administrator or await self.bot.is_owner(ctx.author)):
            embed = discord.Embed(color=discord.Color.red())
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
            embed.add_field(name="❌ only the bot owner can run this command.", value="", inline=False)
            return await ctx.send(embed=embed)

        try:
            await self.bot.reload_extension(f"cogs.{cog}")
            embed = discord.Embed(color=discord.Color.green())
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
            embed.add_field(name="✅ ding ding ding!!!", value=f"cogs.{cog} successfully reloaded", inline=False)
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(color=discord.Color.green())
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
            embed.add_field(name="❌ uh oh...", value=f"cogs.{cog} could not be reloaded due to exception: {e}", inline=False)
            await ctx.send(embed=embed)
    
    @commands.command(name="reload_all")
    async def reload_all(self, ctx):
        """Reloads all cogs."""
        if not (ctx.author.guild_permissions.administrator or await self.bot.is_owner(ctx.author)):
            embed = discord.Embed(color=discord.Color.red())
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
            embed.add_field(name="❌ only the bot owner can run this command.", value="", inline=False)
            return await ctx.send(embed=embed)

        reloaded = []
        for cog in list(self.bot.extensions.keys()):
            try:
                await self.bot.reload_extension(cog)
                reloaded.append(cog)
            except Exception as e:
                embed = discord.Embed(color=discord.Color.red())
                embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
                embed.add_field(name="❌ uh oh...", value=f"cogs.{cog} could not be reloaded due to an exception: {e}", inline=False)
                await ctx.send(embed=embed)
        embed = discord.Embed(color=discord.Color.green())
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        embed.add_field(name="✅ ding ding ding!!!", value=f"{', '.join(reloaded)} successfully reloaded", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="shutdown")
    @commands.is_owner()
    async def shutdown_bot(self, ctx):
        """Shuts down the bot."""
        if not (ctx.author.guild_permissions.administrator or await self.bot.is_owner(ctx.author)):
            embed = discord.Embed(color=discord.Color.red())
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
            embed.add_field(name="❌ only the bot owner can run this command.", value="", inline=False)
            return await ctx.send(embed=embed)

        embed = discord.Embed(color=discord.Color.red())
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        embed.add_field(name="🛑 shutting down...", value="goodnight!", inline=False)
        await ctx.send(embed=embed)
        await self.bot.close()
    
async def setup(bot):
    await bot.add_cog(Maintenance(bot))