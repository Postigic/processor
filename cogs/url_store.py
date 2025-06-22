import discord
from discord.ext import commands
from tinydb import TinyDB, Query
import asyncio
import random
import re
import os
from urllib.parse import urlparse, urlunparse
from utils.paginator import Paginator

URL_REGEX = re.compile(r'https?://[^\s<>"]+|www\.[^\s<>"]+')
DB_PATH = os.getenv("URL_DB_PATH", "data/urls.json")

class URLStore(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = TinyDB(DB_PATH)
        self.urls_table = self.db.table('urls')
        self.blacklist_table = self.db.table('blacklist')

    def normalize_url(self, url):
        parsed = urlparse(url)
        return urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))

    def is_blacklisted(self, url):
        url = self.normalize_url(url)
        return self.blacklist_table.search(Query().url == url)
    
    def add_url(self, url: str):
        url = self.normalize_url(url)

        if self.is_blacklisted(url):
            return False
        
        if not self.urls_table.contains(Query().url == url):
            self.urls_table.insert({"url": url})
            return True
        
        return False
    
    def get_random_url(self):
        urls = self.urls_table.all()
        filtered = [u["url"] for u in urls if not self.is_blacklisted(u["url"])]
        if filtered:
            return random.choice(filtered)
        return None
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        if message.channel.id != 869868084725432402:
            return
        
        ctx = await self.bot.get_context(message)
        if ctx.valid:
            return
        
        urls = URL_REGEX.findall(message.content)

        for embed in message.embeds:
            if embed.url:
                urls.append(embed.url)

        for url in urls:
            added = self.add_url(url)
            if added:
                print(f"Added new URL: {url}")

        if message.reference:
            replied = await message.channel.fetch_message(message.reference.message_id)
            if replied.author.id == self.bot.user.id:
                url = self.get_random_url()
                if url:
                    await message.reply(url)
                return

        if self.bot.user.mentioned_in(message):
            url = self.get_random_url()
            if url:
                await message.reply(url)

    @commands.command(name="url_list")
    @commands.has_permissions(administrator=True)
    async def url_list(self, ctx):
        """List all saved URLs."""
        entries = self.urls_table.all()

        if not entries:
            embed = discord.Embed(color=discord.Color.blue(), description="🦗 nothing here yet...")
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)

            await ctx.send(embed=embed)
            return

        urls = [entry["url"] for entry in entries]
        view = Paginator(urls, ctx.author, self.bot.user, title="📦 saved urls")
        embed = view.get_embed()

        view.message = await ctx.send(embed=embed, view=view)

    @commands.command(name="url_remove")
    @commands.has_permissions(administrator=True)
    async def url_remove(self, ctx, url: str):
        """Remove a specific URL from the database."""
        url = self.normalize_url(url)
    
        embed = discord.Embed(color=discord.Color.red())
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)

        removed = self.urls_table.remove(Query().url == url)

        if removed:
            embed.add_field(name="🚮 removed", value=f"{url} removed from database", inline=False)
        else:
            embed.add_field(name="⚠️ uh oh...", value=f"{url} not found in the database", inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="url_purge")
    @commands.has_permissions(administrator=True)
    async def url_purge(self, ctx):
        """Purge all URLs from the database."""
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        
        embed = discord.Embed(color=discord.Color.dark_red())
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        embed.add_field(name="⚠️ confirmation required", value="are you sure you want to delete all urls? type `yes` to confirm", inline=False)

        await ctx.send(embed=embed)

        try:
            msg = await self.bot.wait_for("message", timeout=15.0, check=check)
            if msg.content.lower() == "yes":
                self.urls_table.truncate()
                embed = discord.Embed(color=discord.Color.dark_red())
                embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
                embed.add_field(name="💥 purged", value="all urls have been purged from the database", inline=False)

                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(color=discord.Color.red())
                embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
                embed.add_field(name="❌ cancelled", value="purge cancelled", inline=False)

                await ctx.send(embed=embed)
        except asyncio.TimeoutError:
            embed = discord.Embed(color=discord.Color.yellow())
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
            embed.add_field(name="⏰ timeout", value="confirmation timed out, purge cancelled", inline=False)

            await ctx.send(embed=embed)

    @commands.command(name="blacklist_list")
    @commands.has_permissions(administrator=True)
    async def blacklist_list(self, ctx):
        """List all blacklisted URLs."""
        entries = self.blacklist_table.all()

        if not entries:
            embed = discord.Embed(title="🚫 blacklisted urls", description="🦗 nothing here yet...", color=discord.Color.dark_grey())
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
            
            await ctx.send(embed=embed)
            return
        
        urls = [entry["url"] for entry in entries]
        view = Paginator(urls, ctx.author, self.bot.user, title="🚫 blacklisted urls", color=discord.Color.dark_grey())
        embed = view.get_embed()

        view.message = await ctx.send(embed=embed, view=view)

    @commands.command(name="blacklist_add")
    @commands.has_permissions(administrator=True)
    async def blacklist_add(self, ctx, url: str):
        """Add a URL to the blacklist."""
        url = self.normalize_url(url)

        embed = discord.Embed(color=discord.Color.red())
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)

        if self.blacklist_table.contains(Query().url == url):
            embed.add_field(name="⚠️ uh oh...", value=f"{url} already blacklisted", inline=False)
        else:
            self.blacklist_table.insert({'url': url})
            embed.add_field(name="✅ ding ding ding!!!", value=f"{url} blacklisted", inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="blacklist_remove")
    @commands.has_permissions(administrator=True)
    async def blacklist_remove(self, ctx, url: str):
        """Remove a URL from the blacklist."""
        url = self.normalize_url(url)

        embed = discord.Embed(color=discord.Color.orange())
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)

        if self.blacklist_table.contains(Query().url == url):
            self.blacklist_table.remove(Query().url == url)
            embed.add_field(name="✅ ding ding ding!!!", value=f"{url} removed from blacklist", inline=False)
        else:
            embed.add_field(name="⚠️ uh oh...", value=f"{url} not found in blacklist", inline=False)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(URLStore(bot))
