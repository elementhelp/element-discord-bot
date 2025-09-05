import os
import discord
from discord.ext import commands
from discord import app_commands
from supabase import create_client, Client
import uuid

# -----------------------------
# CONFIG
# -----------------------------
TOKEN = os.getenv("DISCORD_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# -----------------------------
# EVENTS
# -----------------------------
@bot.event
async def on_ready():
    print(f"✅ Bot conectat ca {bot.user}")
    try:
        synced = await tree.sync()
        print(f"Slash commands sincronizate: {len(synced)}")
    except Exception as e:
        print(f"Eroare sync: {e}")

# -----------------------------
# /setusername
# -----------------------------
@tree.command(name="setusername", description="Setează un username personalizat pentru element script")
async def set_username(interaction: discord.Interaction, username: str):
    user_id = str(interaction.user.id)

    # Verifică dacă există deja
    existing = supabase.table("elements").select("*").eq("user_id", user_id).execute()

    if existing.data:
        # facem update, dar păstrăm script_code existent dacă e
        current_code = existing.data[0].get("script_code") or str(uuid.uuid4())
        supabase.table("elements").update({
            "custom_username": username,
            "script_code": current_code
        }).eq("user_id", user_id).execute()
    else:
        # dacă nu există, inserăm cu script_code random
        supabase.table("elements").insert({
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "custom_username": username,
            "script_code": str(uuid.uuid4()),
        }).execute()

    await interaction.response.send_message(f"✅ Username setat: **{username}**", ephemeral=True)

# -----------------------------
# /setwebhook
# -----------------------------
@tree.command(name="setwebhook", description="Setează un webhook URL pentru element script")
async def set_webhook(interaction: discord.Interaction, webhook: str):
    user_id = str(interaction.user.id)

    existing = supabase.table("elements").select("*").eq("user_id", user_id).execute()

    if existing.data:
        current_code = existing.data[0].get("script_code") or str(uuid.uuid4())
        supabase.table("elements").update({
            "webhook": webhook,
            "script_code": current_code
        }).eq("user_id", user_id).execute()
    else:
        supabase.table("elements").insert({
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "webhook": webhook,
            "script_code": str(uuid.uuid4()),
        }).execute()

    await interaction.response.send_message(f"✅ Webhook setat: ||{webhook}||", ephemeral=True)

# -----------------------------
# /generate
# -----------------------------
@tree.command(name="generate", description="Generează scriptul tău personalizat")
async def generate(interaction: discord.Interaction):
    user_id = str(interaction.user.id)

    existing = supabase.table("elements").select("*").eq("user_id", user_id).execute()

    if not existing.data:
        await interaction.response.send_message("❌ Mai întâi folosește `/setusername` și `/setwebhook`.", ephemeral=True)
        return

    data = existing.data[0]
    script_code = data.get("script_code") or str(uuid.uuid4())
    webhook = data.get("webhook") or "https://discord.com/api/webhooks/placeholder"
    username = data.get("custom_username") or "default_user"

    # linkurile de la tine
    element_url = "https://raw.githubusercontent.com/elementhelp/script/refs/heads/main/element"

    # loadstring personalizat
    script = f'''-- Element Script Generated
_G.USERNAME = "{username}"
_G.WEBHOOK = "{webhook}"
_G.ID = "{script_code}"

loadstring(game:HttpGet("{element_url}"))()
'''

    await interaction.response.send_message(
        f"✅ Script generat pentru tine:\n```lua\n{script}\n```", ephemeral=True
    )

# -----------------------------
# RUN
# -----------------------------
bot.run(TOKEN)
