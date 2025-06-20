from discord.ext import commands
from tinydb import TinyDB, Query
import random
import re
import os

URL_REGEX = re.compile(r'https?://[^\s<>"]+|www\.[^\s<>"]+')
DB_PATH = os.getenv("URL_DB_PATH", "data/urls.json")

class URLStore(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = TinyDB(DB_PATH)
        self.urls_table = self.db.table('urls')
        self.blacklist_table = self.db.table('blacklist')

    def is_blacklisted(self, url):
        return self.blacklist_table.search(Query().url == url)
    
    def add_url(self, url):
        if self.is_blacklisted(url):
            return False
        
        if not self.urls_table.contains(Query().url == url):
            self.urls_table.insert({'url': url})
            return True
        
        return False
    
    def get_random_url(self):
        urls = self.urls_table.all()
        filtered = [u['url'] for u in urls if not self.is_blacklisted(u['url'])]
        if filtered:
            return random.choice(filtered)
        return None
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        if message.channel.id != 869868084725432402:
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

    @commands.command(name="blacklist_add")
    @commands.has_permissions(administrator=True)
    async def blacklist_add(self, ctx, url: str):
        """Add a URL to the blacklist."""
        if self.blacklist_table.contains(Query().url == url):
            await ctx.send("URL is already blacklisted.")
        else:
            self.blacklist_table.insert({'url': url})
            await ctx.send(f"Blacklisted: {url}")

    @commands.command(name="blacklist_remove")
    @commands.has_permissions(administrator=True)
    async def blacklist_remove(self, ctx, url: str):
        """Remove a URL from the blacklist."""
        if self.blacklist_table.contains(Query().url == url):
            self.blacklist_table.remove(Query().url == url)
            await ctx.send(f"Removed from blacklist: {url}")
        else:
            await ctx.send("URL not found in blacklist.")

    @commands.command(name="blacklist_list")
    @commands.has_permissions(administrator=True)
    async def blacklist_list(self, ctx):
        """List all blacklisted URLs."""
        entries = self.blacklist_table.all()
        if entries:
            await ctx.send("\n".join(u['url'] for u in entries))
        else:
            await ctx.send("Blacklist is empty.")

async def setup(bot):
    await bot.add_cog(URLStore(bot))
