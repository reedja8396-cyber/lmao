import discord
from discord.ext import commands
import re

BAD_WORDS = ["examplebadword"]

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot: return
        if any(word in message.content.lower() for word in BAD_WORDS):
            await message.delete()

async def setup(bot):
    await bot.add_cog(AutoMod(bot))
