###############################################
#           Template made by Person0z         #
#          https://github.com/Person0z        #
#           Copyright© Person0z, 2022         #
#           Do Not Remove This Header         #
###############################################

import json
import typing
import disnake
from disnake.ext import commands
import asyncio
import random
import config
from datetime import datetime
from helpers import checks, errors

is_muted = False

class voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.radio_playing = {}

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Loaded Cog voice')

    @commands.slash_command(description='Start a radio station in your voice channel')
    @commands.cooldown(1, 15, commands.BucketType.user) 
    async def radio(
        inter: disnake.ApplicationCommandInteraction,
        country: typing.Literal["US - United States", "UK - United Kingdom", "FR - France", "AF - Africa", "PH - Philippines", "TR - Turkey", "RU - Russia"],
        action: str
    ):
        stations = open("data/stations.json")
        _stations = json.load(stations)
        if inter.author.voice is None:
            embed = disnake.Embed(
                title="Radio", description="```You are not in a voice channel.```", color=disnake.Color.red())
            return await inter.send(embed=embed)

        voice_client = inter.author.voice.channel.guild.voice_client

        if voice_client is None:
            await inter.author.voice.channel.connect()
            voice_client = inter.author.voice.channel.guild.voice_client

        if voice_client.is_playing():
            voice_client.stop()

        source = disnake.PCMVolumeTransformer(
            disnake.FFmpegPCMAudio(_stations[f"{country}_Stations"][action]))
        voice_client.play(source, after=lambda e: print(
            f'Player error: {e}') if e else None)

        embed = disnake.Embed(
            title="Radio | Connect", description=f"```Now playing {action} in {inter.author.voice.channel}```", color=disnake.Color.green())

        embed.set_thumbnail(url=_stations[f"{country}_Images"][action])
        embed.set_footer(
            text=f"Requested by {inter.author}", icon_url=inter.author.avatar.url)

        await inter.send(embed=embed)

    @radio.autocomplete('action')
    async def radio_audiocomplete(self, inter: disnake.ApplicationCommandInteraction, action: str):
        stations = []
        country = inter.filled_options["country"]
        with open("data/stations.json") as f:
            data = json.load(f)
            for i in data[f"{country}_Stations"]:
                if action in i:
                    stations.append(i)
        return stations
            
    @commands.slash_command(name="disconnect", description="Disconnects the bot from the voice channel")
    @commands.cooldown(1, 15, commands.BucketType.user) 
    async def disconnect(inter: disnake.ApplicationCommandInteraction):
        voice_client = inter.guild.voice_client
        if voice_client is None:
            embed = disnake.Embed(
                title="Radio | Disconnect", description="```I am not currently connected to any voice channels.```", color=disnake.Color.red())
            embed.set_footer(
                text=f"Requested by {inter.author}", icon_url=inter.author.avatar.url)
            embed.set_thumbnail(url=inter.guild.me.avatar.url)
            await inter.send(embed=embed)
        else:
            await voice_client.disconnect()
            embed = disnake.Embed(
                title="Radio | Disconnect", description="```I have successfully disconnected from the voice channel.```", color=disnake.Color.green())
            embed.set_footer(
                text=f"Requested by {inter.author}", icon_url=inter.author.avatar.url)
            embed.set_thumbnail(url=inter.guild.me.avatar.url)
            await inter.send(embed=embed)
            
    @commands.slash_command(description='Edit the volume of the bot in your voice channel')
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def volume(self, ctx, volume: int):
        guild = ctx.guild
        voice_client = guild.voice_client
        if voice_client is None:
            embed = disnake.Embed(title='Volume | Error', description='Not connected to a Voice Channel, please join one and try again', color=config.Error())
            return await ctx.send(embed=embed)
        if volume > 100:
            volume = 100
            embed = disnake.Embed(title='Volume | Error', description='The volume cannot be set higher than 100%', color=config.Error())
            return await ctx.send(embed=embed)
        elif volume < 0:
            volume = 0
        voice_client.source.volume = volume / 100
        embed = disnake.Embed(title='Volume | Control', description=f'The volume has been changed and set to {volume}%. Run this command again to change it!', color=config.Success())
        message = await ctx.send(embed=embed)
        await asyncio.sleep(10)

    @commands.slash_command(description="Mutes the bot in the voice channel until unmuted (server wide)")
    @commands.cooldown(1, 5, commands.BucketType.user) 
    async def mute(self, ctx):
        global is_muted
        is_muted = not is_muted
        guild = ctx.guild
        voice_client = guild.voice_client
        if voice_client is None:
            embed = disnake.Embed(title='Mute | Error', description='Not connected to a Voice Channel, please join one and try again', color=config.Error())
            return await ctx.send(embed=embed)
        
        voice_client.source.volume = 0 if is_muted else 1
        status = "muted" if is_muted else "unmuted"
        bot_member = guild.get_member(self.bot.user.id)
        
        # Update bot's nickname with mute emoji
        new_nickname = f"{bot_member.display_name} (Muted 🔇)" if is_muted else bot_member.name
        await bot_member.edit(nick=new_nickname)
        
        embed = disnake.Embed(title='Mute | Control', description=f'The bot has been {status}.', color=config.Success())
        message = await ctx.send(embed=embed)
        await asyncio.sleep(10)

    @commands.slash_command(description="Play a custom stream link (does not work with youtube links)")
    async def play(self, ctx, link: str):
        if ctx.author.voice is None:
            embed = disnake.Embed(
                title="Play", description="You are not in a voice channel.", color=disnake.Color.red())
            await ctx.send(embed=embed)
            return

        voice_channel = ctx.author.voice.channel
        voice_client = disnake.utils.get(ctx.bot.voice_clients, guild=ctx.guild)

        if voice_client:
            if voice_client.channel != voice_channel:
                await voice_client.move_to(voice_channel)
        else:
            voice_client = await voice_channel.connect()

        voice_client.stop()  # Stop any currently playing audio

        audio_source = disnake.FFmpegOpusAudio(link)
        voice_client.play(audio_source)
        embed = disnake.Embed(title="Custom Station Play", description=f"**Now playing stream:** \n> {link}", color=config.Success())
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
        embed.set_thumbnail(url=ctx.guild.me.avatar.url)
        await ctx.send(embed=embed)

    # join command
    @commands.slash_command(description="Joins the voice channel you are in")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def join(self, ctx):
        if ctx.author.voice is None:
            embed = disnake.Embed(
                title="Join", description="You are not in a voice channel.", color=config.Error())
            await ctx.send(embed=embed)
            return

        voice_channel = ctx.author.voice.channel
        voice_client = disnake.utils.get(ctx.bot.voice_clients, guild=ctx.guild)

        if voice_client:
            if voice_client.channel != voice_channel:
                await voice_client.move_to(voice_channel)
        else:
            voice_client = await voice_channel.connect()

        embed = disnake.Embed(
            title="Join a Voice Channel", description=f"Joined ```{voice_channel.name}```", color=config.Success())
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(voice(bot))