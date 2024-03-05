import discord
from discord.ext import commands
import asyncio

class join(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    
    @commands.command()
    async def join(self, ctx):

        def invokeCheckVC():
            coroutine = ctx.invoke(self.bot.get_command('checkvc'))
            asyncio.run_coroutine_threadsafe(
                coroutine, self.bot.loop)
            return

        try:
            if ctx.author.voice is not None:
                vc = ctx.author.voice.channel

                if not ctx.voice_client or not ctx.voice_client.is_connected():
                    user = await ctx.guild.fetch_member(self.bot.user.id)
                    if user.permissions_in(ctx.author.voice.channel).connect is False:
                        embed = discord.Embed(title="Bot requires Connect permission(s) to run this command.", colour=0xff0000)
                        await ctx.channel.send(embed=embed)
                        return
                        
                    self.bot.music.pop(str(ctx.guild.id), None)
                    self.bot.voice_client_attributes.pop(str(ctx.guild.id), None)
                    await vc.connect()

                    attr = {"radio": False,
                            "loop": False,
                            "loop_queue": False,
                            "move_queue_to_last": False,
                            "seek": False,
                            "block_skip_and_stop": False,
                            "send_play_embed": True,
                            "seek_position": "0",
                            "volume": 100}

                    value = self.bot.voice_client_attributes.get(str(ctx.guild.id))
                    if value is None:
                        self.bot.voice_client_attributes[str(ctx.guild.id)] = attr
                    else:
                        pass
                    
                    embed = discord.Embed(title=f"✅ Connected To `{vc.name}` ✅",colour=0xFF69B4)
                    await ctx.send(embed=embed)
                    await ctx.message.add_reaction("✅")
                    invokeCheckVC()
                    return

                else:
                    embed2 = discord.Embed(title="The Bot Is Already In A Voice Channel!",colour=0xff0000)
                    await ctx.send(embed=embed2)
                    return
            else:
                embed3 = discord.Embed(title="You Must Be In A Voice Channel To Use This Command!",colour=0xff0000)
                await ctx.send(embed=embed3)
                return
        except Exception as e:
            print(e)
        

def setup(bot):
    bot.add_cog(join(bot))