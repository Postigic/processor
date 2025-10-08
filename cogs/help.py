import discord
from discord.ext import commands
import inspect
from utils.paginator import Paginator

class Help(commands.HelpCommand):
    def __init__(self):
        super().__init__()

    async def send_bot_help(self, mapping):
        ctx = self.context
        category_commands = {}

        ORDER = ["Fun", "Utility", "Maintenance"]

        for cog, commands_ in mapping.items():
            if cog and cog.qualified_name == "URLStore":
                name = "Utility"
            else:
                name = cog.qualified_name if cog else "No Category"
            
            filtered = await self.filter_commands(commands_, sort=False)
            filtered = [cmd for cmd in filtered if cmd.name != "help"]
            
            if not filtered:
                continue
            
            category_commands.setdefault(name, [])
            category_commands[name].extend(filtered)

        category_commands = dict(sorted(category_commands.items(), key=lambda item: ORDER.index(item[0]) if item[0] in ORDER else 999))

        entries = []

        for name, cmds in category_commands.items():
            value = ""
            for command in cmds:
                signature = self.get_command_signature(command)
                desc = command.help.split("\n")[0] if command.help else "☹️ no description"
                value += f"**{signature}**\n{desc}\n\n"

            entries.append(f"__**{name}**__\n{value.strip()}")

        view = Paginator(entries, ctx.author, ctx.bot.user, title="📖 commands", color=discord.Color.blurple(), page_size=1)
        embed = view.get_embed()
        view.message = await ctx.send(embed=embed, view=view)

    async def send_command_help(self, command):
        ctx = self.context
        embed = discord.Embed(title=self.get_command_signature(command), color=discord.Color.blurple())
        
        if command.help:
            embed.description = command.help
        else:
            embed.description = "No description provided."
        
        await ctx.send(embed=embed)

    def get_command_signature(self, command):
        # prefix = self.context.clean_prefix if self.context else ";"
        params = list(inspect.signature(command.callback).parameters.values())

        params = params[2:]

        parts = []

        for param in params:
            name = param.name

            if param.kind == param.VAR_POSITIONAL:
                part = f"<{name}...>"
            elif param.default is not param.empty:
                part = f"[{name}]"
            else:
                part = f"<{name}>"
            
            parts.append(part)

        return f";{command.qualified_name} {' '.join(parts)}"
