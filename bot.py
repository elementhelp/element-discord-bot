import os
import discord
from discord.ext import commands
from discord import app_commands
from supabase import create_client
import uuid

# 🔑 Variabile din .env (trebuie puse în Railway/Replit/Render)
TOKEN = os.getenv("DISCORD_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Bot online ca {bot.user}")

# /generate -> creează element normal
@bot.tree.command(name="generate", description="Generează un ID și un element nou")
async def generate(interaction: discord.Interaction):
    element_id = str(uuid.uuid4())[:8]  # ID scurt
    loadstring = 'loadstring(game:HttpGet("https://raw.githubusercontent.com/JadeSCRIPTZ/VisualScripts/refs/heads/main/maaa"))()'

    # salvăm în DB
    supabase.table("elements").insert({
        "id": element_id,
        "type": "element",
        "loadstring": loadstring
    }).execute()

    await interaction.response.send_message(
        f"✅ Generat Element!\n**ID:** `{element_id}`\n**Loadstring:** ```{loadstring}```"
    )

# /generate-autojoiner -> creează autojoiner
@bot.tree.command(name="generate-autojoiner", description="Generează un ID și un autojoiner nou")
async def generate_autojoiner(interaction: discord.Interaction):
    element_id = str(uuid.uuid4())[:8]
    loadstring = 'loadstring(game:HttpGet("https://raw.githubusercontent.com/JadeSCRIPTZ/VisualScripts/refs/heads/main/maaa"))()'

    supabase.table("elements").insert({
        "id": element_id,
        "type": "autojoiner",
        "loadstring": loadstring
    }).execute()

    await interaction.response.send_message(
        f"✅ Generat AutoJoiner!\n**ID:** `{element_id}`\n**Loadstring:** ```{loadstring}```"
    )

bot.run(TOKEN)
