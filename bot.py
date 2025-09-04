import os
import discord
from discord.ext import commands

# luăm tokenul din variabilele Railway (ENV)
TOKEN = os.getenv("DISCORD_TOKEN")

# intențiile botului
intents = discord.Intents.default()
intents.message_content = True  # ca să poată citi mesaje

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Botul este online ca {bot.user}")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong! 🏓")

bot.run(TOKEN)
