import discord
from discord.ext import commands
from botprefix import prefix

class setstatus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    @commands.is_owner()
    async def setstatus(self, ctx, actType : str =  None, *, name : str = None):
        try:
            if actType is None:
                embed = discord.Embed(title=f"This Command Is Used Like This:  `{prefix(self.bot, ctx)[0]}setstatus [type] [name]`", colour=0xff0000)
                await ctx.send(embed=embed)
                return

            if name is None:
                embed2 = discord.Embed(title=f"Please Enter Activity Name!", colour=0xff0000)
                await ctx.send(embed=embed2)
                return

            if actType.lower() == "playing":
                newType = discord.ActivityType.playing
            elif actType.lower() == "listening":
                newType = discord.ActivityType.listening
            elif actType.lower() == "watching":
                newType = discord.ActivityType.watching
            elif actType.lower() == "streaming":
                newType = discord.ActivityType.streaming

            await self.bot.change_presence(activity=discord.Activity(type=newType, name=name))

            embed3 = discord.Embed(title=f"Bot Status Changed To **`{actType} {name}`**!", colour=0x00ff00)
            await ctx.send(embed=embed3)
            return

        except:
            embed4 = discord.Embed(title=f"Invalid Activity Type!", colour=0xff0000)
            await ctx.send(embed=embed4)
            return



def setup(bot):
    bot.add_cog(setstatus(bot))