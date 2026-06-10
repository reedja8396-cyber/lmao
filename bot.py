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

class AdvancedBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
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
        """)

        await self.db.commit()

        extensions = [
            "automod",
            "customcmds",
            "developer",
            "giveaways",
            "levels",
            "music",
            "reaction_roles",
            "tickets",
            "welcome"
        ]

        for ext in extensions:
            try:
                await self.load_extension(ext)
                print(f"Loaded {ext}")
            except Exception as e:
                print(f"Failed to load {ext}: {e}")

        print("Bot startup complete.")

bot = AdvancedBot()

@bot.event
async def on_ready():
    print(f"{bot.user} is online!")

if not TOKEN:
    raise ValueError("DISCORD_TOKEN environment variable is missing!")

bot.run(TOKEN)
