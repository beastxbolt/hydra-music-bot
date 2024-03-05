import discord
from discord.ext import commands
import asyncio
import json
import datetime
import youtube_dl
import googleapiclient.discovery
from urllib.parse import parse_qs, urlparse
from botprefix import prefix
from config import developer_key, spotify_client_id, spotify_client_secret
import spotipy
from spotipy import SpotifyClientCredentials

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
spotify = spotipy.Spotify(
    client_credentials_manager=client_credentials_manager)


class play(commands.Cog):
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

    @commands.command(aliases=['p'])
    async def play(self, ctx, *, query: str = None):
        global i

        def invokeCommand():
            coroutine = ctx.invoke(self.bot.get_command('updatemsg'))
            asyncio.run_coroutine_threadsafe(
                coroutine, self.bot.loop)
            return

        def invokeCheckVC():
            coroutine = ctx.invoke(self.bot.get_command('checkvc'))
            asyncio.run_coroutine_threadsafe(
                coroutine, self.bot.loop)
            return

        if query is None:
            embed = discord.Embed(
                title=f"This Command Is Used Like This: `{prefix(self.bot, ctx)[0]}play [URL/Name]`", colour=0xff0000)
            await ctx.send(embed=embed)
            return

        with open('./config.json', 'r+') as file:
            data = json.load(file)

            try:
                channel_id = data['music'][str(ctx.guild.id)]['channel_id']

                channel = self.bot.get_channel(channel_id)
                if channel is not None:
                    try:
                        msg = await channel.fetch_message(data['music'][str(ctx.guild.id)]['message_id'])
                        embed = discord.Embed(
                            description=f"This command is restricted to {channel.mention}. Send music name or url to play.", color=0xffa200)
                        await ctx.send(embed=embed)
                        return
                    except discord.NotFound:
                        pass
                else:
                    pass
            except KeyError:
                pass

        def after(error):
            try:
                FFMPEG_OPTIONS = {"before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                                  "options": f"-vn -ss {self.bot.voice_client_attributes[str(ctx.guild.id)]['seek_position']}"}
            except:
                pass
            try:
                try:
                    if self.bot.voice_client_attributes[str(ctx.guild.id)]['seek'] is True:
                        pass
                    else:
                        try:
                            if self.bot.voice_client_attributes[str(ctx.guild.id)]['loop'] is True and self.bot.voice_client_attributes[str(ctx.guild.id)]['loop_queue'] is True:
                                pass
                            if self.bot.voice_client_attributes[str(ctx.guild.id)]['loop'] is True and self.bot.voice_client_attributes[str(ctx.guild.id)]['loop_queue'] is False:
                                pass
                            if self.bot.voice_client_attributes[str(ctx.guild.id)]['loop'] is False and self.bot.voice_client_attributes[str(ctx.guild.id)]['loop_queue'] is False:
                                firstIndex = list(
                                    self.bot.music[str(ctx.guild.id)].keys())[0]
                                self.bot.music[str(ctx.guild.id)].pop(
                                    firstIndex)
                            if self.bot.voice_client_attributes[str(ctx.guild.id)]['loop'] is False and self.bot.voice_client_attributes[str(ctx.guild.id)]['loop_queue'] is True:
                                var = {'move_queue_to_last': True}
                                self.bot.voice_client_attributes[str(
                                    ctx.guild.id)].update(var)
                        except:
                            pass
                except:
                    pass

                try:
                    try:
                        if self.bot.voice_client_attributes[str(ctx.guild.id)]['move_queue_to_last'] is True:
                            for key, value in self.bot.music[str(ctx.guild.id)].items():
                                firstIndexKey = key
                                break

                            firstIndex = list(
                                self.bot.music[str(ctx.guild.id)].keys())[0]
                            poppedFirstIndexValue = self.bot.music[str(
                                ctx.guild.id)].pop(firstIndex)
                            self.bot.music[str(
                                ctx.guild.id)][firstIndexKey] = poppedFirstIndexValue

                            queueFirstIndex = list(
                                self.bot.music[str(ctx.guild.id)])[0]
                            checkQueue = self.bot.music[str(ctx.guild.id)][
                                queueFirstIndex]["title"]
                            requester = self.bot.music[str(
                                ctx.guild.id)][str(queueFirstIndex)]['requester']

                            var = {'move_queue_to_last': False}
                            self.bot.voice_client_attributes[str(
                                ctx.guild.id)].update(var)

                        else:
                            queueFirstIndex = list(
                                self.bot.music[str(ctx.guild.id)])[0]
                            checkQueue = self.bot.music[str(ctx.guild.id)][
                                queueFirstIndex]["title"]
                            requester = self.bot.music[str(ctx.guild.id)][str(
                                queueFirstIndex)]['requester']

                        if not ctx.voice_client.is_playing():
                            song = self.bot.music[str(ctx.guild.id)][queueFirstIndex]
                            source = song['source']

                            try:
                                findUpcoming = list(
                                    self.bot.music[str(ctx.guild.id)])[1]
                                upcoming = self.bot.music[str(
                                    ctx.guild.id)][str(findUpcoming)]['title']
                            except IndexError:
                                upcoming = "None"

                            ctx.voice_client.play(discord.FFmpegPCMAudio(
                                source=source, **FFMPEG_OPTIONS), after=after)
                            ctx.voice_client.source = discord.PCMVolumeTransformer(
                                ctx.voice_client.source)
                            ctx.voice_client.source.volume = self.bot.voice_client_attributes[str(
                                ctx.guild.id)]['volume'] / 100

                            var = {'seek': False, 'seek_position': '0'}
                            self.bot.voice_client_attributes[str(
                                ctx.guild.id)].update(var)

                            if self.bot.voice_client_attributes[str(ctx.guild.id)]['send_play_embed'] is True:
                                embedx = discord.Embed(
                                    colour=0x32CD32)
                                embedx.add_field(
                                    name="Title", value=f"**[{song['title']}]({song['url']})**", inline=False)
                                embedx.add_field(
                                    name="Channel Name", value=song['channel'], inline=False)
                                embedx.add_field(
                                    name="Duration", value=song['duration'], inline=False)
                                embedx.add_field(
                                    name="Requested By", value=requester, inline=False)
                                embedx.add_field(
                                    name="Upcoming", value=upcoming, inline=False)
                                embedx.set_thumbnail(
                                    url=song['thumbnail'])
                                embedx.set_author(
                                    name="Started Playing", icon_url="https://media.discordapp.net/attachments/564520348821749766/696332404549222440/4305809_200x130..gif")
                                coroutine = ctx.send(embed=embedx)
                                asyncio.run_coroutine_threadsafe(
                                    coroutine, self.bot.loop)
                                invokeCommand()
                                return
                            else:
                                var = {'send_play_embed': True}
                                self.bot.voice_client_attributes[str(
                                    ctx.guild.id)].update(var)
                                return
                        else:
                            return
                    except IndexError:
                        try:
                            invokeCommand()
                            invokeCheckVC()
                            return
                        except Exception as e:
                            print(e)
                except KeyError:
                    try:
                        invokeCommand()
                        invokeCheckVC()
                        return
                    except Exception as e:
                        print(e)

            except Exception as e:
                print(e)
                return

        try:
            if ctx.author.voice is not None:
                vc = ctx.author.voice.channel

                if not ctx.voice_client or not ctx.voice_client.is_connected():
                    user = await ctx.guild.fetch_member(self.bot.user.id)
                    if user.permissions_in(ctx.author.voice.channel).connect is False:
                        embed = discord.Embed(
                            title="Bot requires Connect permission(s) to run this command.", colour=0xff0000)
                        await ctx.channel.send(embed=embed)
                        return

                    if user.permissions_in(ctx.author.voice.channel).speak is False:
                        embed = discord.Embed(
                            title="Bot requires Speak permission(s) to run this command.", colour=0xff0000)
                        await ctx.channel.send(embed=embed)
                        return

                    self.bot.music.pop(str(ctx.guild.id), None)
                    self.bot.voice_client_attributes.pop(
                        str(ctx.guild.id), None)
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
                        str(ctx.guild.id))
                    if value is None:
                        self.bot.voice_client_attributes[str(
                            ctx.guild.id)] = attr
                    else:
                        pass

                    embed2 = discord.Embed(
                        title=f"✅ Connected To `{vc.name}` ✅", colour=0xFF69B4)
                    await ctx.send(embed=embed2)

                if ctx.voice_client.is_connected() and vc != ctx.voice_client.channel:
                    embed3 = discord.Embed(title="You Must Be In The Same Voice Channel As The Bot To Use This Command.",
                                           colour=0xff0000)
                    await ctx.send(embed=embed3)
                    return

                if self.bot.voice_client_attributes[str(ctx.guild.id)]['radio'] is False:
                    FFMPEG_OPTIONS = {"before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                                      "options": f"-vn -ss {self.bot.voice_client_attributes[str(ctx.guild.id)]['seek_position']}"}

                    try:
                        query = query.strip('<>')

                        try:
                            if "youtube.com/playlist?list=" in query or "youtu.be/playlist?list=" in query or "youtube.com/watch?v=" and "&list=" in query or "youtu.be/" and "&list=" in query:
                                var = {'block_skip_and_stop': True}
                                self.bot.voice_client_attributes[str(
                                    ctx.guild.id)].update(var)

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

                                msg = await ctx.send(f"0/{len(playlist_items)} Music Added To Queue.")
                                for vid in playlist_items:
                                    try:
                                        vidIndex = playlist_items.index(
                                            vid) + 1
                                        totalIndex = len(playlist_items)
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
                                                   "requester": str(ctx.author),
                                                   "is_spotify": song['is_spotify']}

                                        value = self.bot.music.get(
                                            str(ctx.guild.id))
                                        if value is None:
                                            self.bot.music[str(
                                                ctx.guild.id)] = {}
                                        else:
                                            pass
                                        if str(song['title']) in self.bot.music[str(ctx.guild.id)]:
                                            self.bot.music[str(ctx.guild.id)
                                                           ][str(song['title']) + f" ({i})"] = {}
                                            self.bot.music[str(ctx.guild.id)][str(
                                                song['title']) + f" ({i})"] = details
                                            i += 1
                                        else:
                                            self.bot.music[str(ctx.guild.id)
                                                           ][str(song['title'])] = {}
                                            self.bot.music[str(ctx.guild.id)][str(
                                                song['title'])] = details

                                        try:
                                            findUpcoming = list(
                                                self.bot.music[str(ctx.guild.id)])[1]
                                            upcoming = self.bot.music[str(
                                                ctx.guild.id)][str(findUpcoming)]['title']
                                        except IndexError:
                                            upcoming = "None"

                                        if ctx.voice_client is not None:
                                            if not ctx.voice_client.is_playing():
                                                ctx.voice_client.play(discord.FFmpegPCMAudio(
                                                    source=source, **FFMPEG_OPTIONS), after=after)
                                                ctx.voice_client.source = discord.PCMVolumeTransformer(
                                                    ctx.voice_client.source)
                                                ctx.voice_client.source.volume = self.bot.voice_client_attributes[str(
                                                    ctx.guild.id)]['volume'] / 100

                                                embed5 = discord.Embed(
                                                    colour=0x32CD32)
                                                embed5.add_field(
                                                    name="Title", value=f"**[{song['title']}]({song['url']})**", inline=False)
                                                embed5.add_field(
                                                    name="Channel Name", value=song['channel'], inline=False)
                                                embed5.add_field(
                                                    name="Duration", value=song['duration'], inline=False)
                                                embed5.add_field(
                                                    name="Requested By", value=ctx.author, inline=False)
                                                embed5.add_field(
                                                    name="Upcoming", value=upcoming, inline=False)
                                                embed5.set_thumbnail(
                                                    url=song['thumbnail'])
                                                embed5.set_author(
                                                    name="Started Playing", icon_url="https://media.discordapp.net/attachments/564520348821749766/696332404549222440/4305809_200x130..gif")
                                                await ctx.send(embed=embed5)
                                        else:
                                            return
                                        await msg.edit(content=f"{vidIndex}/{totalIndex} Music Added To Queue.")
                                    except:
                                        continue
                                await msg.edit(content="All Available Music From YouTube Playlist Added To Queue.")
                                await ctx.message.add_reaction("✅")
                                var = {'block_skip_and_stop': False}
                                self.bot.voice_client_attributes[str(
                                    ctx.guild.id)].update(var)
                                return

                            if "open.spotify.com/playlist" in query:
                                var = {'block_skip_and_stop': True}
                                self.bot.voice_client_attributes[str(
                                    ctx.guild.id)].update(var)

                                playlist = spotify.playlist_tracks(query)

                                msg = await ctx.send(f"0/{len(playlist['items'])} Music Added To Queue.")
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
                                        time = song['time']
                                        duration = song['duration']

                                        details = {"title": title,
                                                "url": url,
                                                "source": source,
                                                "duration": str(duration),
                                                "time": str(time),
                                                "thumbnail": thumbnail,
                                                "channel": channel,
                                                "requester": str(ctx.author),
                                                "is_spotify": True}

                                        value = self.bot.music.get(
                                            str(ctx.guild.id))
                                        if value is None:
                                            self.bot.music[str(
                                                ctx.guild.id)] = {}
                                        else:
                                            pass
                                        if str(title) in self.bot.music[str(ctx.guild.id)]:
                                            self.bot.music[str(ctx.guild.id)
                                                        ][str(title) + f" ({i})"] = {}
                                            self.bot.music[str(ctx.guild.id)][str(
                                                title) + f" ({i})"] = details
                                            i += 1
                                        else:
                                            self.bot.music[str(ctx.guild.id)
                                                        ][str(title)] = {}
                                            self.bot.music[str(ctx.guild.id)][str(
                                                title)] = details

                                        try:
                                            findUpcoming = list(
                                                self.bot.music[str(ctx.guild.id)])[1]
                                            upcoming = self.bot.music[str(
                                                ctx.guild.id)][str(findUpcoming)]['title']
                                        except IndexError:
                                            upcoming = "None"

                                        if ctx.voice_client is not None:
                                            if not ctx.voice_client.is_playing():
                                                ctx.voice_client.play(discord.FFmpegPCMAudio(
                                                    source=source, **FFMPEG_OPTIONS), after=after)
                                                ctx.voice_client.source = discord.PCMVolumeTransformer(
                                                    ctx.voice_client.source)
                                                ctx.voice_client.source.volume = self.bot.voice_client_attributes[str(
                                                    ctx.guild.id)]['volume'] / 100

                                                embed5 = discord.Embed(
                                                    colour=0x32CD32)
                                                embed5.add_field(
                                                    name="Title", value=f"**[{title}]({url})**", inline=False)
                                                embed5.add_field(
                                                    name="Channel Name", value=channel, inline=False)
                                                embed5.add_field(
                                                    name="Duration", value=duration, inline=False)
                                                embed5.add_field(
                                                    name="Requested By", value=ctx.author, inline=False)
                                                embed5.add_field(
                                                    name="Upcoming", value=upcoming, inline=False)
                                                embed5.set_thumbnail(
                                                    url=thumbnail)
                                                embed5.set_author(
                                                    name="Started Playing", icon_url="https://media.discordapp.net/attachments/564520348821749766/696332404549222440/4305809_200x130..gif")
                                                await ctx.send(embed=embed5)
                                        else:
                                            return
                                        await msg.edit(content=f"{itemIndex}/{totalIndex} Music Added To Queue.")
                                    except:
                                        continue
                                await msg.edit(content="All Available Music From Spotify Playlist Added To Queue.")
                                await ctx.message.add_reaction("✅")
                                var = {'block_skip_and_stop': False}
                                self.bot.voice_client_attributes[str(
                                    ctx.guild.id)].update(var)
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
                                           "requester": str(ctx.author),
                                           "is_spotify": song['is_spotify']}

                                value = self.bot.music.get(str(ctx.guild.id))
                                if value is None:
                                    self.bot.music[str(ctx.guild.id)] = {}
                                else:
                                    pass
                                if str(song['title']) in self.bot.music[str(ctx.guild.id)]:
                                    self.bot.music[str(ctx.guild.id)
                                                   ][str(song['title']) + f" ({i})"] = {}
                                    self.bot.music[str(ctx.guild.id)][str(
                                        song['title']) + f" ({i})"] = details
                                    i += 1
                                else:
                                    self.bot.music[str(ctx.guild.id)
                                                   ][str(song['title'])] = {}
                                    self.bot.music[str(ctx.guild.id)][str(
                                        song['title'])] = details

                                embed4 = discord.Embed(
                                    colour=0xffff00)
                                embed4.add_field(
                                    name="Queued", value=f"**[{song['title']}]({song['url']})** [{ctx.author.mention}]", inline=False)
                                embed4.set_author(
                                    name="Song Queued", icon_url="https://media.discordapp.net/attachments/564520348821749766/696334217205907516/giphy.gif")
                                await ctx.send(embed=embed4)

                                try:
                                    findUpcoming = list(
                                        self.bot.music[str(ctx.guild.id)])[1]
                                    upcoming = self.bot.music[str(
                                        ctx.guild.id)][str(findUpcoming)]['title']
                                except IndexError:
                                    upcoming = "None"

                                if ctx.voice_client is not None:
                                    if not ctx.voice_client.is_playing():
                                        ctx.voice_client.play(discord.FFmpegPCMAudio(
                                            source=source, **FFMPEG_OPTIONS), after=after)
                                        ctx.voice_client.source = discord.PCMVolumeTransformer(
                                            ctx.voice_client.source)
                                        ctx.voice_client.source.volume = self.bot.voice_client_attributes[str(
                                            ctx.guild.id)]['volume'] / 100

                                        embed5 = discord.Embed(colour=0x32CD32)
                                        embed5.add_field(
                                            name="Title", value=f"**[{song['title']}]({song['url']})**", inline=False)
                                        embed5.add_field(
                                            name="Channel Name", value=song['channel'], inline=False)
                                        embed5.add_field(
                                            name="Duration", value=song['duration'], inline=False)
                                        embed5.add_field(
                                            name="Requested By", value=ctx.author, inline=False)
                                        embed5.add_field(
                                            name="Upcoming", value=upcoming, inline=False)
                                        embed5.set_thumbnail(
                                            url=song['thumbnail'])
                                        embed5.set_author(
                                            name="Started Playing", icon_url="https://media.discordapp.net/attachments/564520348821749766/696332404549222440/4305809_200x130..gif")
                                        await ctx.send(embed=embed5)
                                        await ctx.message.add_reaction("✅")
                                        return
                                    else:
                                        await ctx.message.add_reaction("✅")
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
                                           "requester": str(ctx.author),
                                           "is_spotify": song['is_spotify']}

                                value = self.bot.music.get(str(ctx.guild.id))
                                if value is None:
                                    self.bot.music[str(ctx.guild.id)] = {}
                                else:
                                    pass
                                if str(song['title']) in self.bot.music[str(ctx.guild.id)]:
                                    self.bot.music[str(ctx.guild.id)
                                                   ][str(song['title']) + f" ({i})"] = {}
                                    self.bot.music[str(ctx.guild.id)][str(
                                        song['title']) + f" ({i})"] = details
                                    i += 1
                                else:
                                    self.bot.music[str(ctx.guild.id)
                                                   ][str(song['title'])] = {}
                                    self.bot.music[str(ctx.guild.id)][str(
                                        song['title'])] = details

                                embed4 = discord.Embed(
                                    colour=0xffff00)
                                embed4.add_field(
                                    name="Queued", value=f"**[{song['title']}]({song['url']})** [{ctx.author.mention}]", inline=False)
                                embed4.set_author(
                                    name="Song Queued", icon_url="https://media.discordapp.net/attachments/564520348821749766/696334217205907516/giphy.gif")
                                await ctx.send(embed=embed4)

                                try:
                                    findUpcoming = list(
                                        self.bot.music[str(ctx.guild.id)])[1]
                                    upcoming = self.bot.music[str(
                                        ctx.guild.id)][str(findUpcoming)]['title']
                                except IndexError:
                                    upcoming = "None"

                                if ctx.voice_client is not None:
                                    if not ctx.voice_client.is_playing():
                                        ctx.voice_client.play(discord.FFmpegPCMAudio(
                                            source=source, **FFMPEG_OPTIONS), after=after)
                                        ctx.voice_client.source = discord.PCMVolumeTransformer(
                                            ctx.voice_client.source)
                                        ctx.voice_client.source.volume = self.bot.voice_client_attributes[str(
                                            ctx.guild.id)]['volume'] / 100

                                        embed5 = discord.Embed(colour=0x32CD32)
                                        embed5.add_field(
                                            name="Title", value=f"**[{song['title']}]({song['url']})**", inline=False)
                                        embed5.add_field(
                                            name="Channel Name", value=song['channel'], inline=False)
                                        embed5.add_field(
                                            name="Duration", value=song['duration'], inline=False)
                                        embed5.add_field(
                                            name="Requested By", value=ctx.author, inline=False)
                                        embed5.add_field(
                                            name="Upcoming", value=upcoming, inline=False)
                                        embed5.set_thumbnail(
                                            url=song['thumbnail'])
                                        embed5.set_author(
                                            name="Started Playing", icon_url="https://media.discordapp.net/attachments/564520348821749766/696332404549222440/4305809_200x130..gif")
                                        await ctx.send(embed=embed5)
                                        await ctx.message.add_reaction("✅")
                                    else:
                                        await ctx.message.add_reaction("✅")
                                else:
                                    return

                        except Exception as e:
                            print(e)
                            embed6 = discord.Embed(
                                title=f"No Such Song Found.", colour=0xff0000)
                            await ctx.send(embed=embed6)
                            return

                    except Exception as e:
                        print(e)
                else:
                    embed = discord.Embed(title="Cannot Play Music While Radio Is Playing.",
                                          description="Use `radio stop` Command To Stop The Radio.", colour=0xff0000)
                    await ctx.send(embed=embed)
                    return
            else:
                embed7 = discord.Embed(title="You Must Be In A Voice Channel To Use This Command.",
                                       colour=0xff0000)
                await ctx.send(embed=embed7)
                return
        except Exception as e:
            print(e)


def setup(bot):
    bot.add_cog(play(bot))
