import discord
from discord.ext import commands
from botprefix import prefix

class volume(commands.Cog):
    def __init__(self,bot):
        self.bot = bot


    @commands.command(aliases=['vol'])
    async def volume(self, ctx, newVol : int = None):

        async def volumeFunc():
            ctx.voice_client.source.volume = newVol / 100
            var = {'volume': newVol}
            self.bot.voice_client_attributes[str(ctx.guild.id)].update(var)
            embed5 = discord.Embed(title=f":loud_sound: Volume Changed To {newVol} :loud_sound:",colour=0x0067ff)
            await ctx.send(embed=embed5)
            await ctx.message.add_reaction("✅")
            return

        if newVol is None:
            embed = discord.Embed(title=f"This Command Is Used Like This: `{prefix(self.bot, ctx)[0]}volume [new volume]`",colour=0xff0000)
            await ctx.send(embed=embed)
            return

        if not isinstance(newVol, int):
            embed2 = discord.Embed(title="Enter A Valid Number!",colour=0xff0000)
            await ctx.send(embed=embed2)
            return

        if newVol <= 0:
            embed3 = discord.Embed(title="Enter A Valid Number!",colour=0xff0000)
            await ctx.send(embed=embed3)
            return

        if newVol > 100:
            embed4 = discord.Embed(title="Enter Number Between 0 and 100!",colour=0xff0000)
            await ctx.send(embed=embed4)
            return

        try:
            if ctx.author.voice is not None:
                if ctx.voice_client is not None:
                    if ctx.author.voice is not None and ctx.author.voice.channel == ctx.voice_client.channel:
                        if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
                            users = ctx.author.voice.channel.members
                            for member in ctx.author.voice.channel.members:
                                if member.bot:
                                    users.remove(member)
                            if len(users) == 1:
                                await volumeFunc()
                                return
                            else:
                                if ctx.author.guild_permissions.administrator:
                                    await volumeFunc()
                                    return
                                else:
                                    if ctx.author.guild_permissions.manage_channels:
                                        await volumeFunc()
                                        return
                                    else:
                                        for role in ctx.author.roles:
                                            if role.name == "DJ":
                                                await volumeFunc()
                                                return
                                        else:
                                            embed2 = discord.Embed(description="**You Need `Administrator` Permission Or `DJ` Role Or `Manage Channels` Permission To Use This Command!** (Being Alone With The Bot Also Works.)",colour=0xff0000)
                                            await ctx.send(embed=embed2)
                                            return
                        else:
                            embed6 = discord.Embed(title="Player Is Not Playing!",colour=0xff0000)
                            await ctx.send(embed=embed6)
                            return
                    else:
                        embed7 = discord.Embed(title="You Must Be In The Same Voice Channel As The Bot To Use This Command!",colour=0xff0000)
                        await ctx.send(embed=embed7)
                        return
                else:
                    embed8 = discord.Embed(title="I'm Not Connected To A Voice Channel!",colour=0xff0000)
                    await ctx.send(embed=embed8)
                    return
            else:
                embed9 = discord.Embed(title="You Must Be In A Voice Channel To Use This Command!",colour=0xff0000)
                await ctx.send(embed=embed9)
                return
        except Exception as e:
            print(e)
        

def setup(bot):
    bot.add_cog(volume(bot))