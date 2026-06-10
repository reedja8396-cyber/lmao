import discord
from discord.ext import commands

class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reaction_roles = {}

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def rr(self, ctx, emoji: str, role: discord.Role):
        message = ctx.message.reference.resolved if ctx.message.reference else (await ctx.channel.history(limit=1).__anext__())
        await message.add_reaction(emoji)
        await ctx.send("Reaction role set!")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        # Full logic in previous message
        pass

async def setup(bot):
    await bot.add_cog(ReactionRoles(bot))
