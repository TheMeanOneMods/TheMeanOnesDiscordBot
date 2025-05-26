import discord
from discord import app_commands
import os
import asyncio

# Set up intents for member events and message content (for logging)
intents = discord.Intents.default()
intents.members = True  # For welcome messages
intents.message_content = True  # For message logging
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

# Channel IDs for logging and welcome messages (replace with your channel IDs)
LOG_CHANNEL_ID = 123456789012345678  # Replace with your log channel ID
WELCOME_CHANNEL_ID = 123456789012345678  # Replace with your welcome channel ID
REACTION_ROLE_MESSAGE_ID = 123456789012345678  # Replace with your reaction role message ID
ROLE_EMOJI_MAP = {
    "👍": 123456789012345678,  # Replace with role ID for 👍 reaction
    "👎": 123456789012345678   # Replace with role ID for 👎 reaction
}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    try:
        # Sync slash commands
        await tree.sync()
        print("Slash commands synced")
        # Ensure reaction role message exists
        channel = bot.get_channel(WELCOME_CHANNEL_ID)
        if channel:
            try:
                message = await channel.fetch_message(REACTION_ROLE_MESSAGE_ID)
                for emoji in ROLE_EMOJI_MAP.keys():
                    await message.add_reaction(emoji)
            except discord.NotFound:
                message = await channel.send("React to this message to get roles!")
                for emoji in ROLE_EMOJI_MAP.keys():
                    await message.add_reaction(emoji)
                print(f"Created reaction role message with ID: {message.id}")
    except Exception as e:
        print(f"Error in on_ready: {e}")

# Slash Commands
@tree.command(name="hello", description="Say hello to the bot")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("Hello! I am an advanced Discord bot!")

@tree.command(name="ping", description="Check bot latency")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong! Latency: {round(bot.latency * 1000)}ms")

@tree.command(name="kick", description="Kick a member from the server")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    try:
        await member.kick(reason=reason)
        await interaction.response.send_message(f"Kicked {member.mention} for: {reason}")
    except discord.Forbidden:
        await interaction.response.send_message("I don't have permission to kick members!")

@tree.command(name="ban", description="Ban a member from the server")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    try:
        await member.ban(reason=reason)
        await interaction.response.send_message(f"Banned {member.mention} for: {reason}")
    except discord.Forbidden:
        await interaction.response.send_message("I don't have permission to ban members!")

# Welcome Message
@bot.event
async def on_member_join(member: discord.Member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        await channel.send(f"Welcome {member.mention} to the server! Please check out the rules and enjoy your stay!")

# Message Logging
@bot.event
async def on_message_delete(message: discord.Message):
    if message.author.bot:
        return  # Ignore bot messages
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        embed = discord.Embed(title="Message Deleted", color=discord.Color.red())
        embed.add_field(name="Author", value=message.author.mention, inline=False)
        embed.add_field(name="Channel", value=message.channel.mention, inline=False)
        embed.add_field(name="Content", value=message.content or "No content (e.g., embed)", inline=False)
        embed.set_footer(text=f"Message ID: {message.id}")
        await log_channel.send(embed=embed)

# Reaction Roles
@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    if payload.message_id != REACTION_ROLE_MESSAGE_ID:
        return
    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)
    if member.bot:
        return
    emoji = str(payload.emoji)
    if emoji in ROLE_EMOJI_MAP:
        role_id = ROLE_EMOJI_MAP[emoji]
        role = guild.get_role(role_id)
        if role:
            await member.add_roles(role)
            await member.send(f"You received the {role.name} role!")

@bot.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
    if payload.message_id != REACTION_ROLE_MESSAGE_ID:
        return
    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)
    if member.bot:
        return
    emoji = str(payload.emoji)
    if emoji in ROLE_EMOJI_MAP:
        role_id = ROLE_EMOJI_MAP[emoji]
        role = guild.get_role(role_id)
        if role:
            await member.remove_roles(role)
            await member.send(f"The {role.name} role was removed!")

# Error Handling for Commands
@tree.error
async def on_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("You don't have permission to use this command!", ephemeral=True)
    else:
        await interaction.response.send_message(f"An error occurred: {str(error)}", ephemeral=True)

# Run the bot
bot.run(os.getenv('DISCORD_TOKEN'))
