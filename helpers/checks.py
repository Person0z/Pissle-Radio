import disnake
from disnake.ext import commands
import config
import json

def is_owner():
    async def predicate(inter):
        if str(inter.author.id) in config.owner_ids:
            return True
        else:
            await inter.response.send_message("You cannot use this command, it is reserved for the bot developer only.", ephemeral=True)
            return False
    return commands.check(predicate)

def is_guild():
    async def predicate(inter):
        with open("data/guilds.json", "r") as file:
            guilds = json.load(file)
        if str(inter.guild_id) in guilds["guild_ids"]:
            return True
        else:
            await inter.response.send_message("You cannot use this command, you do not have a verified server ID.", ephemeral=True)
            return False
    return commands.check(predicate)

def is_owner_guild():
    async def predicate(inter):
        if str(inter.author.id) in config.owner_ids:
            return True
        else:
            await inter.response.send_message("You cannot use this command, please join the Pissle Radio Discord to verify your server and get access to more features!", ephemeral=True)
            return False
    return commands.check(predicate)