import os
import uuid
import discord
from discord import app_commands
from discord.ext import commands
from supabase import create_client, Client

# ---------------- ENV ----------------
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------- BOT INIT ----------------
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"✅ Bot conectat ca {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Slash commands sincronizate: {len(synced)}")
    except Exception as e:
        print(f"❌ Eroare sync: {e}")


# ---------------- SET WEBHOOK ----------------
@bot.tree.command(name="setwebhook", description="Setează webhook-ul pentru raportare")
async def set_webhook(interaction: discord.Interaction, webhook: str):
    user_id = str(interaction.user.id)

    existing = supabase.table("elements").select("id").eq("user_id", user_id).execute()

    if existing.data:
        supabase.table("elements").update({"webhook": webhook}).eq("user_id", user_id).execute()
    else:
        supabase.table("elements").insert({
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "webhook": webhook,
            "custom_username": None
        }).execute()

    await interaction.response.send_message(f"✅ Webhook setat cu succes: `{webhook}`", ephemeral=True)


# ---------------- SET USERNAME ----------------
@bot.tree.command(name="setusername", description="Setează un username custom pentru raportare")
async def set_username(interaction: discord.Interaction, username: str):
    user_id = str(interaction.user.id)

    existing = supabase.table("elements").select("id").eq("user_id", user_id).execute()

    if existing.data:
        supabase.table("elements").update({"custom_username": username}).eq("user_id", user_id).execute()
    else:
        supabase.table("elements").insert({
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "webhook": None,
            "custom_username": username
        }).execute()

    await interaction.response.send_message(f"✅ Username setat cu succes: `{username}`", ephemeral=True)


# ---------------- GENERATE SCRIPT ----------------
@bot.tree.command(name="generate", description="Generează scriptul personalizat Element")
async def generate(interaction: discord.Interaction):
    user_id = str(interaction.user.id)

    existing = supabase.table("elements").select("id, webhook, custom_username").eq("user_id", user_id).execute()

    if not existing.data:
        await interaction.response.send_message("❌ Nu ai setat webhook sau username! Folosește /setwebhook și /setusername.", ephemeral=True)
        return

    element_id = existing.data[0]["id"]
    webhook = existing.data[0].get("webhook", "Not set")
    username = existing.data[0].get("custom_username", "Not set")

    # aici pui linkul la repo-ul tău GitHub unde va fi element.lua
    script = f'loadstring(game:HttpGet("https://raw.githubusercontent.com/elementhelp/script/refs/heads/main/element"))()'

    await interaction.response.send_message(
        f"**Your Element Script**\n"
        f"🔗 Webhook: `{webhook}`\n"
        f"👤 Username: `{username}`\n\n"
        f"```lua\nID = \"{element_id}\"\n{script}\n```",
        ephemeral=True
    )


bot.run(DISCORD_TOKEN)
