import discord
import os
from discord.ext import commands
from flask import Flask
import threading

# ======================
# BOT DISCORD
# ======================

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Botul este online ca {bot.user}")

@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong!")

# ======================
# SERVER FLASK (pentru uptime)
# ======================

app = Flask('')

@app.route('/')
def home():
    return "Botul rulează și este online!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = threading.Thread(target=run)
    t.start()

# ======================
# PORNIRE
# ======================
if __name__ == "__main__":
    keep_alive()
    bot.run(os.getenv("DISCORD_TOKEN"))
