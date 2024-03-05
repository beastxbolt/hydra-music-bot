import discord
from discord.ext import commands
from botprefix import prefix


class remove(commands.Cog):
    def __init__(self,bot):
        self.bot = bot


    @commands.command()
    async def remove(self, ctx, index : int = None):

        async def removeFunc():
            try:
                title = list(self.bot.music[str(ctx.guild.id)])[index]
                embed2 = discord.Embed(description=f"**:white_check_mark: Removed -** {title}",colour=0x00ff00)
                await ctx.send(embed=embed2)
                self.bot.music[str(ctx.guild.id)].pop(title)
                await ctx.invoke(self.bot.get_command('updatemsg'))
                await ctx.message.add_reaction("✅")
                return
            except IndexError:
                embed3 = discord.Embed(title="The Song You Tried To Remove Does Not Exist!",colour=0xff0000)
                await ctx.send(embed=embed3)
                return

        if index is None:
            embed = discord.Embed(title=f"This Command Is Used Like This: `{prefix(self.bot, ctx)[0]}remove [position]`",colour=0xff0000)
            await ctx.send(embed=embed)
            return

        if index <= 0:
            embed = discord.Embed(title="The Song You Tried To Remove Does Not Exist!",colour=0xff0000)
            await ctx.send(embed=embed)
            return

        try:
            if ctx.author.voice is not None:
                if ctx.voice_client is not None:
                    if ctx.author.voice is not None and ctx.author.voice.channel == ctx.voice_client.channel:
                        if ctx.voice_client.is_playing() or ctx.voice_client.is_playing() is False and ctx.voice_client.is_paused():
                            users = ctx.author.voice.channel.members
                            for member in ctx.author.voice.channel.members:
                                if member.bot:
                                    users.remove(member)
                            if len(users) == 1:
                                await removeFunc()
                                return
                            else:
                                if ctx.author.guild_permissions.administrator:
                                    await removeFunc()
                                    return
                                else:
                                    if ctx.author.guild_permissions.manage_channels:
                                        await removeFunc()
                                        return
                                    else:
                                        for role in ctx.author.roles:
                                            if role.name == "DJ":
                                                await removeFunc()
                                                return
                                        else:
                                            embed2 = discord.Embed(description="**You Need `Administrator` Permission Or `DJ` Role Or `Manage Channels` Permission To Use This Command!** (Being Alone With The Bot Also Works.)",colour=0xff0000)
                                            await ctx.send(embed=embed2)
                                            return
                        else:
                            embed2 = discord.Embed(title="Player Is Not Playing!",colour=0xff0000)
                            await ctx.send(embed=embed2)
                            return
                    else: 
                        embed5 = discord.Embed(title="You Must Be In The Same Voice Channel As The Bot To Use This Command!",colour=0xff0000)
                        await ctx.send(embed=embed5)
                        return
                else:
                    embed4 = discord.Embed(title="I'm Not Connected To A Voice Channel!",colour=0xff0000)
                    await ctx.send(embed=embed4)
                    return
            else:
                embed6 = discord.Embed(title="You Must Be In A Voice Channel To Use This Command!",colour=0xff0000)
                await ctx.send(embed=embed6)
                return
        except Exception as e:
            print(e)
        

def setup(bot):
    bot.add_cog(remove(bot))