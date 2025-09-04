import os
import discord
from discord import app_commands
from discord.ext import commands
import uuid
from supabase import create_client, Client

# === Supabase ===
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# === Discord Bot ===
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Bot conectat ca {bot.user}")
    print(f"Slash commands sincronizate: {len(bot.tree.get_commands())}")

# === Comenzi ===
@bot.tree.command(name="generate", description="Generează un ID unic și loadstring Element")
async def generate(interaction: discord.Interaction):
    unique_id = str(uuid.uuid4())
    script = f'loadstring(game:HttpGet("https://raw.githubusercontent.com/JadeSCRIPTZ/VisualScripts/refs/heads/main/maaa"))() -- ID: {unique_id}'
    
    # Salvează în baza de date
    supabase.table("scripts").insert({"id": unique_id, "type": "element"}).execute()
    
    await interaction.response.send_message(f"🔑 ID: `{unique_id}`\n📜 Script:\n```lua\n{script}\n```", ephemeral=True)

@bot.tree.command(name="generate-autojoiner", description="Generează un ID unic și loadstring AutoJoiner")
async def generate_autojoiner(interaction: discord.Interaction):
    unique_id = str(uuid.uuid4())
    script = f'loadstring(game:HttpGet("https://raw.githubusercontent.com/JadeSCRIPTZ/VisualScripts/refs/heads/main/maaa"))() -- AUTOJOINER: {unique_id}'
    
    supabase.table("scripts").insert({"id": unique_id, "type": "autojoiner"}).execute()
    
    await interaction.response.send_message(f"🔑 ID: `{unique_id}`\n🤖 AutoJoiner:\n```lua\n{script}\n```", ephemeral=True)

bot.run(os.getenv("DISCORD_TOKEN"))
