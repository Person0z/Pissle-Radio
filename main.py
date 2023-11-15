###############################################
#           Template made by Person0z         #
#          https://github.com/Person0z        #
#           Copyright© Person0z, 2022         #
#           Do Not Remove This Header         #
###############################################

# Imports Don't Remove any!!
import disnake
from disnake.ext import commands, tasks
import asyncio
import os
import platform
import random
import json
import sys
import config
from helpers import checks, errors
import traceback
import logging
import datetime

# Global Variables
blacklisted_ids = set()
logging.basicConfig(filename='data/error.log', format='%(asctime)s - %(levelname)s - %(message)s')

# Load the blacklist data
def load_blacklist():
    global blacklisted_ids
    with open('data/blacklist.json') as f:
        blacklist_data = json.load(f)
        blacklisted_ids = set(blacklist_data.get('blacklisted_ids', []))

# Bot Prefix
bot = commands.AutoShardedInteractionBot(
    intents=disnake.Intents.default(),
    status=disnake.Status.online,
    )

radio_player = None
voice_channel = None
voice_clients = {}  # Dictionary to store voice clients per server

# Load the initial blacklist data
load_blacklist()

@bot.slash_command_check
async def global_blacklist_check(inter: disnake.ApplicationCommandInteraction):
    load_blacklist()  # Reload the blacklist data on every command invocation
    if str(inter.author.id) in blacklisted_ids:
        await inter.response.send_message("You are blacklisted and cannot use this command or any command on this bot.", ephemeral=True)
        return False
    return True

@bot.event
async def on_slash_command_error(inter, error):
    guild = bot.get_guild(config.guilds_ids)
    if guild is None:
        raise Exception('Server not found')

    channel = guild.get_channel(config.logs_channel)
    if channel is None:
        raise Exception('Channel not found')

    command_name = inter.data['name']  # Moved this line up

    if isinstance(error, commands.CommandOnCooldown):
        await inter.response.send_message(f"This command is on cooldown. Please try again in {error.retry_after:.2f} seconds.", ephemeral=True)
    else:
        # Create the embed
        embed = disnake.Embed(
            title=f'Error in command: {command_name}',
            description=f'An error occurred in command /{command_name}: {type(error).__name__}: {error}',
            color=disnake.Color.red(),
        )
        embed.set_footer(text=f'Report by {inter.author}', icon_url=inter.author.avatar.url)

        error_message = "**An error occurred while processing your command.**\n> This error has been logged and sent to the developer for investigation.\n\nFor more support, join: [Discord Support Server](https://discord.gg/E3cs9ewqMP)"
        await inter.response.send_message(error_message, ephemeral=True)

        logging.error(f"An error occurred in command '/{command_name}': {type(error).__name__}: {error}")
        message = await channel.send(embed=embed)

# auto deafen on join
@bot.event
async def on_voice_state_update(member, before, after):
    if member == bot.user and after.channel is not None:
        await member.guild.change_voice_state(channel=after.channel, self_deaf=True, self_mute=False)

# On Ready
@bot.event
async def on_ready():
    print('###############################################')
    print('#           Template made by Person0z         #')
    print('#          https://github.com/Person0z        #')
    print('#           Copyright© Person0z, 2023         #') 
    print('###############################################')
    print('')
    print('')
    print('===============================================')
    print("The bot is ready!")
    print(f'Logged in as {bot.user.name}#{bot.user.discriminator} | {bot.user.id}')
    print(f"In: {len(bot.guilds)} server(s) | {sum(guild.member_count for guild in bot.guilds)} user(s)") 
    print(f'Running on {platform.system()} {platform.release()} ({os.name})')
    print(f"Disnake version : {disnake.__version__}")
    print(f"Python version: {platform.python_version()}")
    print('===============================================')
    print('')
    print('')
    print('================== Loaded Cogs ================')
    status_task.start()
    await asyncio.sleep(0.01)
    print('===============================================')

# Status Task
@tasks.loop(minutes=0.15)
async def status_task():
    await bot.change_presence(activity=disnake.Game(random.choice(config.activity)))

# Load Cogs On Start
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

#Bot Token
bot.run(config.token, reconnect=True)