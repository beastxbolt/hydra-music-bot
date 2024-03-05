import discord
from discord.ext import commands
import asyncio
import time
import json
import datetime
import random
import youtube_dl
import googleapiclient.discovery
from urllib.parse import parse_qs, urlparse
from botprefix import prefix
from config import developer_key, splashart_url, spotify_client_id, spotify_client_secret
from spotipy import Spotify, SpotifyClientCredentials

i = 1

ytdl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    'usenetrc': True,
    'youtube_include_dash_manifest': False,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '384',
    }],
}

client_credentials_manager = SpotifyClientCredentials(
    client_id=spotify_client_id, client_secret=spotify_client_secret)
spotify = Spotify(
    client_credentials_manager=client_credentials_manager)

class events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def search(self, query):
        with youtube_dl.YoutubeDL(ytdl_opts) as ytdl:
            info = ytdl.extract_info(f'ytsearch:{query}', download=False)
            URL = info['entries'][0]['formats'][0]['url']

        yt_id = info['entries'][0]['id']
        yt_url = 'https://www.youtube.com/watch?v=' + yt_id
        title = info['entries'][0]['title']
        time = int(info['entries'][0]['duration'])
        duration = datetime.timedelta(seconds=time)
        thumbnail = info['entries'][0]['thumbnail']
        channel = info['entries'][0]['uploader']
        is_spotify = False
        return {'source': URL, 'title': title, 'duration': duration, 'time': time, 'url': yt_url, 'channel': channel, 'thumbnail': thumbnail, 'ytId': yt_id, 'is_spotify': is_spotify}

    def urlsearch(self, query):
        with youtube_dl.YoutubeDL(ytdl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            URL = info['formats'][0]['url']

        yt_id = info['id']
        yt_url = 'https://www.youtube.com/watch?v=' + yt_id
        title = info['title']
        time = int(info['duration'])
        duration = datetime.timedelta(seconds=time)
        thumbnail = info['thumbnail']
        channel = info['uploader']
        is_spotify = False
        return {'source': URL, 'title': title, 'duration': duration, 'time': time, 'url': yt_url, 'channel': channel, 'thumbnail': thumbnail, 'ytId': yt_id, 'is_spotify': is_spotify}

    def spotifysearch(self, query):
        track = spotify.track(query)

        all_artists = ""
        artists = track["artists"]
        for artist in artists:
            if artists.index(artist) == 0:
                all_artists += artist['name']

            if artists.index(artist) > 0:
                all_artists += f", {artist['name']}"

        title = track["name"]
        thumbnail = track["album"]["images"][0]["url"]
        url = track["external_urls"]["spotify"]

        with youtube_dl.YoutubeDL(ytdl_opts) as ytdl:
            info = ytdl.extract_info(
                f'ytsearch:{all_artists} - {title}', download=False)
            URL = info['entries'][0]['formats'][0]['url']
            time = int(info['entries'][0]['duration'])
            duration = datetime.timedelta(seconds=time)

        is_spotify = True
        return {'source': URL, 'title': title, 'duration': duration, 'time': time, 'url': url, 'channel': 'None', 'thumbnail': thumbnail, 'is_spotify': is_spotify}

    @commands.Cog.listener()
    async def on_ready(self):
        print("Bot Is Ready!")
            

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(description=f"**{error}**", colour=0xff0000)
            await ctx.send(embed=embed)
            return

        if isinstance(error, commands.BotMissingPermissions):
            embed = discord.Embed(description=f"**{error}**", colour=0xff0000)
            await ctx.send(embed=embed)
            return

        if isinstance(error, commands.CommandNotFound):
            return

        if isinstance(error, commands.NotOwner):
            embed = discord.Embed(
                title="This is a Owner-Only command!", colour=0xff0000)
            await ctx.send(embed=embed)
            return

        if isinstance(error, commands.BadArgument):
            embed4 = discord.Embed(
                title="Check Your Argument and Try Again!", colour=0xff0000)
            await ctx.send(embed=embed4)
            return

    @commands.Cog.listener()
    async def on_command(self, ctx):
        self.bot.recent_invokes[str(ctx.guild.id)] = ctx.channel.id

    @commands.Cog.listener()
    async def on_message(self, message):

        if str(message.channel.type) == "private":
            return

        if message.author.bot and message.author == self.bot.user and "Music Added To Queue." in message.content:
            return

        if message.author.bot and message.author == self.bot.user:
            await asyncio.sleep(10)
            pass

        if message.author.bot and message.author != self.bot.user:
            await asyncio.sleep(20)
            await message.delete()
            return

        with open('./config.json', 'r+') as file:
            data = json.load(file)

            try:
                channel_id = data['music'][str(message.guild.id)]['channel_id']
            except KeyError:
                return

            channel = self.bot.get_channel(channel_id)
            if channel is not None:
                if message.channel.id == channel.id:
                    try:
                        msg = await channel.fetch_message(data['music'][str(message.guild.id)]['message_id'])
                    except discord.NotFound:
                        if message.content.startswith(prefix(self.bot, message)[0]):
                            return
                        else:
                            var = {"channel_id": "null", "message_id": "null"}
                            data["music"][str(message.guild.id)].update(var)
                            file.seek(0)
                            json.dump(data, file, indent=4)

                            embed = discord.Embed(
                                title="Using normal mode again because the template message got deleted!", color=0xffa200)
                            await message.channel.send(embed=embed)

                            ctx = await self.bot.get_context(message)
                            await ctx.invoke(self.bot.get_command('play'), query=message.content)
                            return

                    try:
                        user = await message.guild.fetch_member(self.bot.user.id)

                        if message.content.startswith(prefix(self.bot, message)[0]) or message.author.bot:
                            if user.permissions_in(message.channel).manage_messages is False:
                                await asyncio.sleep(20)
                                if message.id != msg.id and message.author == self.bot.user:
                                    await message.delete()
                                    return
                                else:
                                    return
                            else:
                                await asyncio.sleep(20)
                                if message.id != msg.id:
                                    await message.delete()
                                    return
                                else:
                                    return

                        if user.permissions_in(message.channel).manage_messages is False:
                            embed = discord.Embed(
                                title="Bot requires Manage Messages permission(s) to run this command.", colour=0xff0000)
                            await message.channel.send(embed=embed)
                            return

                        await message.delete()
                    except:
                        pass

                    global i

                    def after(error):
                        try:
                            FFMPEG_OPTIONS = {"before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                                            "options": f"-vn -ss {self.bot.voice_client_attributes[str(message.guild.id)]['seek_position']}"}
                        except:
                            pass
                        try:
                            try:
                                if self.bot.voice_client_attributes[str(message.guild.id)]['seek'] is True:
                                    pass
                                else:
                                    try:
                                        if self.bot.voice_client_attributes[str(message.guild.id)]['loop'] is True and self.bot.voice_client_attributes[str(message.guild.id)]['loop_queue'] is True:
                                            pass
                                        if self.bot.voice_client_attributes[str(message.guild.id)]['loop'] is True and self.bot.voice_client_attributes[str(message.guild.id)]['loop_queue'] is False:
                                            pass
                                        if self.bot.voice_client_attributes[str(message.guild.id)]['loop'] is False and self.bot.voice_client_attributes[str(message.guild.id)]['loop_queue'] is False:
                                            firstIndex = list(
                                                self.bot.music[str(message.guild.id)].keys())[0]
                                            self.bot.music[str(message.guild.id)].pop(
                                                firstIndex)
                                        if self.bot.voice_client_attributes[str(message.guild.id)]['loop'] is False and self.bot.voice_client_attributes[str(message.guild.id)]['loop_queue'] is True:
                                            var = {'move_queue_to_last': True}
                                            self.bot.voice_client_attributes[str(message.guild.id)].update(var)
                                    except:
                                        pass
                            except:
                                pass
                            try:
                                try:
                                    if self.bot.voice_client_attributes[str(message.guild.id)]['move_queue_to_last'] is True:
                                        for key, value in self.bot.music[str(message.guild.id)].items():
                                            firstIndexKey = key
                                            break

                                        firstIndex = list(self.bot.music[str(message.guild.id)].keys())[0]
                                        poppedFirstIndexValue = self.bot.music[str(message.guild.id)].pop(firstIndex)
                                        self.bot.music[str(message.guild.id)][firstIndexKey] = poppedFirstIndexValue

                                        queueFirstIndex = list(
                                            self.bot.music[str(message.guild.id)])[0]
                                        checkQueue = self.bot.music[str(message.guild.id)][
                                            queueFirstIndex]["title"]
                                        requester = self.bot.music[str(message.guild.id)][str(
                                            queueFirstIndex)]['requester']

                                        var = {'move_queue_to_last': False}
                                        self.bot.voice_client_attributes[str(message.guild.id)].update(var)
                                            
                                    else:
                                        queueFirstIndex = list(
                                            self.bot.music[str(message.guild.id)])[0]
                                        checkQueue = self.bot.music[str(message.guild.id)][
                                            queueFirstIndex]["title"]
                                        requester = self.bot.music[str(message.guild.id)][str(
                                            queueFirstIndex)]['requester']
                                except IndexError:
                                    try:
                                        embed = discord.Embed(title="No music playing currently", color=0x0098ff)
                                        embed.set_image(url=splashart_url)
                                        embed.set_footer(text=f"Prefix for this server is: {prefix(self.bot, message)[0]}")
                                        content = "**__Queue list:__**\nJoin a voice channel and queue songs by name or url in here."
                                        coroutine = msg.edit(content=content, embed=embed)
                                        asyncio.run_coroutine_threadsafe(coroutine, self.bot.loop)
                                        time.sleep(120)
                                        if message.guild.voice_client.is_playing():
                                            return
                                        else:
                                            if message.guild.voice_client.is_connected():
                                                coroutine2 = message.guild.voice_client.disconnect()
                                                asyncio.run_coroutine_threadsafe(
                                                    coroutine2, self.bot.loop)
                                                return
                                            else:
                                                return
                                    except Exception as e:
                                        print(e)
                                
                                if not message.guild.voice_client.is_playing():
                                    song = self.bot.music[str(message.guild.id)][queueFirstIndex]
                                    source = song['source']

                                    try:
                                        findUpcoming = list(
                                            self.bot.music[str(message.guild.id)])[1]
                                        upcoming = self.bot.music[str(
                                            message.guild.id)][str(findUpcoming)]['title']
                                    except IndexError:
                                        upcoming = "None"
                                    
                                    message.guild.voice_client.play(discord.FFmpegPCMAudio(
                                        source=source, **FFMPEG_OPTIONS), after=after)
                                    message.guild.voice_client.source = discord.PCMVolumeTransformer(
                                        message.guild.voice_client.source)
                                    message.guild.voice_client.source.volume = self.bot.voice_client_attributes[str(message.guild.id)]['volume'] / 100

                                    var = {'seek': False, 'seek_position': '0'}
                                    self.bot.voice_client_attributes[str(message.guild.id)].update(var)

                                    if self.bot.voice_client_attributes[str(message.guild.id)]['send_play_embed'] is True:
                                        musicList = list(self.bot.music[str(message.guild.id)])
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
                                                    message.guild.id)][str(music)]['title']
                                                url = self.bot.music[str(
                                                    message.guild.id)][str(music)]['url']
                                                duration = self.bot.music[str(
                                                    message.guild.id)][str(music)]['duration']
                                                requester = self.bot.music[str(
                                                    message.guild.id)][str(music)]['requester']

                                                if len(complete_list + f"{i + 1}. {title}" + f" [{duration}] - {message.guild.get_member_named(requester).mention}\n") > 1900:
                                                    i = i + 1
                                                    char_limit = True
                                                    extra_songs += 1
                                                    continue
                                                else:
                                                    complete_list = complete_list + f"{i + 1}. {title}" + f" [{duration}] - {message.guild.get_member_named(requester).mention}\n"
                                                    i = i + 1
                                        
                                        if char_limit is True:
                                            complete_list += f"**And {extra_songs} More...**"

                                        loopStatus = ""
                                        if self.bot.voice_client_attributes[str(message.guild.id)]['loop'] is True:
                                            loopStatus = loopStatus + "✅"
                                        else:
                                            loopStatus = loopStatus + "❌"

                                        loopqueueStatus = ""
                                        if self.bot.voice_client_attributes[str(message.guild.id)]['loop_queue'] is True:
                                            loopqueueStatus = loopqueueStatus + "✅"
                                        else:
                                            loopqueueStatus = loopqueueStatus + "❌"
                                            
                                        radioStatus = ""
                                        if self.bot.voice_client_attributes[str(message.guild.id)]['radio'] is True:
                                            radioStatus = radioStatus + "✅"
                                        else:
                                            radioStatus = radioStatus + "❌"   

                                        text = ""
                                        if i <= 1:
                                            text += "music"
                                        if i > 1:
                                            text += "musics"
                                        
                                        embed = discord.Embed(description=f"**[{song['duration']}] - [{song['title']}]({song['url']})**\nRequested by {message.guild.get_member_named(requester).mention}", color=0x0098ff)
                                        embed.set_image(url=song['thumbnail'])
                                        embed.set_footer(text=f"{i} {text} in queue | Loop: {loopStatus} | Loop Queue: {loopqueueStatus} | Radio: {radioStatus}")

                                        queue = f"**__Queue list:__**\n{complete_list}"
                                        coroutine = msg.edit(content=queue, embed=embed)
                                        asyncio.run_coroutine_threadsafe(coroutine, self.bot.loop)
                                    else:
                                        var = {'send_play_embed': True}
                                        self.bot.voice_client_attributes[str(message.guild.id)].update(var)
                                else:
                                    return
                            except:
                                embed = discord.Embed(title="No music playing currently", color=0x0098ff)
                                embed.set_image(url=splashart_url)
                                embed.set_footer(text=f"Prefix for this server is: {prefix(self.bot, message)[0]}")
                                content = "**__Queue list:__**\nJoin a voice channel and queue songs by name or url in here."
                                coroutine = msg.edit(content=content, embed=embed)
                                asyncio.run_coroutine_threadsafe(coroutine, self.bot.loop)
                                return
                        except:
                            pass

                    try:
                        if message.author.voice is not None:
                            vc = message.author.voice.channel

                            if not message.guild.voice_client or not message.guild.voice_client.is_connected():
                                user = await message.guild.fetch_member(self.bot.user.id)

                                if user.permissions_in(vc).connect is False:
                                    embed = discord.Embed(
                                        title="Bot requires Connect permission(s) to run this command.", colour=0xff0000)
                                    await message.channel.send(embed=embed)
                                    return

                                if user.permissions_in(vc).speak is False:
                                    embed = discord.Embed(
                                        title="Bot requires Speak permission(s) to run this command.", colour=0xff0000)
                                    await message.channel.send(embed=embed)
                                    return

                                self.bot.music.pop(str(message.guild.id), None)
                                self.bot.voice_client_attributes.pop(
                                    str(message.guild.id), None)
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

                                value = self.bot.voice_client_attributes.get(
                                    str(message.guild.id))
                                if value is None:
                                    self.bot.voice_client_attributes[str(
                                        message.guild.id)] = attr
                                else:
                                    pass

                            if message.guild.voice_client.is_connected() and vc != message.guild.voice_client.channel:
                                embed3 = discord.Embed(title="You Must Be In The Same Voice Channel As The Bot To Use This Command.",
                                                       colour=0xff0000)
                                await message.channel.send(embed=embed3)
                                return

                            if self.bot.voice_client_attributes[str(message.guild.id)]['radio'] is False:
                                FFMPEG_OPTIONS = {"before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                                                  "options": f"-vn -ss {self.bot.voice_client_attributes[str(message.guild.id)]['seek_position']}"}

                                try:
                                    user = await message.guild.fetch_member(self.bot.user.id)

                                    if user.permissions_in(vc).speak is False:
                                        embed = discord.Embed(
                                            title="Bot requires Speak permission(s) to run this command.", colour=0xff0000)
                                        await message.channel.send(embed=embed)
                                        return

                                    query = message.content.strip('<>')

                                    try:
                                        if "youtube.com/playlist?list=" in query or "youtu.be/playlist?list=" in query or "youtube.com/watch?v=" and "&list=" in query or "youtu.be/" and "&list=" in query:
                                            var = {'block_skip_and_stop': True}
                                            self.bot.voice_client_attributes[str(
                                                message.guild.id)].update(var)

                                            query = parse_qs(
                                                urlparse(query).query, keep_blank_values=True)
                                            playlist_id = query["list"][0]

                                            youtube = googleapiclient.discovery.build(
                                                "youtube", "v3", developerKey=developer_key)

                                            request = youtube.playlistItems().list(
                                                part="snippet",
                                                playlistId=playlist_id,
                                                maxResults=10
                                            )
                                            response = request.execute()
                                            playlist_items = []

                                            while request is not None:
                                                response = request.execute()
                                                playlist_items += response["items"]
                                                request = youtube.playlistItems().list_next(request, response)

                                            msg2 = await message.channel.send(f"0/{len(playlist_items)} Music Added To Queue.")
                                            for vid in playlist_items:
                                                try:
                                                    vidIndex = playlist_items.index(
                                                        vid) + 1
                                                    totalIndex = len(
                                                        playlist_items)
                                                    url = f"https://youtube.com/watch?v={vid['snippet']['resourceId']['videoId']}"

                                                    song = self.urlsearch(url)
                                                    source = song['source']
                                                    details = {"title": song['title'],
                                                            "url": str(song['url']),
                                                            "source": source,
                                                            "duration": str(song['duration']),
                                                            "time": str(song['time']),
                                                            "thumbnail": str(song['thumbnail']),
                                                            "channel": str(song['channel']),
                                                            "requester": str(message.author),
                                                            "is_spotify": song['is_spotify']}

                                                    value = self.bot.music.get(
                                                        str(message.guild.id))
                                                    if value is None:
                                                        self.bot.music[str(
                                                            message.guild.id)] = {}
                                                    else:
                                                        pass
                                                    if str(song['title']) in self.bot.music[str(message.guild.id)]:
                                                        self.bot.music[str(message.guild.id)
                                                                       ][str(song['title']) + f" ({i})"] = {}
                                                        self.bot.music[str(message.guild.id)][str(
                                                            song['title']) + f" ({i})"] = details
                                                        i += 1
                                                    else:
                                                        self.bot.music[str(message.guild.id)
                                                                       ][str(song['title'])] = {}
                                                        self.bot.music[str(message.guild.id)][str(
                                                            song['title'])] = details

                                                    try:
                                                        findUpcoming = list(
                                                            self.bot.music[str(message.guild.id)])[1]
                                                        upcoming = self.bot.music[str(
                                                            message.guild.id)][str(findUpcoming)]['title']
                                                    except IndexError:
                                                        upcoming = "None"

                                                    if message.guild.voice_client is not None:
                                                        if not message.guild.voice_client.is_playing():
                                                            message.guild.voice_client.play(discord.FFmpegPCMAudio(
                                                                source=source, **FFMPEG_OPTIONS), after=after)
                                                            message.guild.voice_client.source = discord.PCMVolumeTransformer(
                                                                message.guild.voice_client.source)
                                                            message.guild.voice_client.source.volume = self.bot.voice_client_attributes[str(
                                                                message.guild.id)]['volume'] / 100

                                                            musicList = list(
                                                                self.bot.music[str(message.guild.id)])
                                                            i = 0
                                                            skipFirst = 0
                                                            complete_list = ""
                                                            for music in musicList:
                                                                if skipFirst == 0:
                                                                    skipFirst += 1
                                                                else:
                                                                    title = self.bot.music[str(
                                                                        message.guild.id)][str(music)]['title']
                                                                    url = self.bot.music[str(
                                                                        message.guild.id)][str(music)]['url']
                                                                    duration = self.bot.music[str(
                                                                        message.guild.id)][str(music)]['duration']
                                                                    requester = self.bot.music[str(
                                                                        message.guild.id)][str(music)]['requester']

                                                                    complete_list = complete_list + \
                                                                        f"{i + 1}. {title}" + \
                                                                        f" [{duration}] - {message.guild.get_member_named(requester).mention}\n"
                                                                    i = i + 1

                                                            loopStatus = ""
                                                            if self.bot.voice_client_attributes[str(message.guild.id)]['loop'] is True:
                                                                loopStatus = loopStatus + "✅"
                                                            else:
                                                                loopStatus = loopStatus + "❌"

                                                            loopqueueStatus = ""
                                                            if self.bot.voice_client_attributes[str(message.guild.id)]['loop_queue'] is True:
                                                                loopqueueStatus = loopqueueStatus + "✅"
                                                            else:
                                                                loopqueueStatus = loopqueueStatus + "❌"

                                                            radioStatus = ""
                                                            if self.bot.voice_client_attributes[str(message.guild.id)]['radio'] is True:
                                                                radioStatus = radioStatus + "✅"
                                                            else:
                                                                radioStatus = radioStatus + "❌"

                                                            text = ""
                                                            if i <= 1:
                                                                text += "music"
                                                            if i > 1:
                                                                text += "musics"

                                                            embed = discord.Embed(
                                                                description=f"**[{song['duration']}] - [{song['title']}]({song['url']})**\nRequested by {message.author.mention}", color=0x0098ff)
                                                            embed.set_image(
                                                                url=song['thumbnail'])
                                                            embed.set_footer(
                                                                text=f"{i} {text} in queue | Loop: {loopStatus} | Loop Queue: {loopqueueStatus} | Radio: {radioStatus}")

                                                            queue = f"**__Queue list:__**\n{complete_list}"
                                                            coroutine = msg.edit(
                                                                content=queue, embed=embed)
                                                            asyncio.run_coroutine_threadsafe(
                                                                coroutine, self.bot.loop)
                                                    else:
                                                        return
                                                    await msg2.edit(content=f"{vidIndex}/{totalIndex} Music Added To Queue.")
                                                except:
                                                    continue
                                            await msg2.edit(content="All Available Music From YouTube Playlist Added To Queue.", delete_after=10)
                                            musicList = list(
                                                self.bot.music[str(message.guild.id)])
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
                                                        message.guild.id)][str(music)]['title']
                                                    url = self.bot.music[str(
                                                        message.guild.id)][str(music)]['url']
                                                    duration = self.bot.music[str(
                                                        message.guild.id)][str(music)]['duration']
                                                    requester = self.bot.music[str(
                                                        message.guild.id)][str(music)]['requester']

                                                    if len(complete_list + f"{i + 1}. {title}" + f" [{duration}] - {message.guild.get_member_named(requester).mention}\n") > 1900:
                                                        i = i + 1
                                                        char_limit = True
                                                        extra_songs += 1
                                                        continue
                                                    else:
                                                        complete_list = complete_list + f"{i + 1}. {title}" + f" [{duration}] - {message.guild.get_member_named(requester).mention}\n"
                                                        i = i + 1
                                            
                                            if char_limit is True:
                                                complete_list += f"**And {extra_songs} More...**"

                                            loopStatus = ""
                                            if self.bot.voice_client_attributes[str(message.guild.id)]['loop'] is True:
                                                loopStatus = loopStatus + "✅"
                                            else:
                                                loopStatus = loopStatus + "❌"

                                            loopqueueStatus = ""
                                            if self.bot.voice_client_attributes[str(message.guild.id)]['loop_queue'] is True:
                                                loopqueueStatus = loopqueueStatus + "✅"
                                            else:
                                                loopqueueStatus = loopqueueStatus + "❌"

                                            radioStatus = ""
                                            if self.bot.voice_client_attributes[str(message.guild.id)]['radio'] is True:
                                                radioStatus = radioStatus + "✅"
                                            else:
                                                radioStatus = radioStatus + "❌"

                                            text = ""
                                            if i <= 1:
                                                text += "music"
                                            if i > 1:
                                                text += "musics"

                                            checkQueue = list(
                                                self.bot.music[str(message.guild.id)])[0]
                                            title = self.bot.music[str(
                                                message.guild.id)][str(checkQueue)]['title']
                                            url = self.bot.music[str(
                                                message.guild.id)][str(checkQueue)]['url']
                                            duration = self.bot.music[str(
                                                message.guild.id)][str(checkQueue)]['duration']
                                            thumbnail = self.bot.music[str(
                                                message.guild.id)][str(checkQueue)]['thumbnail']
                                            requester = self.bot.music[str(
                                                message.guild.id)][str(checkQueue)]['requester']

                                            embed = discord.Embed(
                                                description=f"**[{duration}] - [{title}]({url})**\nRequested by {message.guild.get_member_named(requester).mention}", color=0x0098ff)
                                            embed.set_image(url=thumbnail)
                                            embed.set_footer(
                                                text=f"{i} {text} in queue | Loop: {loopStatus} | Loop Queue: {loopqueueStatus} | Radio: {radioStatus}")

                                            queue = f"**__Queue list:__**\n{complete_list}"
                                            await msg.edit(content=queue, embed=embed)

                                            var = {
                                                'block_skip_and_stop': False}
                                            self.bot.voice_client_attributes[str(
                                                message.guild.id)].update(var)
                                            return

                                        if "open.spotify.com/playlist" in query:
                                            var = {'block_skip_and_stop': True}
                                            self.bot.voice_client_attributes[str(
                                                message.guild.id)].update(var)

                                            playlist = spotify.playlist_tracks(query)

                                            msg2 = await message.channel.send(f"0/{len(playlist['items'])} Music Added To Queue.")
                                            for item in playlist["items"]:
                                                try:
                                                    all_artists = ""
                                                    artists = item["track"]["artists"]
                                                    for artist in artists:
                                                        if artists.index(artist) == 0:
                                                            all_artists += artist['name']

                                                        if artists.index(artist) > 0:
                                                            all_artists += f", {artist['name']}"

                                                    title = item["track"]["name"]
                                                    thumbnail = item["track"]["album"]["images"][0]["url"]
                                                    url = item["track"]["external_urls"]["spotify"]
                                                    channel = "None"

                                                    itemIndex = playlist["items"].index(
                                                        item) + 1
                                                    totalIndex = len(playlist["items"])
                                                    song = self.search(f"{all_artists} - {title}")
                                                    source = song['source']
                                                    song_time = song['time']
                                                    duration = song['duration']

                                                    details = {"title": title,
                                                            "url": url,
                                                            "source": source,
                                                            "duration": str(duration),
                                                            "time": str(song_time),
                                                            "thumbnail": thumbnail,
                                                            "channel": channel,
                                                            "requester": str(message.author),
                                                            "is_spotify": True}

                                                    value = self.bot.music.get(
                                                        str(message.guild.id))
                                                    if value is None:
                                                        self.bot.music[str(
                                                            message.guild.id)] = {}
                                                    else:
                                                        pass
                                                    if str(title) in self.bot.music[str(message.guild.id)]:
                                                        self.bot.music[str(message.guild.id)
                                                                    ][str(title) + f" ({i})"] = {}
                                                        self.bot.music[str(message.guild.id)][str(
                                                            title) + f" ({i})"] = details
                                                        i += 1
                                                    else:
                                                        self.bot.music[str(message.guild.id)
                                                                    ][str(title)] = {}
                                                        self.bot.music[str(message.guild.id)][str(
                                                            title)] = details

                                                    try:
                                                        findUpcoming = list(
                                                            self.bot.music[str(message.guild.id)])[1]
                                                        upcoming = self.bot.music[str(
                                                            message.guild.id)][str(findUpcoming)]['title']
                                                    except IndexError:
                                                        upcoming = "None"

                                                    if message.guild.voice_client is not None:
                                                        if not message.guild.voice_client.is_playing():
                                                            message.guild.voice_client.play(discord.FFmpegPCMAudio(
                                                                source=source, **FFMPEG_OPTIONS), after=after)
                                                            message.guild.voice_client.source = discord.PCMVolumeTransformer(
                                                                message.guild.voice_client.source)
                                                            message.guild.voice_client.source.volume = self.bot.voice_client_attributes[str(
                                                                message.guild.id)]['volume'] / 100

                                                            musicList = list(
                                                                self.bot.music[str(message.guild.id)])
                                                            i = 0
                                                            skipFirst = 0
                                                            complete_list = ""
                                                            for music in musicList:
                                                                if skipFirst == 0:
                                                                    skipFirst += 1
                                                                else:
                                                                    title = self.bot.music[str(
                                                                        message.guild.id)][str(music)]['title']
                                                                    url = self.bot.music[str(
                                                                        message.guild.id)][str(music)]['url']
                                                                    duration = self.bot.music[str(
                                                                        message.guild.id)][str(music)]['duration']
                                                                    requester = self.bot.music[str(
                                                                        message.guild.id)][str(music)]['requester']

                                                                    complete_list = complete_list + \
                                                                        f"{i + 1}. {title}" + \
                                                                        f" [{duration}] - {message.guild.get_member_named(requester).mention}\n"
                                                                    i = i + 1

                                                            loopStatus = ""
                                                            if self.bot.voice_client_attributes[str(message.guild.id)]['loop'] is True:
                                                                loopStatus = loopStatus + "✅"
                                                            else:
                                                                loopStatus = loopStatus + "❌"

                                                            loopqueueStatus = ""
                                                            if self.bot.voice_client_attributes[str(message.guild.id)]['loop_queue'] is True:
                                                                loopqueueStatus = loopqueueStatus + "✅"
                                                            else:
                                                                loopqueueStatus = loopqueueStatus + "❌"

                                                            radioStatus = ""
                                                            if self.bot.voice_client_attributes[str(message.guild.id)]['radio'] is True:
                                                                radioStatus = radioStatus + "✅"
                                                            else:
                                                                radioStatus = radioStatus + "❌"

                                                            text = ""
                                                            if i <= 1:
                                                                text += "music"
                                                            if i > 1:
                                                                text += "musics"

                                                            embed = discord.Embed(
                                                                description=f"**[{duration}] - [{title}]({url})**\nRequested by {message.author.mention}", color=0x0098ff)
                                                            embed.set_image(
                                                                url=thumbnail)
                                                            embed.set_footer(
                                                                text=f"{i} {text} in queue | Loop: {loopStatus} | Loop Queue: {loopqueueStatus} | Radio: {radioStatus}")

                                                            queue = f"**__Queue list:__**\n{complete_list}"
                                                            coroutine = msg.edit(
                                                                content=queue, embed=embed)
                                                            asyncio.run_coroutine_threadsafe(
                                                                coroutine, self.bot.loop)
                                                    else:
                                                        return
                                                    await msg2.edit(content=f"{itemIndex}/{totalIndex} Music Added To Queue.")
                                                except:
                                                    continue
                                            await msg2.edit(content="All Available Music From Spotify Playlist Added To Queue.", delete_after=10)
                                            musicList = list(
                                                self.bot.music[str(message.guild.id)])
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
                                                        message.guild.id)][str(music)]['title']
                                                    url = self.bot.music[str(
                                                        message.guild.id)][str(music)]['url']
                                                    duration = self.bot.music[str(
                                                        message.guild.id)][str(music)]['duration']
                                                    requester = self.bot.music[str(
                                                        message.guild.id)][str(music)]['requester']

                                                    if len(complete_list + f"{i + 1}. {title}" + f" [{duration}] - {message.guild.get_member_named(requester).mention}\n") > 1900:
                                                        i = i + 1
                                                        char_limit = True
                                                        extra_songs += 1
                                                        continue
                                                    else:
                                                        complete_list = complete_list + f"{i + 1}. {title}" + f" [{duration}] - {message.guild.get_member_named(requester).mention}\n"
                                                        i = i + 1
                                            
                                            if char_limit is True:
                                                complete_list += f"**And {extra_songs} More...**"

                                            loopStatus = ""
                                            if self.bot.voice_client_attributes[str(message.guild.id)]['loop'] is True:
                                                loopStatus = loopStatus + "✅"
                                            else:
                                                loopStatus = loopStatus + "❌"

                                            loopqueueStatus = ""
                                            if self.bot.voice_client_attributes[str(message.guild.id)]['loop_queue'] is True:
                                                loopqueueStatus = loopqueueStatus + "✅"
                                            else:
                                                loopqueueStatus = loopqueueStatus + "❌"

                                            radioStatus = ""
                                            if self.bot.voice_client_attributes[str(message.guild.id)]['radio'] is True:
                                                radioStatus = radioStatus + "✅"
                                            else:
                                                radioStatus = radioStatus + "❌"

                                            text = ""
                                            if i <= 1:
                                                text += "music"
                                            if i > 1:
                                                text += "musics"

                                            checkQueue = list(
                                                self.bot.music[str(message.guild.id)])[0]
                                            title = self.bot.music[str(
                                                message.guild.id)][str(checkQueue)]['title']
                                            url = self.bot.music[str(
                                                message.guild.id)][str(checkQueue)]['url']
                                            duration = self.bot.music[str(
                                                message.guild.id)][str(checkQueue)]['duration']
                                            thumbnail = self.bot.music[str(
                                                message.guild.id)][str(checkQueue)]['thumbnail']
                                            requester = self.bot.music[str(
                                                message.guild.id)][str(checkQueue)]['requester']

                                            embed = discord.Embed(
                                                description=f"**[{duration}] - [{title}]({url})**\nRequested by {message.guild.get_member_named(requester).mention}", color=0x0098ff)
                                            embed.set_image(url=thumbnail)
                                            embed.set_footer(
                                                text=f"{i} {text} in queue | Loop: {loopStatus} | Loop Queue: {loopqueueStatus} | Radio: {radioStatus}")

                                            queue = f"**__Queue list:__**\n{complete_list}"
                                            await msg.edit(content=queue, embed=embed)

                                            var = {
                                                'block_skip_and_stop': False}
                                            self.bot.voice_client_attributes[str(
                                                message.guild.id)].update(var)
                                            return

                                        if "open.spotify.com/track" in query:
                                            song = self.spotifysearch(query)
                                            source = song['source']
                                            details = {"title": song['title'],
                                                    "url": str(song['url']),
                                                    "source": source,
                                                    "duration": str(song['duration']),
                                                    "time": str(song['time']),
                                                    "thumbnail": str(song['thumbnail']),
                                                    "channel": str(song['channel']),
                                                    "requester": str(message.author),
                                                    "is_spotify": song['is_spotify']}

                                            value = self.bot.music.get(str(message.guild.id))
                                            if value is None:
                                                self.bot.music[str(message.guild.id)] = {}
                                            else:
                                                pass
                                            if str(song['title']) in self.bot.music[str(message.guild.id)]:
                                                self.bot.music[str(message.guild.id)
                                                            ][str(song['title']) + f" ({i})"] = {}
                                                self.bot.music[str(message.guild.id)][str(
                                                    song['title']) + f" ({i})"] = details
                                                i += 1
                                            else:
                                                self.bot.music[str(message.guild.id)
                                                            ][str(song['title'])] = {}
                                                self.bot.music[str(message.guild.id)][str(
                                                    song['title'])] = details

                                            if message.guild.voice_client is not None:
                                                if not message.guild.voice_client.is_playing():
                                                    message.guild.voice_client.play(discord.FFmpegPCMAudio(
                                                        source=source, **FFMPEG_OPTIONS), after=after)
                                                    message.guild.voice_client.source = discord.PCMVolumeTransformer(
                                                        message.guild.voice_client.source)
                                                    message.guild.voice_client.source.volume = self.bot.voice_client_attributes[str(
                                                        message.guild.id)]['volume'] / 100

                                                    musicList = list(
                                                        self.bot.music[str(message.guild.id)])
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
                                                                message.guild.id)][str(music)]['title']
                                                            url = self.bot.music[str(
                                                                message.guild.id)][str(music)]['url']
                                                            duration = self.bot.music[str(
                                                                message.guild.id)][str(music)]['duration']
                                                            requester = self.bot.music[str(
                                                                message.guild.id)][str(music)]['requester']

                                                            if len(complete_list + f"{i + 1}. {title}" + f" [{duration}] - {message.guild.get_member_named(requester).mention}\n") > 1900:
                                                                i = i + 1
                                                                char_limit = True
                                                                extra_songs += 1
                                                                continue
                                                            else:
                                                                complete_list = complete_list + f"{i + 1}. {title}" + f" [{duration}] - {message.guild.get_member_named(requester).mention}\n"
                                                                i = i + 1
                                                    
                                                    if char_limit is True:
                                                        complete_list += f"**And {extra_songs} More...**"

                                                    loopStatus = ""
                                                    if self.bot.voice_client_attributes[str(message.guild.id)]['loop'] is True:
                                                        loopStatus = loopStatus + "✅"
                                                    else:
                                                        loopStatus = loopStatus + "❌"

                                                    loopqueueStatus = ""
                                                    if self.bot.voice_client_attributes[str(message.guild.id)]['loop_queue'] is True:
                                                        loopqueueStatus = loopqueueStatus + "✅"
                                                    else:
                                                        loopqueueStatus = loopqueueStatus + "❌"

                                                    radioStatus = ""
                                                    if self.bot.voice_client_attributes[str(message.guild.id)]['radio'] is True:
                                                        radioStatus = radioStatus + "✅"
                                                    else:
                                                        radioStatus = radioStatus + "❌"

                                                    text = ""
                                                    if i <= 1:
                                                        text += "music"
                                                    if i > 1:
                                                        text += "musics"

                                                    embed = discord.Embed(
                                                        description=f"**[{song['duration']}] - [{song['title']}]({song['url']})**\nRequested by {message.author.mention}", color=0x0098ff)
                                                    embed.set_image(
                                                        url=song['thumbnail'])
                                                    embed.set_footer(
                                                        text=f"{i} {text} in queue | Loop: {loopStatus} | Loop Queue: {loopqueueStatus} | Radio: {radioStatus}")

                                                    queue = f"**__Queue list:__**\n{complete_list}"
                                                    coroutine = msg.edit(
                                                        content=queue, embed=embed)
                                                    asyncio.run_coroutine_threadsafe(
                                                        coroutine, self.bot.loop)
                                                    return
                                                else:
                                                    musicList = list(
                                                        self.bot.music[str(message.guild.id)])
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
                                                                message.guild.id)][str(music)]['title']
                                                            url = self.bot.music[str(
                                                                message.guild.id)][str(music)]['url']
                                                            duration = self.bot.music[str(
                                                                message.guild.id)][str(music)]['duration']
                                                            requester = self.bot.music[str(
                                                                message.guild.id)][str(music)]['requester']

                                                            if len(complete_list + f"{i + 1}. {title}" + f" [{duration}] - {message.guild.get_member_named(requester).mention}\n") > 1900:
                                                                i = i + 1
                                                                char_limit = True
                                                                extra_songs += 1
                                                                continue
                                                            else:
                                                                complete_list = complete_list + f"{i + 1}. {title}" + f" [{duration}] - {message.guild.get_member_named(requester).mention}\n"
                                                                i = i + 1
                                                    
                                                    if char_limit is True:
                                                        complete_list += f"**And {extra_songs} More...**"

                                                    loopStatus = ""
                                                    if self.bot.voice_client_attributes[str(message.guild.id)]['loop'] is True:
                                                        loopStatus = loopStatus + "✅"
                                                    else:
                                                        loopStatus = loopStatus + "❌"

                                                    loopqueueStatus = ""
                                                    if self.bot.voice_client_attributes[str(message.guild.id)]['loop_queue'] is True:
                                                        loopqueueStatus = loopqueueStatus + "✅"
                                                    else:
                                                        loopqueueStatus = loopqueueStatus + "❌"

                                                    radioStatus = ""
                                                    if self.bot.voice_client_attributes[str(message.guild.id)]['radio'] is True:
                                                        radioStatus = radioStatus + "✅"
                                                    else:
                                                        radioStatus = radioStatus + "❌"

                                                    text = ""
                                                    if i <= 1:
                                                        text += "music"
                                                    if i > 1:
                                                        text += "musics"

                                                    checkQueue = list(
                                                        self.bot.music[str(message.guild.id)])[0]
                                                    title = self.bot.music[str(
                                                        message.guild.id)][str(checkQueue)]['title']
                                                    url = self.bot.music[str(
                                                        message.guild.id)][str(checkQueue)]['url']
                                                    duration = self.bot.music[str(
                                                        message.guild.id)][str(checkQueue)]['duration']
                                                    thumbnail = self.bot.music[str(
                                                        message.guild.id)][str(checkQueue)]['thumbnail']
                                                    requester = self.bot.music[str(
                                                        message.guild.id)][str(checkQueue)]['requester']

                                                    embed = discord.Embed(
                                                        description=f"**[{duration}] - [{title}]({url})**\nRequested by {message.guild.get_member_named(requester).mention}", color=0x0098ff)
                                                    embed.set_image(
                                                        url=thumbnail)
                                                    embed.set_footer(
                                                        text=f"{i} {text} in queue | Loop: {loopStatus} | Loop Queue: {loopqueueStatus} | Radio: {radioStatus}")

                                                    queue = f"**__Queue list:__**\n{complete_list}"
                                                    coroutine = msg.edit(
                                                        content=queue, embed=embed)
                                                    asyncio.run_coroutine_threadsafe(
                                                        coroutine, self.bot.loop)
                                                    return
                                            else:
                                                return

                                        else:
                                            song = self.search(query)
                                            source = song['source']
                                            details = {"title": song['title'],
                                                    "url": str(song['url']),
                                                    "source": source,
                                                    "duration": str(song['duration']),
                                                    "time": str(song['time']),
                                                    "thumbnail": str(song['thumbnail']),
                                                    "channel": str(song['channel']),
                                                    "requester": str(message.author),
                                                    "is_spotify": song['is_spotify']}

                                            value = self.bot.music.get(
                                                str(message.guild.id))
                                            if value is None:
                                                self.bot.music[str(
                                                    message.guild.id)] = {}
                                            else:
                                                pass
                                            if str(song['title']) in self.bot.music[str(message.guild.id)]:
                                                self.bot.music[str(message.guild.id)
                                                               ][str(song['title']) + f" ({i})"] = {}
                                                self.bot.music[str(message.guild.id)][str(
                                                    song['title']) + f" ({i})"] = details
                                                i += 1
                                            else:
                                                self.bot.music[str(message.guild.id)
                                                               ][str(song['title'])] = {}
                                                self.bot.music[str(message.guild.id)][str(
                                                    song['title'])] = details

                                            if message.guild.voice_client is not None:
                                                if not message.guild.voice_client.is_playing():
                                                    message.guild.voice_client.play(discord.FFmpegPCMAudio(
                                                        source=source, **FFMPEG_OPTIONS), after=after)
                                                    message.guild.voice_client.source = discord.PCMVolumeTransformer(
                                                        message.guild.voice_client.source)
                                                    message.guild.voice_client.source.volume = self.bot.voice_client_attributes[str(
                                                        message.guild.id)]['volume'] / 100

                                                    musicList = list(
                                                        self.bot.music[str(message.guild.id)])
                                                    i = 0
                                                    skipFirst = 0
                                                    complete_list = ""
                                                    for music in musicList:
                                                        if skipFirst == 0:
                                                            skipFirst += 1
                                                        else:
                                                            title = self.bot.music[str(
                                                                message.guild.id)][str(music)]['title']
                                                            url = self.bot.music[str(
                                                                message.guild.id)][str(music)]['url']
                                                            duration = self.bot.music[str(
                                                                message.guild.id)][str(music)]['duration']
                                                            requester = self.bot.music[str(
                                                                message.guild.id)][str(music)]['requester']

                                                            complete_list = complete_list + \
                                                                f"{i + 1}. {title}" + \
                                                                f" [{duration}] - {message.guild.get_member_named(requester).mention}\n"
                                                            i = i + 1

                                                    loopStatus = ""
                                                    if self.bot.voice_client_attributes[str(message.guild.id)]['loop'] is True:
                                                        loopStatus = loopStatus + "✅"
                                                    else:
                                                        loopStatus = loopStatus + "❌"

                                                    loopqueueStatus = ""
                                                    if self.bot.voice_client_attributes[str(message.guild.id)]['loop_queue'] is True:
                                                        loopqueueStatus = loopqueueStatus + "✅"
                                                    else:
                                                        loopqueueStatus = loopqueueStatus + "❌"

                                                    radioStatus = ""
                                                    if self.bot.voice_client_attributes[str(message.guild.id)]['radio'] is True:
                                                        radioStatus = radioStatus + "✅"
                                                    else:
                                                        radioStatus = radioStatus + "❌"

                                                    text = ""
                                                    if i <= 1:
                                                        text += "music"
                                                    if i > 1:
                                                        text += "musics"

                                                    embed = discord.Embed(
                                                        description=f"**[{song['duration']}] - [{song['title']}]({song['url']})**\nRequested by {message.author.mention}", color=0x0098ff)
                                                    embed.set_image(
                                                        url=song['thumbnail'])
                                                    embed.set_footer(
                                                        text=f"{i} {text} in queue | Loop: {loopStatus} | Loop Queue: {loopqueueStatus} | Radio: {radioStatus}")

                                                    queue = f"**__Queue list:__**\n{complete_list}"
                                                    coroutine = msg.edit(
                                                        content=queue, embed=embed)
                                                    asyncio.run_coroutine_threadsafe(
                                                        coroutine, self.bot.loop)
                                                    return
                                                else:
                                                    musicList = list(
                                                        self.bot.music[str(message.guild.id)])
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
                                                                message.guild.id)][str(music)]['title']
                                                            url = self.bot.music[str(
                                                                message.guild.id)][str(music)]['url']
                                                            duration = self.bot.music[str(
                                                                message.guild.id)][str(music)]['duration']
                                                            requester = self.bot.music[str(
                                                                message.guild.id)][str(music)]['requester']

                                                            if len(complete_list + f"{i + 1}. {title}" + f" [{duration}] - {message.guild.get_member_named(requester).mention}\n") > 1900:
                                                                i = i + 1
                                                                char_limit = True
                                                                extra_songs += 1
                                                                continue
                                                            else:
                                                                complete_list = complete_list + f"{i + 1}. {title}" + f" [{duration}] - {message.guild.get_member_named(requester).mention}\n"
                                                                i = i + 1
                                                    
                                                    if char_limit is True:
                                                        complete_list += f"**And {extra_songs} More...**"

                                                    loopStatus = ""
                                                    if self.bot.voice_client_attributes[str(message.guild.id)]['loop'] is True:
                                                        loopStatus = loopStatus + "✅"
                                                    else:
                                                        loopStatus = loopStatus + "❌"

                                                    loopqueueStatus = ""
                                                    if self.bot.voice_client_attributes[str(message.guild.id)]['loop_queue'] is True:
                                                        loopqueueStatus = loopqueueStatus + "✅"
                                                    else:
                                                        loopqueueStatus = loopqueueStatus + "❌"

                                                    radioStatus = ""
                                                    if self.bot.voice_client_attributes[str(message.guild.id)]['radio'] is True:
                                                        radioStatus = radioStatus + "✅"
                                                    else:
                                                        radioStatus = radioStatus + "❌"

                                                    text = ""
                                                    if i <= 1:
                                                        text += "music"
                                                    if i > 1:
                                                        text += "musics"

                                                    checkQueue = list(
                                                        self.bot.music[str(message.guild.id)])[0]
                                                    title = self.bot.music[str(
                                                        message.guild.id)][str(checkQueue)]['title']
                                                    url = self.bot.music[str(
                                                        message.guild.id)][str(checkQueue)]['url']
                                                    duration = self.bot.music[str(
                                                        message.guild.id)][str(checkQueue)]['duration']
                                                    thumbnail = self.bot.music[str(
                                                        message.guild.id)][str(checkQueue)]['thumbnail']
                                                    requester = self.bot.music[str(
                                                        message.guild.id)][str(checkQueue)]['requester']

                                                    embed = discord.Embed(
                                                        description=f"**[{duration}] - [{title}]({url})**\nRequested by {message.guild.get_member_named(requester).mention}", color=0x0098ff)
                                                    embed.set_image(
                                                        url=thumbnail)
                                                    embed.set_footer(
                                                        text=f"{i} {text} in queue | Loop: {loopStatus} | Loop Queue: {loopqueueStatus} | Radio: {radioStatus}")

                                                    queue = f"**__Queue list:__**\n{complete_list}"
                                                    coroutine = msg.edit(
                                                        content=queue, embed=embed)
                                                    asyncio.run_coroutine_threadsafe(
                                                        coroutine, self.bot.loop)
                                                    return
                                            else:
                                                return

                                    except Exception as e:
                                        print(e)
                                        embed6 = discord.Embed(
                                            title=f"An Error Occurred Or No Such Song Found.", colour=0xff0000)
                                        await message.channel.send(embed=embed6)
                                        return

                                except Exception as e:
                                    print(e)
                            else:
                                embed = discord.Embed(description=f"**{message.author.mention}, Cannot Play Music While Radio Is Playing.**\nUse `radio stop` Command To Stop The Radio.", colour=0xff0000)
                                await message.channel.send(embed=embed)
                                return
                        else:
                            embed7 = discord.Embed(description=f"**{message.author.mention}, You Must Be In A Voice Channel To Use This Command.**",
                                                   colour=0xff0000)
                            await message.channel.send(embed=embed7)
                            return
                    except Exception as e:
                        pass
                else:
                    return
            else:
                return

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):

        play_emoji = '\U000025B6'
        pause_emoji = '\U000023F8'
        stop_emoji = '\U000023F9'
        skip_emoji = '\U000023ED'
        shuffle_emoji = '\U0001F500'
        loop_emoji = '\U0001F504'
        loop_queue_emoji = '\U0000267E'
        disconnect_emoji = '\U0000274C'

        if payload.member.bot:
            return

        try:
            with open('./config.json', 'r+') as file:
                data = json.load(file)

                try:
                    channel_id = data['music'][str(
                        payload.guild_id)]['channel_id']
                except KeyError:
                    pass

                channel = self.bot.get_channel(channel_id)
                if channel is not None:
                    if channel.id == payload.channel_id:
                        try:
                            msg = await channel.fetch_message(data['music'][str(payload.guild_id)]['message_id'])
                            if msg.id == payload.message_id:
                                ctx = await self.bot.get_context(msg)
                                member = payload.member

                                async def checkConditions(ctx, member):
                                    try:
                                        if member.voice is not None:
                                            if ctx.voice_client is not None:
                                                if member.voice is not None and member.voice.channel == ctx.voice_client.channel:
                                                    if not ctx.voice_client.is_playing() and ctx.voice_client.is_paused() is True:
                                                        users = member.voice.channel.members
                                                        for member in member.voice.channel.members:
                                                            if member.bot:
                                                                users.remove(
                                                                    member)
                                                        if len(users) == 1:
                                                            return True
                                                        else:
                                                            if member.guild_permissions.administrator:
                                                                return True
                                                            else:
                                                                if member.guild_permissions.manage_channels:
                                                                    return True
                                                                else:
                                                                    for role in member.roles:
                                                                        if role.name == "DJ":
                                                                            return True
                                                                    else:
                                                                        embed2 = discord.Embed(
                                                                            description=f"**{member.mention} You Need `Administrator` Permission Or `DJ` Role Or `Manage Channels` Permission To Use This Command!** (Being Alone With The Bot Also Works.)", colour=0xff0000)
                                                                        await ctx.send(embed=embed2)
                                                                        return False
                                                    else:
                                                        embed2 = discord.Embed(
                                                            description=f"**{member.mention} Player Is Not Paused!**", colour=0xff0000)
                                                        await ctx.send(embed=embed2)
                                                        return False
                                                else:
                                                    embed3 = discord.Embed(
                                                        description=f"**{member.mention} You Must Be In The Same Voice Channel As The Bot To Use This Command!**", colour=0xff0000)
                                                    await ctx.send(embed=embed3)
                                                    return False
                                            else:
                                                embed4 = discord.Embed(
                                                    description=f"**{member.mention} I'm Not Connected To A Voice Channel!**", colour=0xff0000)
                                                await ctx.send(embed=embed4)
                                                return False
                                        else:
                                            embed5 = discord.Embed(
                                                description=f"**{member.mention} You Must Be In A Voice Channel To Use This Command!**", colour=0xff0000)
                                            await ctx.send(embed=embed5)
                                            return False
                                    except Exception as e:
                                        print(e)

                                async def checkConditions2(ctx, member):
                                    try:
                                        if member.voice is not None:
                                            if ctx.voice_client is not None:
                                                if member.voice is not None and member.voice.channel == ctx.voice_client.channel:
                                                    if ctx.voice_client.is_playing() and ctx.voice_client.is_paused() is False:
                                                        users = member.voice.channel.members
                                                        for member in member.voice.channel.members:
                                                            if member.bot:
                                                                users.remove(
                                                                    member)
                                                        if len(users) == 1:
                                                            return True
                                                        else:
                                                            if member.guild_permissions.administrator:
                                                                return True
                                                            else:
                                                                if member.guild_permissions.manage_channels:
                                                                    return True
                                                                else:
                                                                    for role in member.roles:
                                                                        if role.name == "DJ":
                                                                            return True
                                                                    else:
                                                                        embed2 = discord.Embed(
                                                                            description=f"**{member.mention} You Need `Administrator` Permission Or `DJ` Role Or `Manage Channels` Permission To Use This Command!** (Being Alone With The Bot Also Works.)", colour=0xff0000)
                                                                        await ctx.send(embed=embed2)
                                                                        return False
                                                    else:
                                                        embed2 = discord.Embed(
                                                            description=f"**{member.mention} Player Is Not Playing!**", colour=0xff0000)
                                                        await ctx.send(embed=embed2)
                                                        return False
                                                else:
                                                    embed3 = discord.Embed(
                                                        description=f"**{member.mention} You Must Be In The Same Voice Channel As The Bot To Use This Command!**", colour=0xff0000)
                                                    await ctx.send(embed=embed3)
                                                    return False
                                            else:
                                                embed4 = discord.Embed(
                                                    description=f"**{member.mention} I'm Not Connected To A Voice Channel!**", colour=0xff0000)
                                                await ctx.send(embed=embed4)
                                                return False
                                        else:
                                            embed5 = discord.Embed(
                                                description=f"**{member.mention} You Must Be In A Voice Channel To Use This Command!**", colour=0xff0000)
                                            await ctx.send(embed=embed5)
                                            return False
                                    except Exception as e:
                                        print(e)

                                async def checkConditions3(ctx, member):
                                    try:
                                        if member.voice is not None:
                                            if ctx.voice_client is not None:
                                                if member.voice is not None and member.voice.channel == ctx.voice_client.channel:
                                                    if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
                                                        if self.bot.voice_client_attributes[str(ctx.guild.id)]['block_skip_and_stop'] is False:
                                                            if self.bot.voice_client_attributes[str(ctx.guild.id)]['radio'] is False:
                                                                users = member.voice.channel.members
                                                                for member in member.voice.channel.members:
                                                                    if member.bot:
                                                                        users.remove(
                                                                            member)
                                                                if len(users) == 1:
                                                                    return True
                                                                else:
                                                                    if member.guild_permissions.administrator:
                                                                        return True
                                                                    else:
                                                                        if member.guild_permissions.manage_channels:
                                                                            return True
                                                                        else:
                                                                            for role in member.roles:
                                                                                if role.name == "DJ":
                                                                                    return True
                                                                            else:
                                                                                embed2 = discord.Embed(
                                                                                    description=f"**{member.mention} You Need `Administrator` Permission Or `DJ` Role Or `Manage Channels` Permission To Use This Command!** (Being Alone With The Bot Also Works.)", colour=0xff0000)
                                                                                await ctx.send(embed=embed2)
                                                                                return False
                                                            else:
                                                                embed = discord.Embed(
                                                                    description=f"**{member.mention} Cannot Skip & Stop Music While Radio Is Playing!**\nUse `radio stop` Command To Stop The Radio.", colour=0xff0000)
                                                                await ctx.send(embed=embed)
                                                                return False
                                                        else:
                                                            embed3 = discord.Embed(
                                                                description=f"**{member.mention} Cannot Skip & Stop While Adding Playlist In Queue!**", colour=0xff0000)
                                                            await ctx.send(embed=embed3)
                                                            return False
                                                    else:
                                                        embed4 = discord.Embed(
                                                            description=f"**{member.mention} Player Is Not Playing!**", colour=0xff0000)
                                                        await ctx.send(embed=embed4)
                                                        return False
                                                else:
                                                    embed5 = discord.Embed(
                                                        description=f"**{member.mention} You Must Be In The Same Voice Channel As The Bot To Use This Command!**", colour=0xff0000)
                                                    await ctx.send(embed=embed5)
                                                    return False
                                            else:
                                                embed6 = discord.Embed(
                                                    description=f"**{member.mention} I'm Not Connected To A Voice Channel!**", colour=0xff0000)
                                                await ctx.send(embed=embed6)
                                                return False
                                        else:
                                            embed7 = discord.Embed(
                                                description=f"**{member.mention} You Must Be In A Voice Channel To Use This Command!**", colour=0xff0000)
                                            await ctx.send(embed=embed7)
                                            return False
                                    except Exception as e:
                                        print(e)

                                async def checkConditions4(ctx, member):
                                    try:
                                        if member.voice is not None:
                                            if ctx.voice_client is not None:
                                                if member.voice is not None and member.voice.channel == ctx.voice_client.channel:
                                                    if self.bot.voice_client_attributes[str(ctx.guild.id)]['radio'] is False:
                                                        users = member.voice.channel.members
                                                        for member in member.voice.channel.members:
                                                            if member.bot:
                                                                users.remove(
                                                                    member)
                                                        if len(users) == 1:
                                                            return True
                                                        else:
                                                            if member.guild_permissions.administrator:
                                                                return True
                                                            else:
                                                                if member.guild_permissions.manage_channels:
                                                                    return True
                                                                else:
                                                                    for role in member.roles:
                                                                        if role.name == "DJ":
                                                                            return True
                                                                    else:
                                                                        embed2 = discord.Embed(
                                                                            description=f"**{member.mention} You Need `Administrator` Permission Or `DJ` Role Or `Manage Channels` Permission To Use This Command!** (Being Alone With The Bot Also Works.)", colour=0xff0000)
                                                                        await ctx.send(embed=embed2)
                                                                        return False
                                                    else:
                                                        embed = discord.Embed(
                                                            description=f"**{member.mention} Cannot Loop Music While Radio Is Playing!**", colour=0xff0000)
                                                        await ctx.send(embed=embed)
                                                        return False
                                                else:
                                                    embed3 = discord.Embed(
                                                        description=f"**{member.mention} You Must Be In The Same Voice Channel As The Bot To Use This Command!**", colour=0xff0000)
                                                    await ctx.send(embed=embed3)
                                                    return False
                                            else:
                                                embed4 = discord.Embed(
                                                    description=f"**{member.mention} I'm Not Connected To A Voice Channel!**", colour=0xff0000)
                                                await ctx.send(embed=embed4)
                                                return False
                                        else:
                                            embed5 = discord.Embed(
                                                description=f"**{member.mention} You Must Be In A Voice Channel To Use This Command!**", colour=0xff0000)
                                            await ctx.send(embed=embed5)
                                            return False
                                    except Exception as e:
                                        print(e)

                                async def checkConditions5(ctx, member):
                                    try:
                                        if member.voice is not None:
                                            if ctx.voice_client is not None:
                                                if member.voice is not None and member.voice.channel == ctx.voice_client.channel:
                                                    users = member.voice.channel.members
                                                    for member in member.voice.channel.members:
                                                        if member.bot:
                                                            users.remove(
                                                                member)
                                                    if len(users) == 1:
                                                        return True
                                                    else:
                                                        if member.guild_permissions.administrator:
                                                            return True
                                                        else:
                                                            if member.guild_permissions.manage_channels:
                                                                return True
                                                            else:
                                                                for role in member.roles:
                                                                    if role.name == "DJ":
                                                                        return True
                                                                else:
                                                                    embed2 = discord.Embed(
                                                                        description=f"**{member.mention} You Need `Administrator` Permission Or `DJ` Role Or `Manage Channels` Permission To Use This Command!** (Being Alone With The Bot Also Works.)", colour=0xff0000)
                                                                    await ctx.send(embed=embed2)
                                                                    return False
                                                else:
                                                    embed3 = discord.Embed(
                                                        description=f"**{member.mention} You Must Be In The Same Voice Channel As The Bot To Use This Command!**", colour=0xff0000)
                                                    await ctx.send(embed=embed3)
                                                    return False
                                            else:
                                                embed4 = discord.Embed(
                                                    description=f"**{member.mention} I'm Not Connected To A Voice Channel!**", colour=0xff0000)
                                                await ctx.send(embed=embed4)
                                                return False
                                        else:
                                            embed5 = discord.Embed(
                                                description=f"**{member.mention} You Must Be In A Voice Channel To Use This Command!**", colour=0xff0000)
                                            await ctx.send(embed=embed5)
                                            return False
                                    except Exception as e:
                                        print(e)

                                if str(payload.emoji) == play_emoji:
                                    await msg.remove_reaction(payload.emoji, member)

                                    async def resumeFunc():
                                        ctx.voice_client.resume()
                                        await ctx.invoke(self.bot.get_command('updatemsg'))
                                        return

                                    if await checkConditions(ctx, member) is True:
                                        await resumeFunc()
                                        return
                                    else:
                                        return

                                if str(payload.emoji) == pause_emoji:
                                    await msg.remove_reaction(payload.emoji, member)

                                    async def pauseFunc():
                                        ctx.voice_client.pause()
                                        await ctx.invoke(self.bot.get_command('updatemsg'))
                                        return

                                    if await checkConditions2(ctx, member) is True:
                                        await pauseFunc()
                                        return
                                    else:
                                        return

                                if str(payload.emoji) == stop_emoji:
                                    await msg.remove_reaction(payload.emoji, member)

                                    async def stopFunc():
                                        self.bot.music.pop(
                                            str(ctx.guild.id), None)
                                        ctx.voice_client.stop()
                                        return

                                    if await checkConditions3(ctx, member) is True:
                                        await stopFunc()
                                        return
                                    else:
                                        return

                                if str(payload.emoji) == skip_emoji:
                                    await msg.remove_reaction(payload.emoji, member)

                                    async def skipFunc():
                                        ctx.voice_client.stop()
                                        return

                                    if await checkConditions3(ctx, member) is True:
                                        await skipFunc()
                                        return
                                    else:
                                        return

                                if str(payload.emoji) == shuffle_emoji:
                                    await msg.remove_reaction(payload.emoji, member)

                                    async def shuffleFunc():
                                        new_dict = self.bot.music[str(
                                            ctx.guild.id)].copy()
                                        first_index = list(new_dict.keys())[0]
                                        popped = new_dict.pop(first_index)

                                        temp = list(new_dict.items())
                                        random.shuffle(temp)

                                        shuffled_dict = {}
                                        shuffled_dict[first_index] = popped
                                        shuffled_dict.update(dict(temp))
                                        self.bot.music.pop(
                                            str(ctx.guild.id), None)
                                        self.bot.music[str(ctx.guild.id)] = {}
                                        self.bot.music[str(ctx.guild.id)].update(
                                            shuffled_dict)

                                        await ctx.invoke(self.bot.get_command('updatemsg'))
                                        return

                                    if await checkConditions3(ctx, member) is True:
                                        await shuffleFunc()
                                        return
                                    else:
                                        return

                                if str(payload.emoji) == loop_emoji:
                                    await msg.remove_reaction(payload.emoji, member)

                                    async def loopFunc():
                                        if self.bot.voice_client_attributes[str(ctx.guild.id)]['loop'] is False:
                                            var = {'loop': True}
                                            self.bot.voice_client_attributes[str(
                                                ctx.guild.id)].update(var)
                                            await ctx.invoke(self.bot.get_command('updatemsg'))
                                            return
                                        else:
                                            var = {'loop': False}
                                            self.bot.voice_client_attributes[str(
                                                ctx.guild.id)].update(var)
                                            await ctx.invoke(self.bot.get_command('updatemsg'))
                                            return

                                    if await checkConditions4(ctx, member) is True:
                                        await loopFunc()
                                        return
                                    else:
                                        return

                                if str(payload.emoji) == loop_queue_emoji:
                                    await msg.remove_reaction(payload.emoji, member)

                                    async def loopqueueFunc():
                                        if self.bot.voice_client_attributes[str(ctx.guild.id)]['loop_queue'] is False:
                                            var = {'loop_queue': True}
                                            self.bot.voice_client_attributes[str(
                                                ctx.guild.id)].update(var)
                                            await ctx.invoke(self.bot.get_command('updatemsg'))
                                            return
                                        else:
                                            var = {'loop_queue': False}
                                            self.bot.voice_client_attributes[str(
                                                ctx.guild.id)].update(var)
                                            await ctx.invoke(self.bot.get_command('updatemsg'))
                                            return

                                    if await checkConditions4(ctx, member) is True:
                                        await loopqueueFunc()
                                        return
                                    else:
                                        return

                                if str(payload.emoji) == disconnect_emoji:
                                    await msg.remove_reaction(payload.emoji, member)

                                    async def disconnectClient():
                                        self.bot.music.pop(
                                            str(ctx.guild.id), None)
                                        self.bot.voice_client_attributes.pop(
                                            str(ctx.guild.id), None)
                                        if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
                                            ctx.voice_client.stop()
                                        await ctx.voice_client.disconnect()
                                        return

                                    if await checkConditions5(ctx, member) is True:
                                        await disconnectClient()
                                        return
                                    else:
                                        return
                            else:
                                pass
                        except discord.NotFound:
                            pass
                    else:
                        pass
                else:
                    pass

            with open('./config.json', 'r+') as file:
                data = json.load(file)
                try:
                    message_id = data['voting'][str(
                        payload.guild_id)][str(payload.message_id)]

                    if data['voting'][str(payload.guild_id)][str(payload.message_id)]["vote_multiple"] is True:
                        return
                    else:
                        if payload.user_id in data['voting'][str(payload.guild_id)][str(payload.message_id)]["users"]:
                            channel = self.bot.get_channel(payload.channel_id)
                            msg = await channel.fetch_message(payload.message_id)
                            await msg.remove_reaction(payload.emoji, payload.member)
                            return

                        if payload.user_id not in data['voting'][str(payload.guild_id)][str(payload.message_id)]["users"]:
                            users_list = list(
                                data['voting'][str(payload.guild_id)][str(payload.message_id)]["users"])
                            users_list.append(payload.user_id)
                            var = {"users": users_list}
                            data["voting"][str(payload.guild_id)][str(
                                payload.message_id)].update(var)
                            file.seek(0)
                            json.dump(data, file, indent=4)
                            return
                except KeyError:
                    return

        except Exception as e:
            print(e)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):

        member = self.bot.get_user(payload.user_id)
        if member.bot:
            return

        channel = self.bot.get_channel(payload.channel_id)
        msg = await channel.fetch_message(payload.message_id)

        users = []
        for reaction in msg.reactions:
            async for user in reaction.users():
                users.append(user)

        if member in users:
            return

        with open('./config.json', 'r+') as file:
            data = json.load(file)
            try:
                message_id = data['voting'][str(
                    payload.guild_id)][str(payload.message_id)]

                if data['voting'][str(payload.guild_id)][str(payload.message_id)]["vote_multiple"] is True:
                    return
                else:
                    if payload.user_id in data['voting'][str(payload.guild_id)][str(payload.message_id)]["users"]:
                        user_id_index = data["voting"][str(payload.guild_id)][str(
                            payload.message_id)]["users"].index(payload.user_id)
                        data["voting"][str(payload.guild_id)][str(
                            payload.message_id)]["users"].pop(user_id_index)
                        open("./config.json", "w").write(json.dumps(data,
                                                                    sort_keys=True, indent=4, separators=(',', ': ')))
                        return
                    else:
                        return
            except KeyError:
                return


def setup(bot):
    bot.add_cog(events(bot))
