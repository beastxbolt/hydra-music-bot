import discord
import asyncio
from discord.ext import commands

class checkvc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    @commands.is_owner()
    async def checkvc(self, ctx):
        try:
            await asyncio.sleep(120)
            if ctx.guild.voice_client.is_playing() or ctx.guild.voice_client.is_playing() is False and ctx.guild.voice_client.is_paused():
                return
            else:
                if ctx.voice_client.is_connected():
                    await ctx.voice_client.disconnect()
                    return
                else:
                    return
        except:
            return
        

def setup(bot):
    bot.add_cog(checkvc(bot))