import discord
from discord.ext import commands
import json
from botprefix import prefix
from config import splashart_url

class musicsetup(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @commands.command()
    @commands.bot_has_guild_permissions(manage_channels=True)
    async def setup(self, ctx):
        play_emoji = '\U000025B6'
        pause_emoji = '\U000023F8'
        stop_emoji = '\U000023F9'
        skip_emoji = '\U000023ED'
        shuffle_emoji = '\U0001F500'
        loop_emoji = '\U0001F504'
        loop_queue_emoji = '\U0000267E'
        disconnect_emoji = '\U0000274C'
            
        try:
            with open('./config.json', 'r+') as file:
                data = json.load(file)

                try:
                    channel_id = data["music"][str(ctx.guild.id)]["channel_id"]
                except KeyError:
                    try:
                        checkGuildID = data["music"][str(ctx.guild.id)]
                    except KeyError:
                        var = {str(ctx.guild.id): {}}
                        data["music"].update(var)
                        file.seek(0)
                        json.dump(data, file, indent=4)

                    try:
                        checkChannelID = data['music'][str(ctx.guild.id)]['channel_id']
                    except KeyError:
                        new_channel = await ctx.guild.create_text_channel("bot-song-requests")
                        await new_channel.edit(topic=":arrow_forward: Play the music.\n:pause_button: Pause the music.\n:stop_button: Stop and empty the queue.\n:track_next: Skip the song.\n:twisted_rightwards_arrows: Shuffle the queue.\n:arrows_counterclockwise: Loop the current playing music.\n:infinity: Loop the whole queue.\n:x: Disconnect the bot.")
                        var = {"channel_id": new_channel.id}
                        data["music"][str(ctx.guild.id)].update(var)
                        file.seek(0)
                        json.dump(data, file, indent=4)

                        try:
                            if ctx.voice_client.is_playing() or ctx.voice_client.is_playing() is False and ctx.voice_client.is_paused():
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
                                embed.set_footer(text=f"{i} {text} in queue | Loop: {loopStatus} | Loop Queue: {loopqueueStatus} | Radio: {radioStatus}")

                                queue = f"**__Queue list:__**\n{complete_list}"
                                msg = await new_channel.send(content=queue, embed=embed)
                                var = {"message_id": msg.id}
                                data["music"][str(ctx.guild.id)].update(var)
                                file.seek(0)
                                json.dump(data, file, indent=4)

                                await msg.add_reaction(play_emoji)
                                await msg.add_reaction(pause_emoji)
                                await msg.add_reaction(stop_emoji)
                                await msg.add_reaction(skip_emoji)
                                await msg.add_reaction(shuffle_emoji)
                                await msg.add_reaction(loop_emoji)
                                await msg.add_reaction(loop_queue_emoji)
                                await msg.add_reaction(disconnect_emoji)

                                embed = discord.Embed(description=f"**Song Request Channel Has Been Created!**\n**Channel:** {new_channel.mention}\n_You Can Rename And Move This Channel If You Want To._", color=0x00ff00)
                                await ctx.send(embed=embed)
                                await ctx.message.add_reaction("✅")
                                return
                        except:
                            pass

                        embed = discord.Embed(title="No music playing currently", color=0x0098ff)
                        embed.set_image(url=splashart_url)
                        embed.set_footer(text=f"Prefix for this server is: {prefix(self.bot, ctx)[0]}")

                        msg = await new_channel.send("**__Queue list:__**\nJoin a voice channel and queue songs by name or url in here.", embed=embed)
                        var = {"message_id": msg.id}
                        data["music"][str(ctx.guild.id)].update(var)
                        file.seek(0)
                        json.dump(data, file, indent=4)

                        await msg.add_reaction(play_emoji)
                        await msg.add_reaction(pause_emoji)
                        await msg.add_reaction(stop_emoji)
                        await msg.add_reaction(skip_emoji)
                        await msg.add_reaction(shuffle_emoji)
                        await msg.add_reaction(loop_emoji)
                        await msg.add_reaction(loop_queue_emoji)
                        await msg.add_reaction(disconnect_emoji)

                        embed = discord.Embed(description=f"**Song Request Channel Has Been Created!**\n**Channel:** {new_channel.mention}\n_You Can Rename And Move This Channel If You Want To._", color=0x00ff00)
                        await ctx.send(embed=embed)
                        await ctx.message.add_reaction("✅")
                        return

                channel = self.bot.get_channel(channel_id)
                if channel is None:
                    new_channel = await ctx.guild.create_text_channel("bot-song-requests")
                    await new_channel.edit(topic=":arrow_forward: Play the music.\n:pause_button: Pause the music.\n:stop_button: Stop and empty the queue.\n:track_next: Skip the song.\n:twisted_rightwards_arrows: Shuffle the queue.\n:arrows_counterclockwise: Loop the current playing music.\n:infinity: Loop the whole queue.\n:x: Disconnect the bot.")
                    var = {"channel_id": new_channel.id}
                    data["music"][str(ctx.guild.id)].update(var)
                    file.seek(0)
                    json.dump(data, file, indent=4)

                    try:
                        if ctx.voice_client.is_playing() or ctx.voice_client.is_playing() is False and ctx.voice_client.is_paused():
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
                            embed.set_footer(text=f"{i} {text} in queue | Loop: {loopStatus} | Loop Queue: {loopqueueStatus} | Radio: {radioStatus}")

                            queue = f"**__Queue list:__**\n{complete_list}"
                            msg = await new_channel.send(content=queue, embed=embed)
                            var = {"message_id": msg.id}
                            data["music"][str(ctx.guild.id)].update(var)
                            file.seek(0)
                            json.dump(data, file, indent=4)

                            await msg.add_reaction(play_emoji)
                            await msg.add_reaction(pause_emoji)
                            await msg.add_reaction(stop_emoji)
                            await msg.add_reaction(skip_emoji)
                            await msg.add_reaction(shuffle_emoji)
                            await msg.add_reaction(loop_emoji)
                            await msg.add_reaction(loop_queue_emoji)
                            await msg.add_reaction(disconnect_emoji)

                            embed = discord.Embed(description=f"**Song Request Channel Has Been Created!**\n**Channel:** {new_channel.mention}\n_You Can Rename And Move This Channel If You Want To._", color=0x00ff00)
                            await ctx.send(embed=embed)
                            await ctx.message.add_reaction("✅")
                            return
                    except:
                        pass

                    embed = discord.Embed(title="No music playing currently", color=0x0098ff)
                    embed.set_image(url=splashart_url)
                    embed.set_footer(text=f"Prefix for this server is: {prefix(self.bot, ctx)[0]}")

                    msg = await new_channel.send("**__Queue list:__**\nJoin a voice channel and queue songs by name or url in here.", embed=embed)
                    var = {"message_id": msg.id}
                    data["music"][str(ctx.guild.id)].update(var)
                    file.seek(0)
                    json.dump(data, file, indent=4)

                    await msg.add_reaction(play_emoji)
                    await msg.add_reaction(pause_emoji)
                    await msg.add_reaction(stop_emoji)
                    await msg.add_reaction(skip_emoji)
                    await msg.add_reaction(shuffle_emoji)
                    await msg.add_reaction(loop_emoji)
                    await msg.add_reaction(loop_queue_emoji)
                    await msg.add_reaction(disconnect_emoji)

                    embed = discord.Embed(description=f"**Song Request Channel Has Been Created!**\n**Channel:** {new_channel.mention}\n_You Can Rename And Move This Channel If You Want To._", color=0x00ff00)
                    await ctx.send(embed=embed)
                    await ctx.message.add_reaction("✅")
                    return
                else:
                    try:
                        await channel.fetch_message(data['music'][str(ctx.guild.id)]['message_id'])
                        embed = discord.Embed(description=f"Already setup in {channel.mention}", color=0xff0000)
                        await ctx.send(embed=embed)
                        await ctx.message.add_reaction("✅")
                        return
                    except discord.NotFound:
                        new_channel = await ctx.guild.create_text_channel("bot-song-requests")
                        await new_channel.edit(topic=":arrow_forward: Play the music.\n:pause_button: Pause the music.\n:stop_button: Stop and empty the queue.\n:track_next: Skip the song.\n:twisted_rightwards_arrows: Shuffle the queue.\n:arrows_counterclockwise: Loop the current playing music.\n:infinity: Loop the whole queue.\n:x: Disconnect the bot.")
                        var = {"channel_id": new_channel.id}
                        data["music"][str(ctx.guild.id)].update(var)
                        file.seek(0)
                        json.dump(data, file, indent=4)

                        try:
                            if ctx.voice_client.is_playing() or ctx.voice_client.is_playing() is False and ctx.voice_client.is_paused():
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
                                embed.set_footer(text=f"{i} {text} in queue | Loop: {loopStatus} | Loop Queue: {loopqueueStatus} | Radio: {radioStatus}")

                                queue = f"**__Queue list:__**\n{complete_list}"
                                msg = await ctx.send(content=queue, embed=embed)
                                var = {"message_id": msg.id}
                                data["music"][str(ctx.guild.id)].update(var)
                                file.seek(0)
                                json.dump(data, file, indent=4)

                                await msg.add_reaction(play_emoji)
                                await msg.add_reaction(pause_emoji)
                                await msg.add_reaction(stop_emoji)
                                await msg.add_reaction(skip_emoji)
                                await msg.add_reaction(shuffle_emoji)
                                await msg.add_reaction(loop_emoji)
                                await msg.add_reaction(loop_queue_emoji)
                                await msg.add_reaction(disconnect_emoji)

                                embed = discord.Embed(description=f"**Song Request Channel Has Been Created!**\n**Channel:** {new_channel.mention}\n_You Can Rename And Move This Channel If You Want To._", color=0x00ff00)
                                await ctx.send(embed=embed)
                                await ctx.message.add_reaction("✅")
                                return
                        except:
                            pass

                        embed = discord.Embed(title="No music playing currently", color=0x0098ff)
                        embed.set_image(url=splashart_url)
                        embed.set_footer(text=f"Prefix for this server is: {prefix(self.bot, ctx)[0]}")

                        msg = await new_channel.send("**__Queue list:__**\nJoin a voice channel and queue songs by name or url in here.", embed=embed)
                        var = {"message_id": msg.id}
                        data["music"][str(ctx.guild.id)].update(var)
                        file.seek(0)
                        json.dump(data, file, indent=4)

                        await msg.add_reaction(play_emoji)
                        await msg.add_reaction(pause_emoji)
                        await msg.add_reaction(stop_emoji)
                        await msg.add_reaction(skip_emoji)
                        await msg.add_reaction(shuffle_emoji)
                        await msg.add_reaction(loop_emoji)
                        await msg.add_reaction(loop_queue_emoji)
                        await msg.add_reaction(disconnect_emoji)

                        embed = discord.Embed(description=f"**Song Request Channel Has Been Created!**\n**Channel:** {new_channel.mention}\n_You Can Rename And Move This Channel If You Want To._", color=0x00ff00)
                        await ctx.send(embed=embed)
                        await ctx.message.add_reaction("✅")
                        return
        except Exception as e:
            print(e)

        
def setup(bot):
    bot.add_cog(musicsetup(bot))