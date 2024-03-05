import discord
from discord.ext import commands
import datetime
from botprefix import prefix

class seek(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @commands.command()
    async def seek(self, ctx, position : str = None):

        async def seekFunc():
            var = {'seek': True, 'send_play_embed': False, 'seek_position': str(positionInSec)}
            self.bot.voice_client_attributes[str(ctx.guild.id)].update(var)
            ctx.voice_client.stop()
            positionInString =  datetime.timedelta(seconds=positionInSec)

            embed4 = discord.Embed(title=f"Seeked To Position - `{positionInString}`",colour=0x0000ff)
            await ctx.send(embed=embed4)
            await ctx.message.add_reaction("✅")
            return

        if position is None:
            embed = discord.Embed(title=f"This Command Is Used Like This: `{prefix(self.bot, ctx)[0]}seek [position]`", colour=0xff0000)
            await ctx.send(embed=embed)
            return

        try:
            if ctx.author.voice is not None:
                if ctx.voice_client is not None:
                    if ctx.author.voice is not None and ctx.author.voice.channel == ctx.voice_client.channel:
                        if ctx.voice_client.is_playing():
                            if ":" in position:
                                positionInSec = sum(x * int(t) for x, t in zip([1, 60, 3600], reversed(position.split(":"))))
                            else:
                                positionInSec = int(position)
                            checkQueue = list(
                                self.bot.music[str(ctx.guild.id)])[0]
                            time = self.bot.music[str(
                                ctx.guild.id)][str(checkQueue)]['time']
                            if positionInSec < 0:
                                embed2 = discord.Embed(title=f"Invalid Position!", colour=0xff0000)
                                await ctx.send(embed=embed2)
                                return

                            if positionInSec > int(time):
                                embed3 = discord.Embed(title=f"Invalid Position!", colour=0xff0000)
                                await ctx.send(embed=embed3)
                                return
                            if self.bot.voice_client_attributes[str(ctx.guild.id)]['radio'] is True:
                                embed = discord.Embed(title="Cannot Seek While Radio Is Playing!", colour=0xff0000)
                                await ctx.send(embed=embed)
                                return
                            else:
                                users = ctx.author.voice.channel.members
                                for member in ctx.author.voice.channel.members:
                                    if member.bot:
                                        users.remove(member)
                                if len(users) == 1:
                                    await seekFunc()
                                    return
                                else:
                                    if ctx.author.guild_permissions.administrator:
                                        await seekFunc()
                                        return
                                    else:
                                        if ctx.author.guild_permissions.manage_channels:
                                            await seekFunc()
                                            return
                                        else:
                                            for role in ctx.author.roles:
                                                if role.name == "DJ":
                                                    await seekFunc()
                                                    return
                                            else:
                                                embed2 = discord.Embed(description="**You Need `Administrator` Permission Or `DJ` Role Or `Manage Channels` Permission To Use This Command!** (Being Alone With The Bot Also Works.)",colour=0xff0000)
                                                await ctx.send(embed=embed2)
                                                return
                        else:
                            embed5 = discord.Embed(title="Player Is Not Playing!",colour=0xff0000)
                            await ctx.send(embed=embed5)
                            return
                    else:
                        embed6 = discord.Embed(title="You Must Be In The Same Voice Channel As The Bot To Use This Command!",colour=0xff0000)
                        await ctx.send(embed=embed6)
                        return
                else:
                    embed7 = discord.Embed(title="I'm Not Connected To A Voice Channel!",colour=0xff0000)
                    await ctx.send(embed=embed7)
                    return
            else:
                embed8 = discord.Embed(title="You Must Be In A Voice Channel To Use This Command!",colour=0xff0000)
                await ctx.send(embed=embed8)
                return
        except:
            embed9 = discord.Embed(title=f"Invalid Position!", colour=0xff0000)
            await ctx.send(embed=embed9)
            return
            

def setup(bot):
    bot.add_cog(seek(bot))