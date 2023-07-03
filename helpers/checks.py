import disnake
from disnake.ext import commands
import config
import json

def is_owner():
    async def predicate(inter):
        if inter.author.id == config.owner_ids:
            return True
        else:
            await inter.response.send_message("You cannot use this command, it is reserved for the bot developer only.", ephemeral=True)
            return False
    return commands.check(predicate)