import os
import discord
from discord.ext import commands
from cogs.helper import Helper
from cogs.economy import EcoCore, EcoInventory, EcoFruitsCore
intents = discord.Intents.all()

bot = commands.Bot(command_prefix='?', intents=intents, case_insensitive=True)
bot.remove_command("help")

@bot.event
async def on_ready():
    print("INITIALISED!")
    await bot.add_cog(Helper(bot))
    await bot.add_cog(EcoCore(bot))
    await bot.add_cog(EcoInventory(bot))
    await bot.add_cog(EcoFruitsCore(bot))

    @bot.command(brief="Shows bot latency.")
    async def ping(ctx):
        ping = round(bot.latency * 1000, 3)
        await ctx.send(f'Pong! **Latency is {ping} miliseconds**')

# @bot.event
# async def on_command_error(ctx, exception):
#     if isinstance(exception, commands.CommandOnCooldown):
#         minute_time = (exception.retry_after / 60) / 60
#         await ctx.send(f"Command is on cooldown. Please, try again in **{round(minute_time,1)}** hours.")
#     else:
#         print(exception)
bot.run('Nzk5NjQxMDc4NzU1NjIyOTUz.GKWaiW.NnmcvFCIGoyvecoL6dh2ZnG6HaN6VW7VgPv9TE')