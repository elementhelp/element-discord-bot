import os
import discord
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")  # ia tokenul direct din Railway Variables

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Sunt logat ca {bot.user}")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong! 🏓")

bot.run(TOKEN)
