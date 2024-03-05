import discord
from discord.ext import commands

class loopqueue(commands.Cog):
    def __init__(self,bot):
        self.bot = bot


    @commands.command(aliases=['lq'])
    async def loopqueue(self, ctx):

        async def loopqueueFunc():
            if self.bot.voice_client_attributes[str(ctx.guild.id)]['loop_queue'] is False:
                var = {'loop_queue': True}
                self.bot.voice_client_attributes[str(ctx.guild.id)].update(var)
                embed = discord.Embed(title=":repeat: Loop Queue Enabled :repeat:",colour=0x0000ff)
                await ctx.send(embed=embed)
                await ctx.invoke(self.bot.get_command('updatemsg'))
                await ctx.message.add_reaction("✅")
                return
            else:
                var = {'loop_queue': False}
                self.bot.voice_client_attributes[str(ctx.guild.id)].update(var)
                embed2 = discord.Embed(title=":repeat: Loop Queue Disabled :repeat:",colour=0x0000ff)
                await ctx.send(embed=embed2)
                await ctx.invoke(self.bot.get_command('updatemsg'))
                await ctx.message.add_reaction("✅")
                return

        try:
            if ctx.author.voice is not None:
                if ctx.voice_client is not None:
                    if ctx.author.voice is not None and ctx.author.voice.channel == ctx.voice_client.channel:
                        if self.bot.voice_client_attributes[str(ctx.guild.id)]['radio'] is False:
                            users = ctx.author.voice.channel.members
                            for member in ctx.author.voice.channel.members:
                                if member.bot:
                                    users.remove(member)
                            if len(users) == 1:
                                await loopqueueFunc()
                            else:
                                if ctx.author.guild_permissions.administrator:
                                    await loopqueueFunc()
                                else:
                                    if ctx.author.guild_permissions.manage_channels:
                                        await loopqueueFunc()
                                    else:
                                        for role in ctx.author.roles:
                                            if role.name == "DJ":
                                                await loopqueueFunc()
                                                return
                                        else:
                                            embed2 = discord.Embed(description="**You Need `Administrator` Permission Or `DJ` Role Or `Manage Channels` Permission To Use This Command!** (Being Alone With The Bot Also Works.)",colour=0xff0000)
                                            await ctx.send(embed=embed2)
                                            return
                        else: 
                            embed = discord.Embed(title="Cannot Loop Queue While Radio Is Playing!", colour=0xff0000)
                            await ctx.send(embed=embed)
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
    bot.add_cog(loopqueue(bot))