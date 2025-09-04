import discord
from discord.ext import commands
import os
import database  # importăm funcțiile din database.py

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"✅ Bot conectat ca {bot.user}")

@bot.event
async def on_member_join(member):
    database.add_user(str(member))  
    database.log_event(f"{member} s-a alăturat serverului")
    print(f"{member} adăugat în baza de date")

@bot.command()
async def users(ctx):
    users = database.get_users()
    lista = [u["username"] for u in users.data]
    await ctx.send("👥 Useri înregistrați: " + ", ".join(lista))

@bot.command()
async def elements(ctx):
    elems = database.get_elements()
    lista = [f"{e['name']} - {e['description']}" for e in elems.data]
    await ctx.send("🔹 Elemente: " + " | ".join(lista))

bot.run(os.getenv("DISCORD_TOKEN"))
