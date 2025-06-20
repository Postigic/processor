import discord
from discord.ext import commands

class Help(commands.HelpCommand):
    async def send_bot_help(self, mapping):
        ctx = self.context
        embed = discord.Embed(title="Help", color=discord.Color.blue())
        
        for cog, commands_ in mapping.items():
            name = cog.qualified_name if cog else "No Category"
            filtered = await self.filter_commands(commands_, sort=True)

            filtered = [cmd for cmd in filtered if cmd.name != "help"]
            
            if not filtered:
                continue
            
            value = ""
            
            for command in filtered:
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
