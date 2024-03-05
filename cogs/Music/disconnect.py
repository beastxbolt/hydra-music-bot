import discord
from discord.ext import commands

class disconnect(commands.Cog):
    def __init__(self,bot):
        self.bot = bot


    @commands.command(aliases=['dc'])
    async def disconnect(self,ctx):

        async def disconnectClient():
            embed = discord.Embed(title="Successfully Disconnected!",colour=0x00ff00)
            self.bot.music.pop(str(ctx.guild.id), None)
            self.bot.voice_client_attributes.pop(str(ctx.guild.id), None)
            if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
                ctx.voice_client.stop()
            await ctx.voice_client.disconnect()
            await ctx.send(embed=embed)
            await ctx.message.add_reaction("✅")
            return

        try:
            if ctx.author.voice is not None:
                if ctx.voice_client is not None:
                    if ctx.author.voice is not None and ctx.author.voice.channel == ctx.voice_client.channel:
                        users = ctx.author.voice.channel.members
                        for member in ctx.author.voice.channel.members:
                            if member.bot:
                                users.remove(member)
                        if len(users) == 1:
                            await disconnectClient()
                            return
                        else:
                            if ctx.author.guild_permissions.administrator:
                                await disconnectClient()
                                return
                            else:
                                if ctx.author.guild_permissions.manage_channels:
                                    await disconnectClient()
                                    return
                                else:
                                    for role in ctx.author.roles:
                                        if role.name == "DJ":
                                            await disconnectClient()
                                            return
                                    else:
                                        embed2 = discord.Embed(description="**You Need `Administrator` Permission Or `DJ` Role Or `Manage Channels` Permission To Use This Command!** (Being Alone With The Bot Also Works.)",colour=0xff0000)
                                        await ctx.send(embed=embed2)
                                        return
                    else: 
                        embed3 = discord.Embed(title="You Must Be In The Same Voice Channel As The Bot To Use This Command!", colour=0xff0000)
                        await ctx.send(embed=embed3)
                        return
                else:
                    embed4 = discord.Embed(title="I'm Not Connected To A Voice Channel!",colour=0xff0000)
                    await ctx.send(embed=embed4)
                    return
            else:
                embed5 = discord.Embed(title="You Must Be In A Voice Channel To Use This Command!",colour=0xff0000)
                await ctx.send(embed=embed5)
                return
        except Exception as e:
            print(e)
        

def setup(bot):
    bot.add_cog(disconnect(bot))