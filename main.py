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
    try:
        raise error
    except commands.CommandOnCooldown as e:
        await inter.response.send_message(f"This command is on cooldown. Please try again in {e.retry_after:.2f} seconds.", ephemeral=True)
    except Exception as e:
        await inter.response.send_message("**An error occurred while processing your command.**\n> This has already been logged **and** already sent to the developer.\n\n- For more support join: https://discord.gg/E3cs9ewqMP", ephemeral=True)
        command_name = inter.data['name']
        logging.error(f"An error occurred in command '/{command_name}': {type(e).__name__}: {e}")

@bot.event
async def on_voice_state_update(member, before, after):
    if member.id == bot.user.id:  # Check if the member is the bot itself
        if before.deaf != after.deaf:  # Check if the deaf state has changed
            await member.edit(deafen=True)  # Deafen the bot

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
    print(f"In: {len(bot.guilds)} server(s) | {len(bot.users)} user(s)") 
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