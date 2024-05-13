import discord
from discord.ext import commands
from discord import app_commands
from datetime import timedelta
import confuse
import os

class moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='warn', brief='Warns a member.',help="Warns a member..Idk what else to tell you.`")
    async def warn(self, ctx, member: discord.Member,*,reason: str = None):
        await ctx.message.delete()
        embed = discord.Embed(title=f"You've been warned, {member.name}.",description=f"{member.mention}, due to breaking one or multiple rules of the server, a staff member has chosen to warn you. Reason given: {reason}.",color=discord.Color.red())
        embed.set_footer(text=f"Moderation command issued anonymously.")
        await ctx.send(embed=embed)

    @commands.command(name='kick')
    async def kick(self, ctx, member: discord.Member,*,reason: str = None):
        em = discord.Embed(title="Moderator action succesful.", description=f"User {member.name} has been kicked for reason: {reason}")
        em.color = discord.Color.yellow()
        em.set_footer(text="Follow our server rules and guidelines.")
        try:
            await member.kick(reason=reason)
            await ctx.send(embed=em)
        except Exception as e:
            print(e)
            pass


    @commands.hybrid_command(name='ban')
    async def ban(self, ctx, member: discord.Member,*,reason: str = None):
        em = discord.Embed(title="Moderator action succesful.", description=f"User {member.name} has been banned for reason: {reason}")
        em.color = discord.Color.red()
        em.set_footer(text="Follow our server rules and guidelines.")
        await member.ban(reason=reason)
        await ctx.send(embed=em)

    @commands.command(name='mute')
    async def mute(self, ctx, member: discord.Member,days: int, hours: int, minutes: int, seconds: int,*,reason: str):
        if member.id == ctx.author.id:
            await ctx.send("You can't timeout yourself!")
            return

        if member.guild_permissions.moderate_members:
            await ctx.send("You can't do this, this person is a moderator!")
            return

        duration = timedelta(days = days, hours = hours, minutes = minutes, seconds = seconds)
        if duration >= timedelta(days = 28): #added to check if time exceeds 28 days
                await ctx.send("I can't mute someone for more than 28 days!", ephemeral = True) #responds, but only the author can see the response
                return

        if reason == None:
                await member.timeout(duration)
                await ctx.reply(f"<@{member.id}> has been timed out for {days} days, {hours} hours, {minutes} minutes, and {seconds} seconds by <@{ctx.author.id}>.")
        else:
                await member.timeout(duration, reason = reason)
                await ctx.reply(f"<@{member.id}> has been timed out for {days} days, {hours} hours, {minutes} minutes, and {seconds} seconds by <@{ctx.author.id}> for reason: '{reason}'.")

