import discord
from discord.ext import commands
import asyncio
import json
import datetime
import youtube_dl
from botprefix import prefix
from config import splashart_url

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

cap = DesiredCapabilities().CHROME
cap["marionette"] = False

options = Options()
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--headless")

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


class radio(commands.Cog):
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

    @commands.group()
    async def radio(self, ctx):

        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title=f"This Command Is Used Like This: `{prefix(self.bot, ctx)[0]}radio [start | stop]`", colour=0xff0000)
            await ctx.send(embed=embed)
            return

    @radio.command()
    async def start(self, ctx):
        try:
            global i

            def invokeCommand():
                coroutine = ctx.invoke(self.bot.get_command('updatemsg'))
                asyncio.run_coroutine_threadsafe(
                    coroutine, self.bot.loop)
                return

            def after(error):
                global i
                try:
                    if self.bot.voice_client_attributes[str(ctx.guild.id)]['radio'] is False:
                        return
                except:
                    pass
                try:
                    FFMPEG_OPTIONS = {"before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                                        "options": f"-vn -ss {self.bot.voice_client_attributes[str(ctx.guild.id)]['seek_position']}"}
                except:
                    pass

                try:
                    firstIndex = list(
                        self.bot.music[str(ctx.guild.id)].keys())[0]
                    self.bot.music[str(ctx.guild.id)].pop(
                        firstIndex)

                    if not ctx.voice_client.is_playing():
                        driver = webdriver.Chrome(
                            desired_capabilities=cap, options=options)
                        driver.get(
                            "https://www.randomlists.com/random-songs")
                        element = driver.find_element_by_xpath(
                            "/html/body/div/div[1]/main/article/div[2]/ol/li[1]/div/span[1]")
                        author = driver.execute_script("return arguments[0].innerHTML;", element).split(
                            """<span class=" rand_small"="">""")[1]
                        element2 = driver.find_element_by_xpath(
                            "/html/body/div/div[1]/main/article/div[2]/ol/li[1]/div/span[2]")
                        song = driver.execute_script(
                            "return arguments[0].innerHTML;", element2)
                        driver.quit()

                        song = self.search(author + " - " + song)
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

                        ctx.voice_client.play(discord.FFmpegPCMAudio(
                            source=source, **FFMPEG_OPTIONS), after=after)
                        ctx.voice_client.source = discord.PCMVolumeTransformer(
                            ctx.voice_client.source)
                        ctx.voice_client.source.volume = self.bot.voice_client_attributes[str(
                            ctx.guild.id)]['volume'] / 100

                        invokeCommand()
                    else:
                        return
                except:
                    invokeCommand()
                    return

            try:
                try:
                    if ctx.voice_client.is_playing() and self.bot.voice_client_attributes[str(ctx.guild.id)]['radio'] is True or ctx.voice_client.is_playing() is False and ctx.voice_client.is_paused() is True and self.bot.voice_client_attributes[str(ctx.guild.id)]['radio'] is True:
                        embed = discord.Embed(
                            title=f"Radio Is Already Playing!", colour=0xff0000)
                        await ctx.send(embed=embed)
                        return

                    if ctx.voice_client.is_playing() or ctx.voice_client.is_playing() is False and ctx.voice_client.is_paused() is True:
                        embed = discord.Embed(
                            title=f"The Bot Is Already Playing!", colour=0xff0000)
                        await ctx.send(embed=embed)
                        return
                except:
                    pass

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

                        attr = {"radio": True,
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
                        embed3 = discord.Embed(title="You Must Be In The Same Voice Channel As The Bot To Use This Command!",
                                               colour=0xff0000)
                        await ctx.send(embed=embed3)
                        return

                    FFMPEG_OPTIONS = {"before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                                      "options": f"-vn -ss {self.bot.voice_client_attributes[str(ctx.guild.id)]['seek_position']}"}

                    try:
                        driver = webdriver.Chrome(
                            desired_capabilities=cap, options=options)
                        driver.get("https://www.randomlists.com/random-songs")
                        element = driver.find_element_by_xpath(
                            "/html/body/div/div[1]/main/article/div[2]/ol/li[1]/div/span[1]")
                        author = driver.execute_script("return arguments[0].innerHTML;", element).split(
                            """<span class=" rand_small"="">""")[1]
                        element2 = driver.find_element_by_xpath(
                            "/html/body/div/div[1]/main/article/div[2]/ol/li[1]/div/span[2]")
                        song = driver.execute_script(
                            "return arguments[0].innerHTML;", element2)
                        driver.quit()

                        song = self.search(author + " - " + song)
                        source = song['source']
                        details = {"title": song['title'],
                                   "url": str(song['url']),
                                   "duration": str(song['duration']),
                                   "time": str(song['time']),
                                   "thumbnail": str(song['thumbnail']),
                                   "requester": str(ctx.author)}

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

                        if ctx.voice_client is not None:
                            if not ctx.voice_client.is_playing():
                                ctx.voice_client.play(discord.FFmpegPCMAudio(
                                    source=source, **FFMPEG_OPTIONS), after=after)
                                ctx.voice_client.source = discord.PCMVolumeTransformer(
                                    ctx.voice_client.source)
                                ctx.voice_client.source.volume = self.bot.voice_client_attributes[str(
                                    ctx.guild.id)]['volume'] / 100

                                var = {'radio': True}
                                self.bot.voice_client_attributes[str(
                                    ctx.guild.id)].update(var)

                                embed5 = discord.Embed(
                                    title="24/7 Radio...", colour=0x32CD32)
                                embed5.set_author(
                                    name="Started Playing", icon_url="https://media.discordapp.net/attachments/564520348821749766/696332404549222440/4305809_200x130..gif")
                                await ctx.send(embed=embed5)

                                with open('./config.json', 'r+') as file:
                                    data = json.load(file)

                                    try:
                                        channel_id = data['music'][str(
                                            ctx.guild.id)]['channel_id']
                                    except KeyError:
                                        return

                                    channel = self.bot.get_channel(channel_id)
                                    if channel is not None:
                                        try:
                                            msg = await channel.fetch_message(data['music'][str(ctx.guild.id)]['message_id'])
                                        except discord.NotFound:
                                            return

                                        musicList = list(
                                            self.bot.music[str(ctx.guild.id)])
                                        i = 0
                                        skipFirst = 0
                                        complete_list = ""
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

                                                complete_list = complete_list + \
                                                    f"{i + 1}. {title}" + \
                                                    f" [{duration}] - {ctx.guild.get_member_named(requester).mention}\n"
                                                i = i + 1

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

                                        embed = discord.Embed(
                                            description=f"**[{duration}] - [{title}]({url})**\nRequested by {ctx.guild.get_member_named(requester).mention}", color=0x0098ff)
                                        embed.set_image(url=thumbnail)
                                        embed.set_footer(
                                            text=f"{i} {text} in queue | Loop: {loopStatus} | Loop Queue: {loopqueueStatus} | Radio: {radioStatus}")

                                        queue = f"**__Queue list:__**\n{complete_list}"
                                        await msg.edit(content=queue, embed=embed)
                                    else:
                                        return
                        else:
                            return
                    except Exception as e:
                        print(e)
                else:
                    embed7 = discord.Embed(title="You Must Be In A Voice Channel To Use This Command!",
                                           colour=0xff0000)
                    await ctx.send(embed=embed7)
                    return
            except Exception as e:
                print(e)
        except Exception as e:
            print(e)

    @radio.command()
    async def stop(self, ctx):

        async def stopRadioFunc():
            self.bot.music.pop(str(ctx.guild.id), None)
            ctx.voice_client.stop()
            var = {'radio': False}
            self.bot.voice_client_attributes[str(ctx.guild.id)].update(var)
            embed = discord.Embed(
                title="Radio Stopped!", colour=0x0000ff)
            await ctx.send(embed=embed)
            await ctx.message.add_reaction("✅")

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
                    except discord.NotFound:
                        return
                    embed = discord.Embed(
                        title="No music playing currently", color=0x0098ff)
                    embed.set_image(url=splashart_url)
                    embed.set_footer(
                        text=f"Prefix for this server is: {prefix(self.bot, ctx)[0]}")
                    content = "**__Queue list:__**\nJoin a voice channel and queue songs by name or url in here."
                    await msg.edit(content=content, embed=embed)
                    return
                else:
                    return

        try:
            if ctx.author.voice is not None:
                if ctx.voice_client is not None:
                    if ctx.author.voice is not None and ctx.author.voice.channel == ctx.voice_client.channel:
                        if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
                            if self.bot.voice_client_attributes[str(ctx.guild.id)]['radio'] is True:
                                users = ctx.author.voice.channel.members
                                for member in ctx.author.voice.channel.members:
                                    if member.bot:
                                        users.remove(member)
                                if len(users) == 1:
                                    await stopRadioFunc()
                                    return
                                else:
                                    if ctx.author.guild_permissions.administrator:
                                        await stopRadioFunc()
                                        return
                                    else:
                                        if ctx.author.guild_permissions.manage_channels:
                                            await stopRadioFunc()
                                            return
                                        else:
                                            for role in ctx.author.roles:
                                                if role.name == "DJ":
                                                    await stopRadioFunc()
                                                    return
                                            else:
                                                embed2 = discord.Embed(
                                                    description="**You Need `Administrator` Permission Or `DJ` Role Or `Manage Channels` Permission To Use This Command!** (Being Alone With The Bot Also Works.)", colour=0xff0000)
                                                await ctx.send(embed=embed2)
                                                return
                            else:
                                embed = discord.Embed(
                                    title="Radio Is Not Playing!", colour=0xff0000)
                                await ctx.send(embed=embed)
                                return
                        else:
                            embed4 = discord.Embed(
                                title="Radio Is Not Playing!", colour=0xff0000)
                            await ctx.send(embed=embed4)
                            return
                    else:
                        embed5 = discord.Embed(
                            title="You Must Be In The Same Voice Channel As The Bot To Use This Command!", colour=0xff0000)
                        await ctx.send(embed=embed5)
                        return
                else:
                    embed6 = discord.Embed(
                        title="I'm Not Connected To A Voice Channel!", colour=0xff0000)
                    await ctx.send(embed=embed6)
                    return
            else:
                embed7 = discord.Embed(title="You Must Be In A Voice Channel To Use This Command!",
                                       colour=0xff0000)
                await ctx.send(embed=embed7)
                return
        except Exception as e:
            print(e)


def setup(bot):
    bot.add_cog(radio(bot))
