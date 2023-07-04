###############################################
#           Template made by Person0z         #
#          https://github.com/Person0z        #
#           Copyright© Person0z, 2022         #
#           Do Not Remove This Header         #
###############################################

# Importing the required modules
import disnake
from disnake.ext import commands, tasks
from helpers import checks
import config
import json
import asyncio
import sys
import os

radio_player = None

# Creating the class
class owner(commands.Cog):
    def __init__(self, bot):
    	self.bot = bot
        
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Loaded Cog Owner')

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        bot_voice_channel = member.guild.voice_client
        if bot_voice_channel and len(bot_voice_channel.channel.members) == 1 and bot_voice_channel.channel.members[0] == self.bot.user:
            await asyncio.sleep(2)
        if bot_voice_channel and len(bot_voice_channel.channel.members) == 1 and bot_voice_channel.channel.members[0] == self.bot.user:
            await bot_voice_channel.disconnect()
            print(f"Left {bot_voice_channel.channel.name} due to inactivity.")

    # A slash command to raise an error
    @commands.slash_command(name="error", description="Command that raises an error")
    @checks.is_owner()
    async def error_command(inter: disnake.ApplicationCommandInteraction):
        raise ValueError("This is a deliberate error for testing purposes.")

    # A slash command to blacklist a user from using the bot
    @commands.slash_command(description="Toggle a user's blacklist status")
    @checks.is_owner()
    async def blacklist(self, ctx, user: disnake.User):
        with open('data/blacklist.json', 'r') as file:
            blacklist = json.load(file)
        if str(user.id) in blacklist['blacklisted_ids']:
            blacklist['blacklisted_ids'].remove(str(user.id))
            action = 'unblacklisted'
        else:
            blacklist['blacklisted_ids'].append(str(user.id))
            action = 'blacklisted'
        with open('data/blacklist.json', 'w') as file:
            json.dump(blacklist, file, indent=4)
        await ctx.send(f'{user} has been {action}.')

    # A slash command to restart the bot
    @commands.slash_command(name="restart", description="Restarts the bot", guild=config.guilds_ids)
    @checks.is_owner()
    async def restart(self, inter: disnake.ApplicationCommandInteraction):
        # Pause all radio stations (if implemented)
        if radio_player is not None:
            radio_player.pause_all()
        # Play the restart message
        voice_client = disnake.utils.get(self.bot.voice_clients, guild=inter.guild)
        if voice_client is not None and voice_client.is_connected():
            voice_client.stop()
            voice_client.play(disnake.FFmpegPCMAudio('assets/restart.mp3'))
        # Send a message to the user
        await inter.send("Restarting the bot, please hold tight...", ephemeral=True)
        # Wait 10 seconds
        await asyncio.sleep(10)
        # Disconnect from the voice channel (if connected)
        if voice_client is not None and voice_client.is_connected():
            await voice_client.disconnect()
        # Restart the bot
        os.execl(sys.executable, sys.executable, *sys.argv)

    # A slash command to reload cogs
    @commands.slash_command(name="reload", description="Reloads a cog", guild=config.guilds_ids)
    @checks.is_owner()
    async def reload(self, inter: disnake.ApplicationCommandInteraction, cog: str):
        try:
            self.bot.reload_extension(f"cogs.{cog}")
            await inter.send(f'Reloaded the cog: ``{cog}``', ephemeral=True)
        except Exception as e:
            await inter.send(f'Failed to reload the cog: ``{cog}``', ephemeral=True)

def setup(bot):
    bot.add_cog(owner(bot))