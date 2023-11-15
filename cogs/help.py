###############################################
#           Template made by Person0z         #
#          https://github.com/Person0z        #
#           Copyright© Person0z, 2022         #
#           Do Not Remove This Header         #
###############################################

# Importing the required modules
import disnake
from disnake.ext import commands, tasks
from helpers import checks, errors
import config

# code 
class Help(commands.Cog):

    def __init__(self, bot):
    	self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Loaded Cog Help')

    # Help Command with subcommands 
    @commands.slash_command(description='Shows useful (or not) info about the bot')
    async def help(
        inter: disnake.ApplicationCommandInteraction,
        action: str = commands.Param(choices=["general", 'radio']),
    ):
        try:
            if action == "general":
                embedVar = disnake.Embed(
                    title="General Commands!",
                    description="Check important commands, that you can use!",
                    colour=config.Success())
                embedVar.add_field(name="Bot Prefix", value="```/ + !```", inline=False)
                embedVar.add_field(name="General Commands",
                                    value=
                                        "```/botinfo - Shows useful (or not) info about the bot```" +
                                        "```/invite - Invite the bot to your server```" +
                                        "```/suggest [suggestion] - Suggest something to the creators of the bot!```" +
                                        "```/report [report] - Report an issue about the bot, users or radio stations to the developers!```" +
                                        "```/update [version] - Gives update logs that happens on the bot daily!```" +
                                        "```/links - This will get you the links for the bot.```" +
                                        "```/wiki - You can get some info about the bot here, how it works and more!```",
                                        inline=False)
                embedVar.add_field(name="Additional Support", value="If you require more support or questions feel free to join the [Pissle Radio Discord](https://discord.gg/wjZfP86RaC)")
                embedVar.set_thumbnail(
                    url=inter.bot.user.avatar.url
                )
                await inter.response.send_message(embed=embedVar, delete_after=15)

            if action == "radio":
                embedVar = disnake.Embed(
                    title="Radio Commands!",
                    description="Check important commands, that you can use!",
                    colour=config.Success())
                embedVar.add_field(name="Bot Prefix", value="```/ (Slash Commands)```", inline=False)
                embedVar.add_field(name="Radio Commands",
                                    value=
                                    "```/radio continent:[] country:[] action:[] - Start a radio station```" +
                                    "```/play - this command only works for verified servers, it plays custom links and file audio```"
                                    "```/disconnect - Stop a radio station```" +
                                    "```/join - Joins a voice channel```" +
                                    "```/volume [0-100] - Sets a volume server wide for the bot (server wide, admins only)```" +
                                    "```/mute - mutes the bot until unmuted. Shows an icon to show the bot is muted!```",
                                    inline=False)
                embedVar.add_field(name="Additional Support", value="If you require more support or questions feel free to join the [Pissle Radio Discord](https://discord.gg/wjZfP86RaC)")
                embedVar.set_thumbnail(
                    url=inter.bot.user.avatar.url
                )
                await inter.response.send_message(embed=embedVar, delete_after=15)
        except Exception as e:
            print(f'Error sending help message: {e}')
            await inter.send(embed=errors.create_error_embed(f"Error sending help command: {e}"))

def setup(bot):
    bot.add_cog(Help(bot))