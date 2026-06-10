import discord
from discord.ext import commands
from discord.ui import View, Button, Select
import asyncio
import os
import sys
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
        embed.add_field(name="Commands", value=len([c for c in self.bot.walk_commands()]), inline=True)
        embed.add_field(name="Cogs Loaded", value=len(self.bot.cogs), inline=True)
        embed.add_field(name="Python", value=platform.python_version(), inline=True)
        embed.add_field(name="discord.py", value=discord.__version__, inline=True)
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

    @discord.ui.button(label="Guilds", style=discord.ButtonStyle.blue, row=1)
    async def guilds_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer(ephemeral=True)
        guilds = "\n".join([f"• {g.name} ({g.id}) - {g.member_count} members" for g in self.bot.guilds[:15]])
        embed = discord.Embed(title=f"Servers ({len(self.bot.guilds)})", description=guilds or "None", color=discord.Color.blue())
        await interaction.followup.send(embed=embed, ephemeral=True)

    @discord.ui.button(label="Eval", style=discord.ButtonStyle.red, row=1)
    async def eval_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(EvalModal(self.bot))

    @discord.ui.button(label="Shutdown", style=discord.ButtonStyle.danger, row=1)
    async def shutdown_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("Shutting down...", ephemeral=True)
        await self.bot.close()

class EvalModal(discord.ui.Modal, title="Code Eval"):
    code = discord.ui.TextInput(label="Python Code", style=discord.TextStyle.paragraph, required=True, placeholder="print('Hello World')")

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            local_vars = {"bot": self.bot, "interaction": interaction, "discord": discord, "commands": commands}
            exec(self.code.value, local_vars)
            result = "Code executed successfully (no output)"
            if 'result' in local_vars:
                result = f"Result:\n{local_vars['result']}"
            await interaction.followup.send(result, ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"Error:\n{traceback.format_exc()}", ephemeral=True)

class Developer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if not hasattr(bot, "start_time"):
            bot.start_time = datetime.datetime.utcnow()

    @commands.command(name="devpanel", aliases=["dp", "panel", "dev"])
    @commands.is_owner()
    async def devpanel(self, ctx):
        """Opens the Developer Control Panel"""
        embed = discord.Embed(
            title="Developer Panel",
            description="Bot management tools",
            color=discord.Color.dark_purple()
        )
        embed.set_footer(text=f"Owner: {ctx.author} • {len(self.bot.cogs)} cogs loaded")
        
        view = DevPanel(self.bot)
        await ctx.send(embed=embed, view=view)

    # ==================== DEV COMMANDS ====================
    @commands.command()
    @commands.is_owner()
    async def inv(self, ctx):
        """Bot inventory & diagnostics"""
        embed = discord.Embed(title="Bot Inventory", color=discord.Color.blue())
        embed.add_field(name="Guilds", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="Commands", value=len(list(self.bot.walk_commands())), inline=True)
        embed.add_field(name="Cogs", value=len(self.bot.cogs), inline=True)
        embed.add_field(name="Latency", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        embed.add_field(name="Uptime", value=str(datetime.datetime.utcnow() - self.bot.start_time).split('.')[0], inline=True)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def status(self, ctx, *, activity: str = None):
        """Change bot status"""
        if not activity:
            await ctx.send("Usage: !status Playing with code")
            return
        await self.bot.change_presence(activity=discord.Game(name=activity))
        await ctx.send(f"Status updated to: {activity}")

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, *, cog: str = None):
        """Reload one or all cogs"""
        if not cog or cog.lower() == "all":
            for extension in list(self.bot.extensions):
                try:
                    await self.bot.reload_extension(extension)
                except Exception as e:
                    await ctx.send(f"Failed {extension}: {e}")
            await ctx.send("All cogs reloaded successfully!")
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
    async def guilds(self, ctx):
        """List all servers"""
        embed = discord.Embed(title=f"Servers ({len(self.bot.guilds)})", color=discord.Color.blue())
        for guild in self.bot.guilds:
            embed.add_field(name=guild.name, value=f"{guild.id} • {guild.member_count} members", inline=True)
        await ctx.send(embed=embed)

    @commands.command(name="eval")
    @commands.is_owner()
    async def _eval(self, ctx, *, code: str):
        """Evaluate Python code"""
        try:
            local_vars = {"ctx": ctx, "bot": self.bot, "discord": discord, "commands": commands}
            exec(code, local_vars)
            result = local_vars.get("result", "Executed (no output)")
            await ctx.send(f"```py\n{result}```")
        except Exception as e:
            await ctx.send(f"```py\n{traceback.format_exc()}```")

    @commands.command()
    @commands.is_owner()
    async def shutdown(self, ctx):
        """Shutdown the bot"""
        await ctx.send("Shutting down...")
        await self.bot.close()

    @commands.command()
    @commands.is_owner()
    async def ping(self, ctx):
        """Bot latency"""
        await ctx.send(f"Pong! {round(self.bot.latency * 1000)}ms")

    @commands.command()
    @commands.is_owner()
    async def logs(self, ctx, lines: int = 20):
        """Show recent bot logs"""
        try:
            with open("bot.log", "r", encoding="utf-8") as f:
                content = "".join(f.readlines()[-lines:])
            await ctx.send(f"```ansi\n{content[-1900:]}```")
        except:
            await ctx.send("No log file found.")

async def setup(bot):
    await bot.add_cog(Developer(bot))
    print("[Developer] Loaded with DevPanel")
