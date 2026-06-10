import discord
from discord.ext import commands
import wavelink

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def play(self, ctx, *, query: str):
        await ctx.send("Music commands ready (Lavalink required)")

async def setup(bot):
    await bot.add_cog(Music(bot))
