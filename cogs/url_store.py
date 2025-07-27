import discord
from discord.ext import commands
import aiosqlite
import asyncio
import random
import re
import os
from urllib.parse import urlparse, urlunparse
from utils.paginator import Paginator

URL_REGEX = re.compile(r'https?://[^\s<>"]+|www\.[^\s<>"]+')
DB_PATH = os.getenv("URL_DB_PATH", "data/urls.db")

class URLStore(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = DB_PATH
        self.db = None

    async def cog_load(self):
        self.db = await aiosqlite.connect(self.db_path)
        await self.db.execute("PRAGMA journal_mode=WAL;")
        await self.initialize_db()

    async def cog_unload(self):
        if self.db:
            await self.db.close()

    async def initialize_db(self):
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL
            )
        """)
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS blacklist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL
            )
        """)
        await self.db.commit()

    def normalize_url(self, url):
        parsed = urlparse(url)
        return urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))

    async def is_blacklisted(self, url):
        url = self.normalize_url(url)
        async with self.db.execute("SELECT 1 FROM blacklist WHERE url = ?", (url,)) as cursor:
            return await cursor.fetchone() is not None

    async def add_url(self, url: str):
        url = self.normalize_url(url)
        if await self.is_blacklisted(url):
            return False
        try:
            await self.db.execute("INSERT INTO urls (url) VALUES (?)", (url,))
            await self.db.commit()
            return True
        except aiosqlite.IntegrityError:
            return False

    def classify_url_weight(self, url: str) -> int:
        if any(domain in url for domain in ["tenor.com", "discordapp", "imgur.com"]):
            return 10
        elif "fxtwitter.com" in url:
            return 6
        elif any(domain in url for domain in ["youtube.com", "youtu.be"]):
            return 2
        return 1

    async def get_random_url(self):
        async with self.db.execute("SELECT url FROM urls") as cursor:
            all_urls = [row[0] for row in await cursor.fetchall()]

        filtered = [url for url in all_urls if not await self.is_blacklisted(url)]
        if not filtered:
            return None

        weights = [self.classify_url_weight(url) for url in filtered]
        return random.choices(filtered, weights=weights, k=1)[0]

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.channel.id != 869868084725432402:
            return
        ctx = await self.bot.get_context(message)
        if ctx.valid:
            return

        urls = URL_REGEX.findall(message.content)
        urls.extend(embed.url for embed in message.embeds if embed.url)

        for url in urls:
            if await self.add_url(url):
                print(f"Added new URL: {url}")

        if message.reference:
            replied = await message.channel.fetch_message(message.reference.message_id)
            if replied.author.id == self.bot.user.id:
                url = await self.get_random_url()
                if url:
                    await message.reply(url)
                return

        if self.bot.user.mentioned_in(message):
            url = await self.get_random_url()
            if url:
                await message.reply(url)

    @commands.command(name="url_list")
    @commands.has_permissions(administrator=True)
    async def url_list(self, ctx):
        """Lists all saved URLs."""
        async with self.db.execute("SELECT url FROM urls") as cursor:
            urls = [row[0] for row in await cursor.fetchall()]

        if not urls:
            embed = discord.Embed(color=discord.Color.blue(), description="🦗 nothing here yet...")
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
            await ctx.send(embed=embed)
            return

        view = Paginator(urls, ctx.author, self.bot.user, title="📦 saved urls")
        embed = view.get_embed()
        view.message = await ctx.send(embed=embed, view=view)

    @commands.command(name="url_scan")
    @commands.has_permissions(administrator=True)
    async def url_scan(self, ctx, limit: int = 1000):
        """Scans the last `limit` (default: 1000) messages in the channel for URLs and adds them to the database."""
        scanning_embed = discord.Embed(color=discord.Color.blue())
        scanning_embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        scanning_embed.add_field(name="🔍 scanning...", value=f"scanning the last `{limit}` messages for urls...", inline=False)
        msg = await ctx.send(embed=scanning_embed)

        added_count = 0
        to_insert = []

        async for message in ctx.channel.history(limit=limit):
            if message.author.bot:
                continue
            urls = URL_REGEX.findall(message.content)
            urls.extend(embed.url for embed in message.embeds if embed.url)
            for url in urls:
                norm = self.normalize_url(url)
                if not await self.is_blacklisted(norm):
                    to_insert.append((norm,))

        if to_insert:
            try:
                await self.db.executemany("INSERT OR IGNORE INTO urls (url) VALUES (?)", to_insert)
                await self.db.commit()
                added_count = self.db.total_changes
            except Exception as e:
                print(f"Batch insert error: {e}")

        done_embed = discord.Embed(color=discord.Color.green())
        done_embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        done_embed.add_field(name="✅ ding ding ding!!!", value=f"added `{added_count}` new urls", inline=False)
        await msg.edit(embed=done_embed)

    @commands.command(name="url_remove")
    @commands.has_permissions(administrator=True)
    async def url_remove(self, ctx, url: str):
        """Removes a URL from the database."""
        url = self.normalize_url(url)
        cursor = await self.db.execute("DELETE FROM urls WHERE url = ?", (url,))
        await self.db.commit()
        removed = cursor.rowcount > 0

        embed = discord.Embed(color=discord.Color.red())
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        if removed:
            embed.add_field(name="🚮 removed", value=f"{url} removed from database", inline=False)
        else:
            embed.add_field(name="⚠️ uh oh...", value=f"{url} not found in the database", inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="url_purge")
    @commands.has_permissions(administrator=True)
    async def url_purge(self, ctx):
        """Purges all URLs from the database."""
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        embed = discord.Embed(color=discord.Color.dark_red())
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        embed.add_field(name="⚠️ confirmation required", value="are you sure you want to delete all urls? type `yes` to confirm", inline=False)
        await ctx.send(embed=embed)

        try:
            msg = await self.bot.wait_for("message", timeout=15.0, check=check)
            if msg.content.lower() == "yes":
                await self.db.execute("DELETE FROM urls")
                await self.db.commit()
                embed = discord.Embed(color=discord.Color.dark_red())
                embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
                embed.add_field(name="💥 purged", value="all urls have been purged from the database", inline=False)
            else:
                embed = discord.Embed(color=discord.Color.red())
                embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
                embed.add_field(name="❌ cancelled", value="purge cancelled", inline=False)
        except asyncio.TimeoutError:
            embed = discord.Embed(color=discord.Color.yellow())
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
            embed.add_field(name="⏰ timeout", value="confirmation timed out, purge cancelled", inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="blacklist_list")
    @commands.has_permissions(administrator=True)
    async def blacklist_list(self, ctx):
        """Lists all blacklisted URLs."""
        async with self.db.execute("SELECT url FROM blacklist") as cursor:
            urls = [row[0] for row in await cursor.fetchall()]

        if not urls:
            embed = discord.Embed(title="🚫 blacklisted urls", description="🦗 nothing here yet...", color=discord.Color.dark_grey())
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
            await ctx.send(embed=embed)
            return

        view = Paginator(urls, ctx.author, self.bot.user, title="🚫 blacklisted urls", color=discord.Color.dark_grey())
        embed = view.get_embed()
        view.message = await ctx.send(embed=embed, view=view)

    @commands.command(name="blacklist_add")
    @commands.has_permissions(administrator=True)
    async def blacklist_add(self, ctx, url: str):
        """Adds a URL to the blacklist."""
        url = self.normalize_url(url)
        embed = discord.Embed(color=discord.Color.red())
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)

        async with self.db.execute("SELECT 1 FROM blacklist WHERE url = ?", (url,)) as cursor:
            if await cursor.fetchone():
                embed.add_field(name="⚠️ uh oh...", value=f"{url} already blacklisted", inline=False)
            else:
                await self.db.execute("INSERT INTO blacklist (url) VALUES (?)", (url,))
                await self.db.commit()
                embed.add_field(name="✅ ding ding ding!!!", value=f"{url} blacklisted", inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="blacklist_remove")
    @commands.has_permissions(administrator=True)
    async def blacklist_remove(self, ctx, url: str):
        """Removes a URL from the blacklist."""
        url = self.normalize_url(url)
        embed = discord.Embed(color=discord.Color.orange())
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)

        cursor = await self.db.execute("DELETE FROM blacklist WHERE url = ?", (url,))
        await self.db.commit()
        if cursor.rowcount:
            embed.add_field(name="✅ ding ding ding!!!", value=f"{url} removed from blacklist", inline=False)
        else:
            embed.add_field(name="⚠️ uh oh...", value=f"{url} not found in blacklist", inline=False)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(URLStore(bot))
