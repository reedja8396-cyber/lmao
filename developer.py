import discord
from discord.ext import commands
from discord.ui import View, Button
import asyncio
import traceback
import datetime
import platform

class DevPanel(View):
    def __init__(self, bot):
        super().__init__(timeout=300)
        self.bot = bot

    @discord.ui.button(label="Bot Status", style=discord.ButtonStyle.green, row=0)
    async def status_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer(ephemeral=True)
        latency = round(self.bot.latency * 1000)
        embed = discord.Embed(title="Bot Status", color=discord.Color.green())
        embed.add_field(name="Ping", value=f"{latency}ms", inline=True)
        embed.add_field(name="Guilds", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="Users", value=len(self.bot.users), inline=True)
        embed.add_field(name="Commands", value=len(list(self.bot.walk_commands())), inline=True)
        embed.add_field(name="Cogs", value=len(self.bot.cogs), inline=True)
        embed.add_field(name="Python", value=platform.python_version(), inline=True)
        embed.add_field(name="discord.py", value=discord.__version__, inline=True)
        uptime = str(datetime.datetime.utcnow() - self.bot.start_time).split('.')[0] if hasattr(self.bot, 'start_time') else "N/A"
        embed.add_field(name="Uptime", value=uptime, inline=True)
        await interaction.followup.send(embed=embed, ephemeral=True)

    @discord.ui.button(label="Reload All", style=discord.ButtonStyle.blurple, row=0)
    async def reload_all(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer(ephemeral=True)
        reloaded = []
        for cog in list(self.bot.extensions):
            try:
                await self.bot.reload_extension(cog)
                reloaded.append(cog.split('.')[-1])
            except Exception as e:
                await interaction.followup.send(f"Failed {cog}: {e}", ephemeral=True)
        await interaction.followup.send(f"Reloaded: {', '.join(reloaded)}", ephemeral=True)

    @discord.ui.button(label="List Cogs", style=discord.ButtonStyle.gray, row=0)
    async def list_cogs(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer(ephemeral=True)
        cogs = "\n".join([f"• {cog}" for cog in self.bot.cogs.keys()])
        await interaction.followup.send(f"Loaded Cogs:\n{cogs}", ephemeral=True)

    @discord.ui.button(label="Eval", style=discord.ButtonStyle.red, row=1)
    async def eval_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(EvalModal(self.bot))

    @discord.ui.button(label="Shutdown", style=discord.ButtonStyle.danger, row=1)
    async def shutdown_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("Shutting down...", ephemeral=True)
        await asyncio.sleep(1)
        await self.bot.close()

class EvalModal(discord.ui.Modal, title="Code Eval"):
    code = discord.ui.TextInput(label="Python Code", style=discord.TextStyle.paragraph, required=True)

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            local = {"bot": self.bot, "interaction": interaction, "discord": discord, "commands": commands}
            exec(self.code.value, local)
            result = local.get("result", "Executed successfully (no output)")
            await interaction.followup.send(f"Result:\n{result}", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"Error:\n{traceback.format_exc()}", ephemeral=True)

class Developer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if not hasattr(bot, "start_time"):
            bot.start_time = datetime.datetime.utcnow()
        self.blacklist = getattr(bot, "blacklist", set())

    @commands.command(name="devpanel", aliases=["dp", "panel", "dev"])
    @commands.is_owner()
    async def devpanel(self, ctx):
        """Open the Developer Panel"""
        embed = discord.Embed(title="Developer Panel", description="Bot management tools", color=discord.Color.dark_purple())
        embed.set_footer(text=f"Owner: {ctx.author} • {len(self.bot.cogs)} cogs")
        view = DevPanel(self.bot)
        await ctx.send(embed=embed, view=view)

    # ====================== CORE COMMANDS ======================
    @commands.command()
    @commands.is_owner()
    async def inv(self, ctx):
        """Bot inventory"""
        embed = discord.Embed(title="Bot Inventory", color=discord.Color.blue())
        embed.add_field(name="Guilds", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="Commands", value=len(list(self.bot.walk_commands())), inline=True)
        embed.add_field(name="Cogs", value=len(self.bot.cogs), inline=True)
        embed.add_field(name="Latency", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        uptime = str(datetime.datetime.utcnow() - self.bot.start_time).split('.')[0]
        embed.add_field(name="Uptime", value=uptime, inline=True)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def status(self, ctx, *, activity: str = None):
        """Change bot status"""
        if not activity:
            await ctx.send("Usage: `!status Playing something`")
            return
        await self.bot.change_presence(activity=discord.Game(name=activity))
        await ctx.send(f"Status updated to: {activity}")

    # ====================== MODERATION TOOLS ======================
    @commands.command()
    @commands.is_owner()
    async def unban(self, ctx, user_id: int):
        """Unban a user by ID"""
        try:
            user = await self.bot.fetch_user(user_id)
            await ctx.guild.unban(user)
            await ctx.send(f"Unbanned {user} ({user_id})")
        except Exception as e:
            await ctx.send(f"Failed to unban: {e}")

    @commands.command()
    @commands.is_owner()
    async def timeoutall(self, ctx, minutes: int = 10):
        """Timeout all members in the current server (owner only)"""
        if not ctx.guild:
            return await ctx.send("Use in a server")
        count = 0
        for member in ctx.guild.members:
            if not member.bot and member.top_role < ctx.guild.me.top_role:
                try:
                    await member.timeout(datetime.timedelta(minutes=minutes))
                    count += 1
                except:
                    pass
        await ctx.send(f"Timed out {count} members for {minutes} minutes.")

    @commands.command()
    @commands.is_owner()
    async def stripall(self, ctx):
        """Strip all roles from everyone (dangerous)"""
        if not ctx.guild:
            return await ctx.send("Use in a server")
        count = 0
        for member in ctx.guild.members:
            if member.top_role < ctx.guild.me.top_role and not member.bot:
                try:
                    await member.edit(roles=[])
                    count += 1
                except:
                    pass
        await ctx.send(f"Stripped roles from {count} members.")

    # ====================== SERVER & BOT MANAGEMENT ======================
    @commands.command(aliases=["servers"])
    @commands.is_owner()
    async def guilds(self, ctx):
        """List all servers"""
        embed = discord.Embed(title=f"Servers ({len(self.bot.guilds)})", color=discord.Color.blue())
        for g in self.bot.guilds:
            embed.add_field(name=g.name, value=f"ID: {g.id}\nMembers: {g.member_count}", inline=True)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def serverinfo(self, ctx, guild_id: int = None):
        """Server details"""
        guild = ctx.guild if not guild_id else self.bot.get_guild(guild_id)
        if not guild:
            return await ctx.send("Guild not found")
        embed = discord.Embed(title=f"Server: {guild.name}", color=discord.Color.blue())
        embed.add_field(name="ID", value=guild.id, inline=True)
        embed.add_field(name="Members", value=guild.member_count, inline=True)
        embed.add_field(name="Channels", value=len(guild.channels), inline=True)
        embed.add_field(name="Roles", value=len(guild.roles), inline=True)
        embed.add_field(name="Owner", value=guild.owner, inline=True)
        await ctx.send(embed=embed)

    # ====================== BLACKLIST ======================
    @commands.command()
    @commands.is_owner()
    async def blacklist(self, ctx, user_id: int):
        """Blacklist a user"""
        self.blacklist.add(user_id)
        self.bot.blacklist = self.blacklist
        await ctx.send(f"Blacklisted user {user_id}")

    @commands.command()
    @commands.is_owner()
    async def unblacklist(self, ctx, user_id: int):
        """Unblacklist a user"""
        self.blacklist.discard(user_id)
        self.bot.blacklist = self.blacklist
        await ctx.send(f"Unblacklisted user {user_id}")

    # ====================== UTILITIES ======================
    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, *, cog: str = None):
        """Reload cog(s)"""
        if not cog or cog.lower() == "all":
            for ext in list(self.bot.extensions):
                try:
                    await self.bot.reload_extension(ext)
                except Exception as e:
                    await ctx.send(f"Failed {ext}: {e}")
            await ctx.send("All cogs reloaded!")
        else:
            try:
                name = f"cogs.{cog}" if not cog.startswith("cogs.") else cog
                await self.bot.reload_extension(name)
                await ctx.send(f"Reloaded {cog}")
            except Exception as e:
                await ctx.send(f"Failed: {e}")

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, cog: str):
        """Load a cog"""
        try:
            await self.bot.load_extension(f"cogs.{cog}")
            await ctx.send(f"Loaded {cog}")
        except Exception as e:
            await ctx.send(f"Failed: {e}")

    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx, cog: str):
        """Unload a cog"""
        try:
            await self.bot.unload_extension(f"cogs.{cog}")
            await ctx.send(f"Unloaded {cog}")
        except Exception as e:
            await ctx.send(f"Failed: {e}")

    @commands.command()
    @commands.is_owner()
    async def ping(self, ctx):
        """Latency"""
        await ctx.send(f"Pong! {round(self.bot.latency * 1000)}ms")

    @commands.command()
    @commands.is_owner()
    async def logs(self, ctx, lines: int = 30):
        """Show recent logs"""
        try:
            with open("bot.log", "r", encoding="utf-8") as f:
                content = "".join(f.readlines()[-lines:])
            await ctx.send(f"```ansi\n{content[-1900:]}```")
        except Exception:
            await ctx.send("No log file found or unable to read.")

    @commands.command(name="eval")
    @commands.is_owner()
    async def _eval(self, ctx, *, code: str):
        """Evaluate Python code"""
        try:
            local = {"ctx": ctx, "bot": self.bot, "discord": discord}
            exec(code, local)
            result = local.get("result", "Executed (no output)")
            await ctx.send(f"```py\n{result}```")
        except Exception as e:
            await ctx.send(f"```py\n{traceback.format_exc()}```")

    @commands.command()
    @commands.is_owner()
    async def shutdown(self, ctx):
        """Shutdown bot"""
        await ctx.send("Shutting down...")
        await self.bot.close()

async def setup(bot):
    await bot.add_cog(Developer(bot))
    print("[Developer] Loaded with full DevPanel")
