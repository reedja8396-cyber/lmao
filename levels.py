import discord
from discord.ext import commands

class Levels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def rank(self, ctx):
        await ctx.send("Level system ready (DB expansion recommended)")

async def setup(bot):
    await bot.add_cog(Levels(bot))
