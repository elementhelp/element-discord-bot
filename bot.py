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
# UTILS
# ---------------------------
def generate_key() -> str:
    """Generate a unique KEY for the user"""
    random_part = secrets.token_urlsafe(24)
    return f"ELEMENT${random_part}"


@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Bot connected as {bot.user}")


# ---------------------------
# SET WEBHOOK
# ---------------------------
@tree.command(name="setwebhook", description="Set your webhook")
async def set_webhook(interaction: discord.Interaction, webhook: str):
    user_id = str(interaction.user.id)

    existing = supabase.table("elements").select("id").eq("user_id", user_id).execute()
    if existing.data:
        supabase.table("elements").update({"webhook": webhook}).eq("user_id", user_id).execute()
    else:
        supabase.table("elements").insert({"user_id": user_id, "webhook": webhook}).execute()

    await interaction.response.send_message(
        f"Webhook set `{webhook}`",
        ephemeral=True
    )


# ---------------------------
# SET USERNAME
# ---------------------------
@tree.command(name="setusername", description="Set your username")
async def set_username(interaction: discord.Interaction, username: str):
    user_id = str(interaction.user.id)

    existing = supabase.table("elements").select("id").eq("user_id", user_id).execute()
    if existing.data:
        supabase.table("elements").update({"username": username}).eq("user_id", user_id).execute()
    else:
        supabase.table("elements").insert({"user_id": user_id, "username": username}).execute()

    await interaction.response.send_message(
        f"Username set `{username}`",
        ephemeral=True
    )


# ---------------------------
# GENERATE ELEMENT SCRIPT (shows ID, not KEY)
# ---------------------------
@tree.command(name="generate", description="Generate your Element Script")
async def generate(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    existing = supabase.table("elements").select("id, webhook, username, key").eq("user_id", user_id).execute()

    if not existing.data:
        await interaction.response.send_message(
            "❌ No record found. Please use `/setwebhook` and `/setusername` first.",
            ephemeral=True
        )
        return

    element = existing.data[0]
    element_id = element["id"]
    webhook = element.get("webhook", "⚠️ Not set")
    username = element.get("username", "⚠️ Not set")

    # ensure KEY exists in DB for autojoiner
    if not element.get("key"):
        new_key = generate_key()
        supabase.table("elements").update({"key": new_key}).eq("id", element_id).execute()

    msg = (
        "## Your Element Script\n"
        f"Webhook: `{webhook}`\n"
        f"Username: `{username}`\n\n"
        "```lua\n"
        f'ID="{element_id}";\n'
        f'loadstring(game:HttpGet("{AUTOJOINER_URL}"))()\n'
        "```"
    )

    await interaction.response.send_message(msg, ephemeral=True)


# ---------------------------
# GENERATE AUTOJOINER SCRIPT (shows KEY + loadstring)
# ---------------------------
@tree.command(name="generate-autojoiner", description="Generate your Auto Joiner Script")
async def generate_autojoiner(interaction: discord.Interaction):
    user_id = str(interaction.user.id)

    existing = supabase.table("elements").select("id, key").eq("user_id", user_id).execute()
    if not existing.data:
        await interaction.response.send_message(
            "❌ No record found. Please use `/generate` first.",
            ephemeral=True
        )
        return

    element = existing.data[0]
    element_id = element["id"]
    key = element.get("key")

    if not key:
        key = generate_key()
        supabase.table("elements").update({"key": key}).eq("id", element_id).execute()

    msg = (
        "## DON'T SHARE! THIS CONTAINS YOUR PRIVATE KEY!\n\n"
        "```lua\n"
        f'KEY="{key}"\n'
        f'loadstring(game:HttpGet("{AUTOJOINER_URL}"))()\n'
        "```"
    )

    await interaction.response.send_message(msg, ephemeral=True)


# ---------------------------
# RUN BOT
# ---------------------------
bot.run(TOKEN)
