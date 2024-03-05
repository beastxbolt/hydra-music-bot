import discord
from discord.ext import commands
import random

class shuffle(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    
    @commands.command()
    async def shuffle(self, ctx):

        async def shuffleFunc():
            new_dict = self.bot.music[str(ctx.guild.id)].copy()
            first_index = list(new_dict.keys())[0]
            popped = new_dict.pop(first_index)

            temp = list(new_dict.items())
            random.shuffle(temp)

            shuffled_dict = {}
            shuffled_dict[first_index] = popped
            shuffled_dict.update(dict(temp))
            self.bot.music.pop(str(ctx.guild.id), None)
            self.bot.music[str(ctx.guild.id)] = {}
            self.bot.music[str(ctx.guild.id)].update(shuffled_dict)

            embed = discord.Embed(title="Shuffled!",colour=0x0000ff)
            await ctx.send(embed=embed)
            await ctx.invoke(self.bot.get_command('updatemsg'))
            await ctx.message.add_reaction("✅")
            return

        try:
            if ctx.author.voice is not None:
                if ctx.voice_client is not None:
                    if ctx.author.voice is not None and ctx.author.voice.channel == ctx.voice_client.channel:
                        if ctx.voice_client.is_playing() or ctx.voice_client.is_playing() and ctx.voice_client.is_paused() is False or ctx.voice_client.is_playing() and ctx.voice_client.is_paused():
                            if self.bot.voice_client_attributes[str(ctx.guild.id)]['block_skip_and_stop'] is False:
                                if self.bot.voice_client_attributes[str(ctx.guild.id)]['radio'] is False:
                                    users = ctx.author.voice.channel.members
                                    for member in ctx.author.voice.channel.members:
                                        if member.bot:
                                            users.remove(member)
                                    if len(users) == 1:
                                        await shuffleFunc()
                                        return
                                    else:
                                        if ctx.author.guild_permissions.administrator:
                                            await shuffleFunc()
                                            return
                                        else:
                                            if ctx.author.guild_permissions.manage_channels:
                                                await shuffleFunc()
                                                return
                                            else:
                                                for role in ctx.author.roles:
                                                    if role.name == "DJ":
                                                        await shuffleFunc()
                                                        return
                                                else:
                                                    embed2 = discord.Embed(description="**You Need `Administrator` Permission Or `DJ` Role Or `Manage Channels` Permission To Use This Command!** (Being Alone With The Bot Also Works.)",colour=0xff0000)
                                                    await ctx.send(embed=embed2)
                                                    return
                                else: 
                                    embed = discord.Embed(title="Cannot Shuffle Queue While Radio Is Playing!", colour=0xff0000)
                                    await ctx.send(embed=embed)
                                    return
                            else:
                                embed3 = discord.Embed(title="Cannot Shuffle While Adding Playlist In Queue!",colour=0xff0000)
                                await ctx.send(embed=embed3)
                                return
                        else:
                            embed4 = discord.Embed(title="Player Is Not Playing!",colour=0xff0000)
                            await ctx.send(embed=embed4)
                            return
                    else:
                        embed5 = discord.Embed(title="You Must Be In The Same Voice Channel As The Bot To Use This Command!",colour=0xff0000)
                        await ctx.send(embed=embed5)
                        return
                else:
                    embed6 = discord.Embed(title="I'm Not Connected To A Voice Channel!",colour=0xff0000)
                    await ctx.send(embed=embed6)
                    return
            else:
                embed8 = discord.Embed(title="You Must Be In A Voice Channel To Use This Command!",colour=0xff0000)
                await ctx.send(embed=embed8)
                return
        except Exception as e:
            print(e)
        

def setup(bot):
    bot.add_cog(shuffle(bot))