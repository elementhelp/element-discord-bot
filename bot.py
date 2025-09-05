import os
import discord
from discord.ext import commands
from discord import app_commands
from supabase import create_client, Client

# ---------------------------
# ENV VARS
# ---------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------------------
# BOT SETUP
# ---------------------------
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# ---------------------------
# EVENTS
# ---------------------------
@bot.event
async def on_ready():
    print(f"✅ Bot connected as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"🔗 Synced {len(synced)} commands")
    except Exception as e:
        print(f"❌ Sync failed: {e}")

# ---------------------------
# COMMAND: Generate AutoJoiner
# ---------------------------
@bot.tree.command(name="generate-autojoiner", description="Generează scriptul AutoJoiner pentru user")
async def generate_autojoiner(interaction: discord.Interaction, webhook: str):
    await interaction.response.defer(ephemeral=True)

    key = str(interaction.user.id)  # cheia devine ID-ul userului
    user_id = str(interaction.user.id)

    # UPsert in Supabase (insert sau update dacă există deja)
    supabase.table("elements").upsert({
        "user_id": user_id,
        "username": interaction.user.name,
        "key": key,
        "webhook": webhook
    }, on_conflict=["user_id"]).execute()

    script = f'''-- AutoJoiner Script
KEY="{key}"
loadstring(game:HttpGet("https://element.up.railway.app/cdn/autojoiner.luau"))()'''

    await interaction.followup.send(
        f"✅ Script generat pentru {interaction.user.mention}\n```lua\n{script}\n```",
        ephemeral=True
    )

# ---------------------------
# RUN
# ---------------------------
bot.run(DISCORD_TOKEN)
