import discord
from discord.ui import View, Button

class Paginator(View):
    def __init__(self, items, author, bot_user, title, color=discord.Color.blue(), page_size=10):
        super().__init__(timeout=60)
        self.items = items
        self.page_size = page_size
        self.current_page = 0
        self.author = author
        self.bot_user = bot_user
        self.title = title
        self.color = color
        self.total_pages = (len(items) + page_size - 1) // page_size

        self.prev_button.disabled = True
        if self.total_pages <= 1:
            self.next_button.disabled = True

    def get_embed(self):
        embed = discord.Embed(title=f"{self.title} (page {self.current_page + 1}/{self.total_pages})", color=self.color)
        embed.set_author(name=self.bot_user.name, icon_url=self.bot_user.avatar.url)

        start = self.current_page * self.page_size
        end = start + self.page_size

        for i, item in enumerate(self.items[start:end], start=start + 1):
            if "\n" in item or item.startswith("__**"):
                embed.add_field(name=f"", value=item, inline=False)
            else:
                embed.add_field(name=f"{i}.", value=item, inline=False)

        return embed

    @discord.ui.button(label="◀ Previous", style=discord.ButtonStyle.grey)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.author:
            await interaction.response.send_message("this ain't your session bud...", ephemeral=True)
            return

        self.current_page -= 1
        if self.current_page == 0:
            self.prev_button.disabled = True
        self.next_button.disabled = False

        await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="Next ▶", style=discord.ButtonStyle.grey)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.author:
            await interaction.response.send_message("this ain't your session bud...", ephemeral=True)
            return

        self.current_page += 1
        if self.current_page == self.total_pages - 1:
            self.next_button.disabled = True
        self.prev_button.disabled = False

        await interaction.response.edit_message(embed=self.get_embed(), view=self)

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        try:
            await self.message.edit(view=self)
        except discord.NotFound:
            pass