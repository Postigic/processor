import discord
from discord.ext import commands

class Help(commands.HelpCommand):
    def __init__(self):
        super().__init__()

    async def send_bot_help(self, mapping):
        ctx = self.context
        embed = discord.Embed(color=discord.Color.blue())
        embed.set_author(name=ctx.bot.user.name, icon_url=ctx.bot.user.avatar.url)

        category_commands = {}

        for cog, commands_ in mapping.items():
            if cog and cog.qualified_name == "URLStore":
                name = "Utility"
            else:
                name = cog.qualified_name if cog else "No Category"
            
            filtered = await self.filter_commands(commands_, sort=True)
            filtered = [cmd for cmd in filtered if cmd.name != "help"]
            
            if not filtered:
                continue

            category_commands.setdefault(name, [])
            category_commands[name].extend(filtered)
            
        for name, cmds in category_commands.items():
            value = ""
            for command in cmds:
                signature = self.get_command_signature(command)
                desc = command.help.split("\n")[0] if command.help else "No description."
                value += f"**{signature}**\n{desc}\n\n"

            if embed.fields:
                embed.add_field(name="\n", value="\n", inline=False)
            
            embed.add_field(name=name, value=value, inline=False)
    
        await ctx.send(embed=embed)

    async def send_command_help(self, command):
        ctx = self.context
        embed = discord.Embed(title=self.get_command_signature(command), color=discord.Color.green())
        
        if command.help:
            embed.description = command.help
        else:
            embed.description = "No description provided."
        
        await ctx.send(embed=embed)

    def get_command_signature(self, command):
        prefix = self.context.clean_prefix if self.context else ";"
        return f"{prefix}{command.qualified_name} {command.signature}"
