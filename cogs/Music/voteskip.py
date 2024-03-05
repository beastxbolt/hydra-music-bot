import discord
from discord.ext import commands
from asyncio import TimeoutError
import math

class voteskip(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    
    @commands.command(aliases=['vs'])
    async def voteskip(self, ctx):
        
        tick = '\U00002705'
        cross = '\U0000274C'
        box = '\U0001F5F3'

        usersVoted = []
        usersVotedYes = []
        usersVotedNo = []
        numberOfYesVotes = 0
        numberOfNoVotes = 0
            
        async def votePassed(msg, yesVotes, requiredYesVotes):
            embed = discord.Embed(title=f"{tick} Vote Passed! Skipping...", description=f"**{yesVotes}/{requiredYesVotes}** Voted YES", colour=0x00ff00)
            await msg.clear_reactions()
            await msg.edit(embed=embed)
            await ctx.message.add_reaction("✅")
            return

        async def voteFailed(msg, noVotes, requiredYesVotes):
            embed2 = discord.Embed(title=f"{cross} Vote Failed!", description=f"**{noVotes}/{requiredYesVotes}** Voted NO", colour=0xff0000)
            await msg.clear_reactions()
            await msg.edit(embed=embed2)
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
                                        votePassedEmbed = discord.Embed(title=f"{tick} Vote Passed! Skipping...", colour=0x00ff00)
                                        await ctx.send(embed=votePassedEmbed)
                                        ctx.voice_client.stop()
                                        return


                                    if len(users) == 2:
                                        embed3 = discord.Embed(title=f"{box} Vote By: {ctx.author} {box}", description = f"**Skip Current Music?\n{numberOfYesVotes}/2 Votes\n\nTotal Votes: {len(users)}**", colour=0x0000ff)
                                        embed3.set_footer(text=f"{numberOfNoVotes} Users Voted No")
                                        msg = await ctx.send(embed=embed3)
                                        await msg.add_reaction(emoji = tick)
                                        await msg.add_reaction(emoji = cross)
                                        
                                        def check(reaction, user):
                                            return not user.bot and user in users
                                            
                                        try:
                                            while True:
                                                reaction, user = await self.bot.wait_for('reaction_add', timeout=120, check=check)

                                                if reaction.emoji == tick:
                                                    if user in users:
                                                        if user not in usersVoted:
                                                            if user in usersVotedYes:
                                                                pass
                                                            else:
                                                                numberOfYesVotes += 1
                                                                usersVotedYes.append(user)
                                                                usersVoted.append(user)

                                                                embed4 = discord.Embed(title=f"{box} Vote By: {ctx.author} {box}", description = f"**Skip Current Music?\n{numberOfYesVotes}/2 Votes\n\nTotal Votes: {len(users)}**", colour=0x0000ff)
                                                                embed4.set_footer(text=f"{numberOfNoVotes} Users Voted No")
                                                                await msg.edit(embed=embed4)
                                                                
                                                                if numberOfYesVotes == 2:
                                                                    await votePassed(msg, numberOfYesVotes, 2)
                                                                    ctx.voice_client.stop()
                                                                    return
                                                                else:
                                                                    pass
                                                        else:
                                                            pass
                                                    else:
                                                        pass

                                                elif reaction.emoji == cross:
                                                    if user in users:
                                                        if user not in usersVoted:
                                                            if user in usersVotedNo:
                                                                pass
                                                            else:
                                                                numberOfNoVotes += 1
                                                                usersVotedNo.append(user)
                                                                usersVoted.append(user)

                                                                embed5 = discord.Embed(title=f"{box} Vote By: {ctx.author} {box}", description = f"**Skip Current Music?\n{numberOfYesVotes}/2 Votes\n\nTotal Votes: {len(users)}**", colour=0x0000ff)
                                                                embed5.set_footer(text=f"{numberOfNoVotes} Users Voted No")
                                                                await msg.edit(embed=embed5)

                                                                if numberOfNoVotes == 1 or numberOfNoVotes == 2:
                                                                    await voteFailed(msg, numberOfNoVotes, len(users))
                                                                    return
                                                                else:
                                                                    pass
                                                        else:
                                                            pass
                                                    else:
                                                        pass           
                                        except TimeoutError:
                                            embed6 = discord.Embed(title=f"{cross} Vote Failed!", description=f"**Not Enough Votes!**", colour=0xff0000)
                                            await msg.clear_reactions()
                                            await msg.edit(embed=embed6)
                                            return


                                    if len(users) >= 3:
                                        numberOfRequiredYesVotes = math.floor(70 / 100 * len(users))
                                        numberOfRequiredNoVotes = math.ceil(30 / 100 * len(users)) + 1

                                        embed7 = discord.Embed(title=f"{box} Vote By: {ctx.author} {box}", description = f"**Skip Current Music?\n{numberOfYesVotes}/{numberOfRequiredYesVotes} Votes\n\nTotal Votes: {len(users)}**", colour=0x0000ff)
                                        embed7.set_footer(text=f"{numberOfNoVotes} Users Voted No")
                                        msg = await ctx.send(embed=embed7)
                                        await msg.add_reaction(emoji = tick)
                                        await msg.add_reaction(emoji = cross)
                                        
                                        def check2(reaction, user):
                                            return not user.bot and user in users
                                            
                                        try:
                                            while True:
                                                reaction, user = await self.bot.wait_for('reaction_add', timeout=120, check=check2)

                                                if reaction.emoji == tick:
                                                    if user in users:
                                                        if user not in usersVoted:
                                                            if user in usersVotedYes:
                                                                pass
                                                            else:
                                                                numberOfYesVotes += 1
                                                                usersVotedYes.append(user)
                                                                usersVoted.append(user)

                                                                embed8 = discord.Embed(title=f"{box} Vote By: {ctx.author} {box}", description = f"**Skip Current Music?\n{numberOfYesVotes}/{numberOfRequiredYesVotes} Votes\n\nTotal Votes: {len(users)}**", colour=0x0000ff)
                                                                embed8.set_footer(text=f"{numberOfNoVotes} Users Voted No")
                                                                await msg.edit(embed=embed8)
                                                                
                                                                if numberOfYesVotes == numberOfRequiredYesVotes:
                                                                    await votePassed(msg, numberOfYesVotes, numberOfRequiredYesVotes)
                                                                    ctx.voice_client.stop()
                                                                    return
                                                                else:
                                                                    pass
                                                        else:
                                                            pass
                                                    else:
                                                        pass

                                                elif reaction.emoji == cross:
                                                    if user in users:
                                                        if user not in usersVoted:
                                                            if user in usersVotedNo:
                                                                pass
                                                            else:
                                                                numberOfNoVotes += 1
                                                                usersVotedNo.append(user)
                                                                usersVoted.append(user)

                                                                embed9 = discord.Embed(title=f"{box} Vote By: {ctx.author} {box}", description = f"**Skip Current Music?\n{numberOfYesVotes}/2 Votes\n\nTotal Votes: {len(users)}**", colour=0x0000ff)
                                                                embed9.set_footer(text=f"{numberOfNoVotes} Users Voted No")
                                                                await msg.edit(embed=embed9)

                                                                if numberOfNoVotes == numberOfRequiredNoVotes:
                                                                    await voteFailed(msg, numberOfNoVotes, len(users))
                                                                    return
                                                                else:
                                                                    pass
                                                        else:
                                                            pass
                                                    else:
                                                        pass
                                                
                                        except TimeoutError:
                                            embed10 = discord.Embed(title=f"{cross} Vote Failed!", description=f"**Not Enough Votes!**", colour=0xff0000)
                                            await msg.clear_reactions()
                                            await msg.edit(embed=embed10)
                                            return
                                else: 
                                    embed = discord.Embed(title="Cannot Skip Music While Radio Is Playing!", colour=0xff0000)
                                    await ctx.send(embed=embed)
                                    return
                            else:
                                embed11 = discord.Embed(title="Cannot Skip While Adding Playlist In Queue!",colour=0xff0000)
                                await ctx.send(embed=embed11)
                                return
                        else:
                            embed12 = discord.Embed(title="Player Is Not Playing!",colour=0xff0000)
                            await ctx.send(embed=embed12)
                            return
                    else:
                        embed13 = discord.Embed(title="You Must Be In The Same Voice Channel As The Bot To Use This Command!",colour=0xff0000)
                        await ctx.send(embed=embed13)
                        return
                else:
                    embed14 = discord.Embed(title="I'm Not Connected To A Voice Channel!",colour=0xff0000)
                    await ctx.send(embed=embed14)
                    return
            else:
                embed15 = discord.Embed(title="You Must Be In A Voice Channel To Use This Command!",colour=0xff0000)
                await ctx.send(embed=embed15)
                return
        except Exception as e:
            print(e)
        

def setup(bot):
    bot.add_cog(voteskip(bot))