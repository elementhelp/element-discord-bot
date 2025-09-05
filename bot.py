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

ELEMENT_URL = "https://raw.githubusercontent.com/elementhelp/script/refs/heads/main/element"
AUTOJOINER_URL = "https://raw.githubusercontent.com/elementhelp/script/refs/heads/main/autojoiner"

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

    existing = supabase.table("elements").select("*").eq("user_id", user_id).execute()

    if existing.data:
        element_id = existing.data[0]["id"]
        supabase.table("elements").update({
            "custom_username": username
        }).eq("user_id", user_id).execute()
    else:
        element_id = str(uuid.uuid4())
        supabase.table("elements").insert({
            "id": element_id,
            "user_id": user_id,
            "custom_username": username,
            "script_code": element_id
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
        element_id = existing.data[0]["id"]
        supabase.table("elements").update({
            "webhook": webhook
        }).eq("user_id", user_id).execute()
    else:
        element_id = str(uuid.uuid4())
        supabase.table("elements").insert({
            "id": element_id,
            "user_id": user_id,
            "webhook": webhook,
            "script_code": element_id
        }).execute()

    await interaction.response.send_message(f"✅ Webhook setat: ||{webhook}||", ephemeral=True)

# -----------------------------
# /generate (Element Script)
# -----------------------------
@tree.command(name="generate", description="Generează scriptul tău personalizat (Element)")
async def generate(interaction: discord.Interaction):
    user_id = str(interaction.user.id)

    existing = supabase.table("elements").select("*").eq("user_id", user_id).execute()
    if not existing.data:
        await interaction.response.send_message("❌ Mai întâi folosește `/setusername` și `/setwebhook`.", ephemeral=True)
        return

    data = existing.data[0]
    element_id = data["id"]
    webhook = data.get("webhook") or "https://discord.com/api/webhooks/placeholder"
    username = data.get("custom_username") or "default_user"

    loadstring = f'loadstring(game:HttpGet("{ELEMENT_URL}"))()'

    msg = (
        f"🤖 **Your Element Script**\n"
        f"🔑 ID: `{element_id}`\n"
        f"📜 Loadstring:\n```lua\n{loadstring}\n```\n"
        f"🌐 Webhook: {webhook}\n"
        f"👤 Username: {username}"
    )

    await interaction.response.send_message(msg, ephemeral=True)

# -----------------------------
# /generate-autojoiner
# -----------------------------
@tree.command(name="generate-autojoiner", description="Generează scriptul autojoiner pentru tine")
async def generate_autojoiner(interaction: discord.Interaction):
    user_id = str(interaction.user.id)

    existing = supabase.table("elements").select("id").eq("user_id", user_id).execute()
    if not existing.data:
        await interaction.response.send_message("❌ Folosește mai întâi `/generate` ca să îți creezi un ID.", ephemeral=True)
        return

    element_id = existing.data[0]["id"]
    loadstring = f'loadstring(game:HttpGet("{AUTOJOINER_URL}"))()'

    msg = (
        f"🤖 **Your Autojoiner**\n"
        f"🔑 Autojoiner ID: `{element_id}`\n"
        f"📜 Loadstring:\n```lua\n{loadstring}\n```"
    )

    await interaction.response.send_message(msg, ephemeral=True)

# -----------------------------
# RUN
# -----------------------------
bot.run(TOKEN)
