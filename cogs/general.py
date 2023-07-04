###############################################
#           Template made by Person0z         #
#          https://github.com/Person0z        #
#           Copyright© Person0z, 2022         #
#           Do Not Remove This Header         #
###############################################

# Importing the required modules
import disnake
from disnake.ext import commands, tasks
import datetime
import os
import psutil 
import requests
import json
import aiohttp
import config
from helpers import checks, errors

class general(commands.Cog):
    
    def __init__(self, bot):
    	self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Loaded Cog General')

    # Bot CPU and RAM usage with storage usage
    @commands.slash_command(name='botinfo', description='Get info about the bot',)
    async def botinfo(self, inter: disnake.ApplicationCommandInteraction):
        cpu = psutil.cpu_percent()
        ram_used = psutil.virtual_memory().used / (1024.0 ** 3)
        ram_total = psutil.virtual_memory().total / (1024.0 ** 3)

        shard_info = ''
        for shard_id, shard in enumerate(self.bot.latencies):
            shard_info += f'Shard ID: {shard_id}, Latency: {shard[1]}\n'
        total_shards = len(self.bot.latencies)
        
        embed = disnake.Embed(title=f"{self.bot.user.name}'s Info", color=config.Success())
        embed.add_field(name="Bot Info", value=f"""
            Bot: ```{self.bot.user.name}#{self.bot.user.discriminator} ({self.bot.user.id})```
            Bot Created: ```{self.bot.user.created_at.strftime('%a, %#d %B %Y, %I:%M %p UTC')}```
            Bot CPU Usage: ```{cpu}% / 100%```
            Bot RAM Usage: ```{ram_used:.2f} GB / {ram_total:.2f} GB```
            Bot Swap Usage ```{psutil.swap_memory().used / (1024.0 ** 3):.2f} GB / {psutil.swap_memory().total / (1024.0 ** 3):.2f} GB```
            Bot Ping: ```{round(self.bot.latency * 1000)}ms```
            Bot Library: ```Disnake```
            Bot Developer: ```Person0z```
            Shard Info: ```{shard_info}```
            Total Shards: ```{total_shards}```
            Total Servers: ```{len(self.bot.guilds)}```
            Total Users: ```{sum(guild.member_count for guild in self.bot.guilds)}```
            """, inline=False)
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        embed.set_footer(text=f'Requested by {inter.author}', icon_url=inter.author.avatar.url)
        await inter.response.send_message(embed=embed)

    # invite the bot to your server
    @commands.slash_command(name='invite',
                            description='Invite the bot to your server',)
    async def invite(self, inter: disnake.ApplicationCommandInteraction):
        embed = disnake.Embed(title="Invite me, Pissle Radio!", color=config.Success())
        embed.add_field (name="Invite Link:", value=f"[Click Here (on this link to invite me!)](https://discord.com/oauth2/authorize?client_id={self.bot.user.id}&permissions={config.invite_perm}&scope=bot)", inline=False)
        embed.set_footer(text=f'Requested by {inter.author}', icon_url=inter.author.avatar.url)
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        await inter.response.send_message(embed=embed)
                
    @commands.slash_command(name='suggest', 
                            description='Suggest something to the creators of the bot')
    @commands.cooldown(1, 180, commands.BucketType.user) 
    async def suggest(
        self, 
        inter: disnake.ApplicationCommandInteraction,
        suggestion: str,
    ):
        # Get the guild (support server)
        guild = self.bot.get_guild(1121849705735929886)  # replace with the support server's ID
        if guild is None:
            raise Exception('Support server not found')
            
        # Get the channel
        channel = guild.get_channel(1121918891623469186)  # replace with the channel's ID in the support server
        if channel is None:
            raise Exception('Suggestions channel not found')
        
        # Create the embed
        embed = disnake.Embed(
            title=f'Suggestion - {inter.author} ({inter.user.id})',
            description=f'{inter.user} suggested that we: \n ```{suggestion}```',
            color=disnake.Color.green(),
        )
        embed.set_footer(text=f'Suggestion by {inter.author}', icon_url=inter.author.avatar.url)
        # Send the embed and add reactions
        message = await channel.send(embed=embed)
        await message.add_reaction('👍')
        await message.add_reaction('👎')

        await inter.response.send_message("Your suggestion has been sent! Thank you for your feedback.")

    @commands.slash_command(description="Get the changes in the latest update")
    async def update(inter: disnake.ApplicationCommandInteraction, version: str):
        updates = open("data/updates.json")
        updates_data = json.load(updates)

        matching_updates = []
        for update in updates_data.get("updates", []):
            if version.lower() in update.get("version", "").lower() or version.lower() in update.get("log", "").lower():
                matching_updates.append(update)

        if not matching_updates:
            embed = disnake.Embed(
                title="Updates",
                description=f"No updates found for version/log: {version}",
                color=disnake.Color.blue()
            )
        else:
            update_embeds = []
            for update in matching_updates:
                version_number = update.get("version")
                timestamp = update.get("timestamp")
                message = update.get("log")

                embed = disnake.Embed(
                    title=f"Update - Version: {version_number}",
                    description=message,
                    color=disnake.Color.blue()
                )
                embed.set_footer(text=f"Timestamp: {timestamp}")
                update_embeds.append(embed)

            await inter.send(embeds=update_embeds)

    @update.autocomplete('version')
    async def update_autocomplete(inter: disnake.ApplicationCommandInteraction, version: str):
        try:
            updates = open("data/updates.json")
            updates_data = json.load(updates)

            available_versions = []
            for update in updates_data.get("updates", []):
                update_version = update.get("version")
                if update_version and version.lower() in update_version.lower():
                    available_versions.append(update_version)

            return available_versions
        except Exception as e:
            print(f'Error sending update autocomplete: {e}')
            await inter.send('Failed')

    @commands.slash_command(description="Search the wiki for a specific entry")
    async def wiki(inter: disnake.ApplicationCommandInteraction, query: str):
        with open("data/wiki.json") as file:
            wiki_data = json.load(file)

        matching_entries = []
        for entry in wiki_data.get("entries", []):
            if query.lower() in entry.get("title", "").lower() or query.lower() in entry.get("content", "").lower():
                matching_entries.append(entry)

        if not matching_entries:
            embed = disnake.Embed(
                title="Wiki Search",
                description=f"No matching entries found for: {query}",
                color=disnake.Color.blue()
            )
        else:
            entry_embeds = []
            for entry in matching_entries:
                title = entry.get("title")
                content = entry.get("content")

                embed = disnake.Embed(
                    title=title,
                    description=content,
                    color=disnake.Color.blue()
                )
                entry_embeds.append(embed)

            await inter.send(embeds=entry_embeds)

    @wiki.autocomplete('query')
    async def wiki_autocomplete(inter: disnake.ApplicationCommandInteraction, query: str):
        with open("data/wiki.json") as file:
            wiki_data = json.load(file)

        available_queries = []
        for entry in wiki_data.get("entries", []):
            entry_title = entry.get("title")
            if entry_title and query.lower() in entry_title.lower():
                available_queries.append(entry_title)

        return available_queries

    # bot links for voting and stuff
    @commands.slash_command(description="Get the bot's links")
    async def links(inter: disnake.ApplicationCommandInteraction):
        embed = disnake.Embed(
            title="Bot Links",
            description="Here are some links for the bot",
            color=disnake.Color.blue()
        )
        embed.add_field(name="Top.gg Link", value="> [Top.gg Bot Link](https://top.gg/bot/1121848910839812126)", inline=True)
        embed.add_field(name="Support Server", value="> [Discord Server Invite](https://discord.gg/E3cs9ewqMP)", inline=True)
        embed.add_field(name="Vote Link", value="> [Top.gg Vote Link](https://top.gg/bot/1121848910839812126/vote)", inline=True)
        embed.add_field(name="Developer Github", value="> [Person0z's Github](https://github.com/Person0z)", inline=True)
        await inter.send(embed=embed)


def setup(bot):
    bot.add_cog(general(bot))