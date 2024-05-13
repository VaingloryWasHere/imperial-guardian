import discord
from discord.ext import commands

class Helper(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True,case_insensitive=True)
    async def help(self, ctx):
    	#Default help command
    	em = discord.Embed(title="Commands List",description="This is a generic help list. For more information, type ?help <command name>")
    	for command in self.bot.commands:
            if command.cog_name == "Helper":
                pass #ignoring helper commands - @help.command
            em.add_field(name=command.name, value=command.brief, inline=True)
    	await ctx.send(embed=em)

    @help.command()
    async def test(self, ctx):
    	await ctx.send("!")