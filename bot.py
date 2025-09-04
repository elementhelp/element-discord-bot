import os
import uuid
import discord
from discord import app_commands
from discord.ext import commands
from supabase import create_client, Client

# Variabilele din environment
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Conectare Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Inițializare bot
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Loadstring de test (tu îl poți schimba oricând)
TEST_LOADSTRING = 'loadstring(game:HttpGet("https://raw.githubusercontent.com/JadeSCRIPTZ/VisualScripts/refs/heads/main/maaa"))()'


@bot.event
async def on_ready():
    print(f"✅ Bot conectat ca {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Slash commands sincronizate: {len(synced)}")
    except Exception as e:
        print(f"❌ Eroare sync: {e}")


# /generate
@bot.tree.command(name="generate", description="Generează un ID și un element loadstring.")
async def generate(interaction: discord.Interaction):
    unique_id = str(uuid.uuid4())
    data = {
        "id": unique_id,
        "type": "element",
        "script": TEST_LOADSTRING,
    }
    supabase.table("elements").insert(data).execute()
    await interaction.response.send_message(
        f"🔑 ID generat: `{unique_id}`\n📜 Loadstring:\n```lua\n{TEST_LOADSTRING}\n```"
    )


# /generate-autojoiner
@bot.tree.command(name="generate-autojoiner", description="Generează un ID pentru autojoiner.")
async def generate_autojoiner(interaction: discord.Interaction):
    unique_id = str(uuid.uuid4())
    data = {
        "id": unique_id,
        "type": "autojoiner",
        "script": TEST_LOADSTRING,
    }
    supabase.table("elements").insert(data).execute()
    await interaction.response.send_message(
        f"🤖 Autojoiner ID: `{unique_id}`\n📜 Loadstring:\n```lua\n{TEST_LOADSTRING}\n```"
    )


bot.run(DISCORD_TOKEN)
