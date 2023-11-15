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

    @commands.slash_command(description='Initiate a radio station broadcast in your current voice channel')
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def radio(
        inter: disnake.ApplicationCommandInteraction,
        continent: typing.Literal["North America", "Europe", "South America", "Asia", "Africa"],
        country: str,
        action: str
    ):
        await inter.response.defer()

        stations_file = "data/stations.json"
        with open(stations_file, "r") as file:
            stations_data = json.load(file)

        if inter.author.voice is None:
            embed = disnake.Embed(
                title="Radio", description="```You are not connected to a voice channel.```", color=disnake.Color.red())
            return await inter.send(embed=embed)

        voice_client = inter.author.voice.channel.guild.voice_client

        if voice_client is None:
            await inter.author.voice.channel.connect()
            voice_client = inter.author.voice.channel.guild.voice_client

        if voice_client.is_playing():
            voice_client.stop()

        continent_stations = stations_data.get(f"{continent}_Stations", {})
        country_stations = continent_stations.get(country, {})
        station_url = country_stations.get(action)

        if not station_url:
            embed = disnake.Embed(
                title="Radio", description="```Selected station information not available.```", color=disnake.Color.red())
            return await inter.send(embed=embed)

        source = disnake.PCMVolumeTransformer(
            disnake.FFmpegPCMAudio(station_url, before_options=''), volume=0.2)  # Adjust the volume here
        voice_client.play(source, after=lambda e: print(
            f'Player error: {e}') if e else None)

        embed = disnake.Embed(
            title="Radio | Connection Established", description=f"```Now playing {action} in {inter.author.voice.channel}```", color=disnake.Color.green())

        continent_images = stations_data.get(f"{continent}_Images", {})
        country_images = continent_images.get(country, {})
        image = country_images.get(action, "")
        if image:
            embed.set_thumbnail(url=image)

        embed.set_footer(
            text=f"Requested by {inter.author}", icon_url=inter.author.avatar.url)

        await inter.send(embed=embed)


    @radio.autocomplete('country')
    async def radio_autocomplete_country(self, inter: disnake.ApplicationCommandInteraction, country: str):
        continent = inter.filled_options["continent"]
        available_countries = {
            "North America": ["United States"],
            "South America": ["Colombia"],
            "Europe": ["United Kingdom", "France", "Sweden"],
            "Asia": ["Philippines", "Russia", "India"],
            "Africa": ["Africa", "Juba"]
        }
        filtered_countries = available_countries.get(continent, [])
        return [c for c in filtered_countries if country in c]

    @radio.autocomplete('action')
    async def radio_autocomplete_action(self, inter: disnake.ApplicationCommandInteraction, action: str):
        continent = inter.filled_options["continent"]
        country = inter.filled_options["country"]
        stations = open("data/stations.json")
        _stations = json.load(stations)
        available_actions = _stations[f"{continent}_Stations"][country].keys()
        return [a for a in available_actions if action in a]

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
            
    @commands.slash_command(description="Volume control for the radio")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def volume(inter: disnake.ApplicationCommandInteraction, volume: int):
        voice_client = inter.guild.voice_client
        if voice_client is None:
            embed = disnake.Embed(
                title="Radio | Volume",
                description="```I am not currently connected to any voice channels.```",
                color=disnake.Color.red()
            )
            embed.set_footer(
                text=f"Requested by {inter.author}", icon_url=inter.author.avatar.url
            )
            embed.set_thumbnail(url=inter.guild.me.avatar.url)
            await inter.response.send_message(embed=embed)
        else:
            max_ffmpeg_volume = 0.2
            if volume > 100:
                embed = disnake.Embed(
                    title="Radio | Volume",
                    description="```Volume cannot be higher than 100```",
                    color=disnake.Color.red()
                )
                embed.set_footer(
                    text=f"Requested by {inter.author}", icon_url=inter.author.avatar.url
                )
                embed.set_thumbnail(url=inter.guild.me.avatar.url)
                await inter.response.send_message(embed=embed)
            else:
                adjusted_volume = int(volume * max_ffmpeg_volume)
                voice_client.source.volume = adjusted_volume / 100
                embed = disnake.Embed(
                    title="Radio | Volume",
                    description=f"```Volume set to {adjusted_volume}% of maximum (20%)```",
                    color=disnake.Color.green()
                )
                embed.set_footer(
                    text=f"Requested by {inter.author}", icon_url=inter.author.avatar.url
                )
                embed.set_thumbnail(url=inter.guild.me.avatar.url)
                await inter.response.send_message(embed=embed)

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
        
        embed = disnake.Embed(title='Mute | Control', description=f'The bot has been {status}.', color=config.Success())
        message = await ctx.send(embed=embed)
        await asyncio.sleep(10)

    @commands.slash_command(description="Play a custom stream link (does not work with youtube links)")
    @checks.is_guild()
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