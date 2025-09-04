import discord
from discord.ext import commands
import os

TOKEN = os.getenv("DISCORD_TOKEN")  # cheia o pui în Render -> Environment

intents = discord.Intents.default()
intents.message_content = True  # ai nevoie pt comenzi text

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Botul este online ca {bot.user}!")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong! 🏓")

bot.run(TOKEN)
