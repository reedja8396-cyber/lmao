import discord
from discord.ext import commands

class CustomCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.custom_commands = {}

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def customcmd(self, ctx, name: str, *, response: str):
        self.custom_commands.setdefault(ctx.guild.id, {})[name.lower()] = response
        await ctx.send(f"Custom command !{name} added.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.content.startswith('!'): return
        cmd = message.content[1:].split()[0].lower()
        resp = self.custom_commands.get(message.guild.id, {}).get(cmd)
        if resp:
            await message.channel.send(resp)

async def setup(bot):
    await bot.add_cog(CustomCommands(bot))
