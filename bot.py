import os
import uuid
import secrets
import discord
from discord.ext import commands
from supabase import create_client, Client

# ====== CONFIG ======
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

ELEMENT_URL = "https://element.up.railway.app/cdn/element.luau"
AUTOJOINER_URL = "https://element.up.railway.app/cdn/autojoiner.luau"

# ====== INIT ======
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# ====== HELPERS ======
def generate_id():
    return str(uuid.uuid4())

def generate_key():
    return "ELEMENT$" + secrets.token_urlsafe(24)


# ====== COMMANDS ======
@bot.tree.command(name="setwebhook", description="Set your webhook URL")
async def setwebhook(interaction: discord.Interaction, webhook: str):
    user_id = str(interaction.user.id)
    supabase.table("elements").upsert({
        "user_id": user_id,
        "webhook": webhook
    }).execute()

    await interaction.response.send_message(
        f"Webhook set `{webhook}`", ephemeral=True
    )


@bot.tree.command(name="setusername", description="Set your Roblox username")
async def setusername(interaction: discord.Interaction, username: str):
    user_id = str(interaction.user.id)
    supabase.table("elements").upsert({
        "user_id": user_id,
        "username": username
    }).execute()

    await interaction.response.send_message(
        f"Username set `{username}`", ephemeral=True
    )


@bot.tree.command(name="generate", description="Generate your Element Script")
async def generate(interaction: discord.Interaction):
    user_id = str(interaction.user.id)

    # get user info
    data = supabase.table("elements").select("id, username, webhook").eq("user_id", user_id).execute()
    record = data.data[0] if data.data else None

    if record and record.get("id"):
        element_id = record["id"]
    else:
        element_id = generate_id()
        supabase.table("elements").upsert({
            "user_id": user_id,
            "id": element_id
        }).execute()

    username = record["username"] if record else None
    webhook = record["webhook"] if record else None

    msg = (
        f"## Your Element Script\n"
        f"Webhook: `{webhook}`\n"
        f"Username: `{username}`\n\n"
        f"```lua\n"
        f'ID="{element_id}"\n'
        f'loadstring(game:HttpGet("{ELEMENT_URL}"))()\n'
        f"```"
    )

    await interaction.response.send_message(msg, ephemeral=True)


@bot.tree.command(name="generate-autojoiner", description="Generate your Autojoiner Script")
async def generate_autojoiner(interaction: discord.Interaction):
    user_id = str(interaction.user.id)

    data = supabase.table("elements").select("key").eq("user_id", user_id).execute()
    record = data.data[0] if data.data else None

    if record and record.get("key"):
        key = record["key"]
    else:
        key = generate_key()
        supabase.table("elements").upsert({
            "user_id": user_id,
            "key": key
        }).execute()

    msg = (
        f"## ⚠️ DON'T SHARE! THIS CONTAINS YOUR PRIVATE KEY! ⚠️\n\n"
        f"```lua\n"
        f'KEY="{key}"\n'
        f'loadstring(game:HttpGet("{AUTOJOINER_URL}"))()\n'
        f"```"
    )

    await interaction.response.send_message(msg, ephemeral=True)


# ====== START ======
@bot.event
async def on_ready():
    print(f"✅ Bot connected as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"🔗 Synced {len(synced)} commands")
    except Exception as e:
        print(f"❌ Sync error: {e}")


bot.run(DISCORD_TOKEN)
