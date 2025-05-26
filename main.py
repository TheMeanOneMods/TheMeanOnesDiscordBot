import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command()
async def hello(ctx):
    await ctx.send('Hello! I am your Discord bot.')

@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong! Latency: {round(bot.latency * 1000)}ms')

bot.run(os.getenv('DISCORD_TOKEN'))