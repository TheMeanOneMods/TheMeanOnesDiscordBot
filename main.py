import discord
from discord import app_commands
import os

intents = discord.Intents.default()
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await tree.sync()
    print("Slash commands synced")

@tree.command(name="hello", description="Say hello to the bot")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("Hello! I am your Discord bot.")

@tree.command(name="ping", description="Check bot latency")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong! Latency: {round(bot.latency * 1000)}ms")

bot.run(os.getenv('DISCORD_TOKEN'))
