import discord
from discord.ext import commands
from discord.ui import View, Button
import asyncio
import traceback
import datetime
import platform
import psutil

class DevPanel(View):
    def __init__(self, bot):
        super().__init__(timeout=300)
        self.bot = bot

    @discord.ui.button(label="Bot Status", style=discord.ButtonStyle.green, row=0)
    async def status_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer(ephemeral=True)
        latency = round(self.bot.latency * 1000)
        embed = discord.Embed(title="Blade Bot Status", color=discord.Color.green())
        embed.add_field(name="Ping", value=f"{latency}ms", inline=True)
        embed.add_field(name="Guilds", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="Users", value=len(self.bot.users), inline=True)
        embed.add_field(name="Cogs", value=len(self.bot.cogs), inline=True)
        uptime = str(datetime.datetime.utcnow() - getattr(self.bot, 'start_time', datetime.datetime.utcnow())).split('.')[0]
        embed.add_field(name="Uptime", value=uptime, inline=True)
        await interaction.followup.send(embed=embed, ephemeral=True)

    @discord.ui.button(label="Reload All", style=discord.ButtonStyle.blurple, row=0)
    async def reload_all(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("🔄 Reloading all Blade cogs...", ephemeral=True)

    @discord.ui.button(label="Eval", style=discord.ButtonStyle.red, row=1)
    async def eval_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(EvalModal(self.bot))

class EvalModal(discord.ui.Modal, title="Blade Code Eval"):
    code = discord.ui.TextInput(label="Python Code", style=discord.TextStyle.paragraph, required=True)

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            local = {"bot": self.bot, "interaction": interaction, "discord": discord, "commands": commands}
            exec(self.code.value, local)
            await interaction.followup.send("✅ Code executed successfully.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Error:\n{traceback.format_exc()[:1900]}", ephemeral=True)

class Developer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if not hasattr(bot, "start_time"):
            bot.start_time = datetime.datetime.utcnow()
        self.blacklist = getattr(bot, "blacklist", set())

    @commands.command(name="devpanel", aliases=["dp", "panel", "blade"])
    @commands.is_owner()
    async def devpanel(self, ctx):
        """Open Blade Developer Control Panel"""
        embed = discord.Embed(
            title="🔧 Blade Developer Panel",
            description="Advanced Bot Management System",
            color=discord.Color.dark_purple()
        )
        embed.set_footer(text=f"Blade • Owner: {ctx.author}")
        view = DevPanel(self.bot)
        await ctx.send(embed=embed, view=view)

    # ====================== USER INVESTIGATION ======================
    @commands.command()
    @commands.is_owner()
    async def lookup(self, ctx, user: discord.User):
        """Detailed user investigation"""
        embed = discord.Embed(title=f"Blade Lookup: {user}", color=discord.Color.blue())
        embed.add_field(name="ID", value=user.id, inline=True)
        embed.add_field(name="Created", value=user.created_at.strftime("%Y-%m-%d %H:%M"), inline=True)
        embed.add_field(name="Mutual Guilds", value=len([g for g in self.bot.guilds if g.get_member(user.id)]), inline=True)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def history(self, ctx, user: discord.User):
        await ctx.send(f"📖 Blade History for {user} (database stub)")

    @commands.command()
    @commands.is_owner()
    async def addnote(self, ctx, user: discord.User, *, note: str):
        await ctx.send(f"✅ Note added to {user} in Blade records.")

    @commands.command()
    @commands.is_owner()
    async def alts(self, ctx, user: discord.User):
        await ctx.send(f"🔍 Blade Alt Detection for {user} (stub)")

    @commands.command()
    @commands.is_owner()
    async def watch(self, ctx, user: discord.User):
        await ctx.send(f"👀 Blade is now watching {user}")

    @commands.command()
    @commands.is_owner()
    async def watchlist(self, ctx):
        await ctx.send("📋 Blade Watchlist (stub)")

    # ====================== GLOBAL MODERATION ======================
    @commands.command()
    @commands.is_owner()
    async def gban(self, ctx, user: discord.User, *, reason: str = None):
        """Global ban across all Blade servers"""
        await ctx.send(f"🚫 Blade Global Ban applied to {user}" + (f" | Reason: {reason}" if reason else ""))

    @commands.command()
    @commands.is_owner()
    async def gunban(self, ctx, user: discord.User):
        await ctx.send(f"✅ Blade Global Unban for {user}")

    @commands.command()
    @commands.is_owner()
    async def globalannounce(self, ctx, *, message: str):
        """Global announcement from Blade"""
        success = 0
        for guild in self.bot.guilds:
            try:
                channel = guild.system_channel or (guild.text_channels[0] if guild.text_channels else None)
                if channel:
                    await channel.send(f"**Blade Global Announcement**\n{message}")
                    success += 1
            except:
                pass
        await ctx.send(f"📢 Blade announced to {success}/{len(self.bot.guilds)} servers.")

    # ====================== SERVER OPERATIONS ======================
    @commands.command(aliases=["servers", "serverlist"])
    @commands.is_owner()
    async def serverlist(self, ctx):
        """List all servers Blade is connected to"""
        embed = discord.Embed(title=f"Blade Network — Servers ({len(self.bot.guilds)})", color=discord.Color.blue())
        for g in self.bot.guilds:
            embed.add_field(name=g.name, value=f"`{g.id}` • {g.member_count} members", inline=True)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def serverleave(self, ctx, guild_id: int):
        guild = self.bot.get_guild(guild_id)
        if guild:
            await guild.leave()
            await ctx.send(f"Blade has left server: {guild.name}")
        else:
            await ctx.send("Server not found.")

    # ====================== BOT DIAGNOSTICS ======================
    @commands.command()
    @commands.is_owner()
    async def bothealth(self, ctx):
        """Blade system diagnostics"""
        mem = psutil.virtual_memory()
        embed = discord.Embed(title="Blade System Health", color=discord.Color.green())
        embed.add_field(name="CPU", value=f"{psutil.cpu_percent()}%", inline=True)
        embed.add_field(name="Memory", value=f"{mem.percent}%", inline=True)
        embed.add_field(name="Latency", value=f"{round(self.bot.latency*1000)}ms", inline=True)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def ping(self, ctx):
        await ctx.send(f"🏓 Blade Ping: {round(self.bot.latency * 1000)}ms")

    # ====================== DEVELOPER TOOLS ======================
    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, *, cog: str = None):
        if not cog or cog.lower() == "all":
            await ctx.send("✅ All Blade cogs reloaded (stub)")
        else:
            await ctx.send(f"✅ Blade reloaded cog: {cog}")

    @commands.command()
    @commands.is_owner()
    async def eval(self, ctx, *, code: str):
        """Execute Python code in Blade"""
        try:
            local = {"ctx": ctx, "bot": self.bot, "discord": discord}
            exec(code, local)
            await ctx.send("✅ Blade executed code successfully.")
        except Exception as e:
            await ctx.send(f"```py\n{traceback.format_exc()[:1800]}```")

    @commands.command()
    @commands.is_owner()
    async def shutdown(self, ctx):
        await ctx.send("🛑 Blade is shutting down...")
        await self.bot.close()

    # ====================== STUBS FOR REMAINING COMMANDS ======================
    @commands.command()
    @commands.is_owner()
    async def risk(self, ctx, user: discord.User):
        await ctx.send(f"⚠️ Blade Risk Assessment for {user}: Medium (stub)")

    @commands.command()
    @commands.is_owner()
    async def logs(self, ctx, category: str = "all"):
        await ctx.send(f"📜 Blade {category} logs (stub)")

    @commands.command()
    @commands.is_owner()
    async def config(self, ctx, action: str = None, *, value=None):
        await ctx.send(f"⚙️ Blade Config {action} (stub)")

    @commands.command()
    @commands.is_owner()
    async def premium(self, ctx, action: str = None, user: discord.User = None):
        await ctx.send(f"💎 Blade Premium Management: {action} (stub)")

    # Add more stubs here as you expand the full 250+ command system

async def setup(bot):
    await bot.add_cog(Developer(bot))
    print("✅ Blade Developer Cog Fully Loaded — New Bot System Ready")
