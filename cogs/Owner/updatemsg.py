import discord
from discord.ext import commands
from botprefix import prefix
import json
from config import splashart_url

class updatemsg(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    @commands.is_owner()
    async def updatemsg(self, ctx):
        with open('./config.json', 'r+') as file:
            data = json.load(file)

            try:
                channel_id = data['music'][str(ctx.guild.id)]['channel_id']
            except KeyError:
                return

            channel = self.bot.get_channel(channel_id)
            if channel is not None:
                try:
                    msg = await channel.fetch_message(data['music'][str(ctx.guild.id)]['message_id'])

                    try:
                        try:
                            checkQueue = list(
                                self.bot.music[str(ctx.guild.id)])[0]
                            title = self.bot.music[str(
                                ctx.guild.id)][str(checkQueue)]['title']
                            duration = self.bot.music[str(
                                ctx.guild.id)][str(checkQueue)]['duration']
                            thumbnail = self.bot.music[str(
                                ctx.guild.id)][str(checkQueue)]['thumbnail']

                            musicList = list(self.bot.music[str(ctx.guild.id)])
                            i = 0
                            skipFirst = 0
                            complete_list = ""
                            char_limit = False
                            extra_songs = 0
                            for music in musicList:
                                if skipFirst == 0:
                                    skipFirst += 1
                                else:
                                    title = self.bot.music[str(
                                        ctx.guild.id)][str(music)]['title']
                                    url = self.bot.music[str(
                                        ctx.guild.id)][str(music)]['url']
                                    duration = self.bot.music[str(
                                        ctx.guild.id)][str(music)]['duration']
                                    requester = self.bot.music[str(
                                        ctx.guild.id)][str(music)]['requester']

                                    if len(complete_list + f"{i + 1}. {title}" + f" [{duration}] - {ctx.guild.get_member_named(requester).mention}\n") > 1900:
                                        i = i + 1
                                        char_limit = True
                                        extra_songs += 1
                                        continue
                                    else:
                                        complete_list = complete_list + f"{i + 1}. {title}" + f" [{duration}] - {ctx.guild.get_member_named(requester).mention}\n"
                                        i = i + 1
                            
                            if char_limit is True:
                                complete_list += f"**And {extra_songs} More...**"

                            loopStatus = ""
                            if self.bot.voice_client_attributes[str(ctx.guild.id)]['loop'] is True:
                                loopStatus = loopStatus + "✅"
                            else:
                                loopStatus = loopStatus + "❌"

                            loopqueueStatus = ""
                            if self.bot.voice_client_attributes[str(ctx.guild.id)]['loop_queue'] is True:
                                loopqueueStatus = loopqueueStatus + "✅"
                            else:
                                loopqueueStatus = loopqueueStatus + "❌"
                                
                            radioStatus = ""
                            if self.bot.voice_client_attributes[str(ctx.guild.id)]['radio'] is True:
                                radioStatus = radioStatus + "✅"
                            else:
                                radioStatus = radioStatus + "❌"   

                            try:
                                playerStatus = ""
                                if ctx.voice_client.is_paused():
                                    playerStatus = playerStatus + " | Paused ⏸️"
                            except:
                                return

                            text = ""
                            if i <= 1:
                                text += "music"
                            if i > 1:
                                text += "musics"

                            checkQueue = list(
                                self.bot.music[str(ctx.guild.id)])[0]
                            title = self.bot.music[str(
                                ctx.guild.id)][str(checkQueue)]['title']
                            url = self.bot.music[str(
                                ctx.guild.id)][str(checkQueue)]['url']
                            duration = self.bot.music[str(
                                ctx.guild.id)][str(checkQueue)]['duration']
                            thumbnail = self.bot.music[str(
                                ctx.guild.id)][str(checkQueue)]['thumbnail']
                            requester = self.bot.music[str(
                                ctx.guild.id)][str(checkQueue)]['requester']
                            
                            embed = discord.Embed(description=f"**[{duration}] - [{title}]({url})**\nRequested by {ctx.guild.get_member_named(requester).mention}", color=0x0098ff)
                            embed.set_image(url=thumbnail)
                            embed.set_footer(text=f"{i} {text} in queue | Loop: {loopStatus} | Loop Queue: {loopqueueStatus} | Radio: {radioStatus}{playerStatus}")

                            queue = f"**__Queue list:__**\n{complete_list}"
                            await msg.edit(content=queue, embed=embed)
                            return
                        except IndexError:
                            embed = discord.Embed(title="No music playing currently", color=0x0098ff)
                            embed.set_image(url=splashart_url)
                            embed.set_footer(text=f"Prefix for this server is: {prefix(self.bot, ctx)[0]}")
                            content = "**__Queue list:__**\nJoin a voice channel and queue songs by name or url in here."
                            await msg.edit(content=content, embed=embed)
                            return
                            
                    except KeyError:
                        embed = discord.Embed(title="No music playing currently", color=0x0098ff)
                        embed.set_image(url=splashart_url)
                        embed.set_footer(text=f"Prefix for this server is: {prefix(self.bot, ctx)[0]}")
                        content = "**__Queue list:__**\nJoin a voice channel and queue songs by name or url in here."
                        await msg.edit(content=content, embed=embed)
                        return
                
                except discord.NotFound:
                    return
            else:
                return

def setup(bot):
    bot.add_cog(updatemsg(bot))