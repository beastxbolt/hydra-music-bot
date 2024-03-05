import discord
from discord.ext import commands
import os
from botprefix import prefix
from config import bot_token

intents = discord.Intents.all()
bot = commands.AutoShardedBot(command_prefix=prefix, strip_after_prefix=True, case_insensitive=True, intents=intents)

bot.music = {}
bot.voice_client_attributes = {}
bot.recent_invokes = {}
bot.restart_time = None
bot.restart_reason = None
bot.log_restart_msg = True

def loadcogs(folder):
    for cog in os.listdir(f"./cogs/{folder}"):
        if cog.endswith(".py"):
            try:
                cog = f"cogs.{folder}.{cog.replace('.py','')}"
                bot.load_extension(cog)
            except Exception as e:
                print(f"{cog} cannot be loaded")
                raise e

loadcogs("Info")
print("Info Loaded!")

loadcogs("Music")
print("Music Loaded!")

loadcogs("Owner")
print("Owner Loaded!")

loadcogs("Utility")
print("Utility Loaded!")

bot.run(bot_token)