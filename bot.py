import discord
from discord.ext import commands
import os
import aiosqlite
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.moderation = True
intents.guilds = True

class AdvancedBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents, help_command=None)
        self.db = None

    async def setup_hook(self):
        self.db = await aiosqlite.connect("bot.db")
        
        await self.db.executescript('''
            CREATE TABLE IF NOT EXISTS warnings (user_id INTEGER, guild_id INTEGER, reason TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS mutes (user_id INTEGER, guild_id INTEGER, until TIMESTAMP);
            CREATE TABLE IF NOT EXISTS jails (user_id INTEGER, guild_id INTEGER, until TIMESTAMP, reason TEXT);
            CREATE TABLE IF NOT EXISTS tickets (channel_id INTEGER, user_id INTEGER, guild_id INTEGER, opened_at DATETIME);
            CREATE TABLE IF NOT EXISTS giveaways (message_id INTEGER, guild_id INTEGER, channel_id INTEGER, end_time TIMESTAMP, prize TEXT, winners INTEGER);
            CREATE TABLE IF NOT EXISTS server_settings (guild_id INTEGER PRIMARY KEY, prefix TEXT DEFAULT "!", mod_log INTEGER, ticket_category INTEGER);
        ''')
        await self.db.commit()

        # Load all cogs
        await self.load_extension("cogs.moderation")
        await self.load_extension("cogs.jail")
        await self.load_extension("cogs.tickets")
        await self.load_extension("cogs.modlog")
        await self.load_extension("cogs.reaction_roles")
        await self.load_extension("cogs.music")
        await self.load_extension("cogs.giveaways")
        await self.load_extension("cogs.developer")
        await self.load_extension("cogs.automod")
        await self.load_extension("cogs.utility")
        await self.load_extension("cogs.levels")
        await self.load_extension("cogs.welcome")
        await self.load_extension("cogs.customcmds")

        print("✅ All cogs loaded!")

bot = AdvancedBot()

@bot.event
async def on_ready():
    print(f'🚀 {bot.user} is now online!')
    await bot.tree.sync()

bot.run(TOKEN)
