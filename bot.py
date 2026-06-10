import discord
from discord.ext import commands
import os
import aiosqlite
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.moderation = True  # Added for better moderation

class AdvancedBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=",",
            intents=intents,
            help_command=None
        )
        self.db = None

    async def setup_hook(self):
        self.db = await aiosqlite.connect("bot.db")
        await self.db.executescript("""
            CREATE TABLE IF NOT EXISTS warnings (
                user_id INTEGER,
                guild_id INTEGER,
                reason TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS tickets (
                channel_id INTEGER,
                user_id INTEGER,
                guild_id INTEGER,
                opened_at DATETIME
            );
            CREATE TABLE IF NOT EXISTS giveaways (
                message_id INTEGER,
                channel_id INTEGER,
                guild_id INTEGER,
                prize TEXT,
                end_time DATETIME,
                winners INTEGER
            );
        """)
        await self.db.commit()

        extensions = [
            "cogs.developer",
            "cogs.moderation",
            "cogs.giveaways",
            "cogs.tickets",
            "cogs.welcome",
            "cogs.automod",
            "cogs.customcmds",
            "cogs.levels",
            "cogs.music",
            "cogs.reaction_roles"
        ]
        
        for ext in extensions:
            try:
                await self.load_extension(ext)
                print(f"✅ Loaded {ext}")
            except Exception as e:
                print(f"❌ Failed to load {ext}: {e}")

        print("🚀 Blade Bot startup complete.")

bot = AdvancedBot()

@bot.event
async def on_ready():
    print(f"{bot.user} is online! | Blade Moderation System Ready")

if not TOKEN:
    raise ValueError("DISCORD_TOKEN environment variable is missing!")

bot.run(TOKEN)
