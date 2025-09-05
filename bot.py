import os
import uuid
import discord
from discord import app_commands
from discord.ext import commands
from supabase import create_client, Client

# Variabile din environment (Railway -> Variables)
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Conectare Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Inițializare bot
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

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
    user_id = str(interaction.user.id)

    existing = supabase.table("elements").select("id, script_code").eq("user_id", user_id).execute()

    if existing.data:
        element_id = existing.data[0]["id"]
        script = existing.data[0]["script_code"]
    else:
        element_id = str(uuid.uuid4())
        script = TEST_LOADSTRING
        supabase.table("elements").insert({
            "id": element_id,
            "user_id": user_id,
            "script_code": script
        }).execute()

    await interaction.response.send_message(
        f"Your element script:\n"
        f"ID = `{element_id}`\n"
        f"📜 Loadstring:\n```lua\n{script}\n```",
        ephemeral=True
    )


# /generate-autojoiner
@bot.tree.command(name="generate-autojoiner", description="Generează un ID pentru autojoiner.")
async def generate_autojoiner(interaction: discord.Interaction):
    element_id = str(uuid.uuid4())
    script = TEST_LOADSTRING

    supabase.table("elements").insert({
        "id": element_id,
        "user_id": str(interaction.user.id),
        "script_code": script
    }).execute()

    await interaction.response.send_message(
        f"🤖 Autojoiner ID: `{element_id}`\n📜 Loadstring:\n```lua\n{script}\n```",
        ephemeral=True
    )


bot.run(DISCORD_TOKEN)
