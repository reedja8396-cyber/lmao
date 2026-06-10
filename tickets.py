import discord
from discord.ext import commands
from discord.ui import View, Button
import datetime

class TicketView(View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Open Ticket", style=discord.ButtonStyle.green, emoji="🎟️")
    async def open_ticket(self, interaction: discord.Interaction, button: Button):
        guild = interaction.guild
        member = interaction.user
        category = discord.utils.get(guild.categories, name="Tickets") or await guild.create_category("Tickets")
        channel = await guild.create_text_channel(f"ticket-{member.name}", category=category, overwrites={
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            member: discord.PermissionOverwrite(read_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True)
        })
        await channel.send(f"{member.mention} Welcome! Use `!close` to close.")
        await interaction.response.send_message("Ticket created!", ephemeral=True)

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def ticketpanel(self, ctx):
        embed = discord.Embed(title="Support", description="Click to open ticket", color=discord.Color.green())
        await ctx.send(embed=embed, view=TicketView(self.bot))

    @commands.command()
    async def close(self, ctx, *, reason="No reason"):
        if "ticket" not in ctx.channel.name:
            return await ctx.send("Not a ticket channel.")
        transcript = []
        async for msg in ctx.channel.history(limit=None, oldest_first=True):
            transcript.append(f"{msg.author}: {msg.content}")
        with open(f"transcript_{ctx.channel.name}.txt", "w") as f:
            f.write("\n".join(transcript))
        await ctx.send("Closing ticket...", file=discord.File(f"transcript_{ctx.channel.name}.txt"))
        await ctx.channel.delete()

async def setup(bot):
    await bot.add_cog(Tickets(bot))
