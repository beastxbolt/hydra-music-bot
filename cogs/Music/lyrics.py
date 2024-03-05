import discord
from discord.ext import commands
import asyncio
import lyricsgenius
from botprefix import prefix
from config import lyrics_genius_token

class lyrics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def lyrics(self, ctx, *, query : str = None):

        if query is None:
            embed = discord.Embed(title=f"This Command Is Used Like This: `{prefix(self.bot, ctx)[0]}lyrics [query]`", color=0xff0000)
            await ctx.send(embed=embed)
            return
        else:
            try:
                genius = lyricsgenius.Genius(lyrics_genius_token)
                song = genius.search_song(query)
                title = song.title
                artist = song.artist
                lyrics = song.lyrics
                lyrics_list = [lyrics[i:i+2048] for i in range(0, len(lyrics), 2048)]

                i = 0
                for lyrics in lyrics_list:
                    if i == 0:
                        embed = discord.Embed(title=f"Title: {title}\nAuthor: {artist}", color=0x33FF9E, description=lyrics)
                        await ctx.send(embed=embed)
                        i += 1
                        continue
                    if i == 1:
                        embed = discord.Embed(color=0x33FF9E, description=lyrics)
                        await ctx.send(embed=embed)
                    await asyncio.sleep(1)
                await ctx.message.add_reaction("✅")
                return
            except:
                embed = discord.Embed(title="No Lyrics Found!", color=0xff0000)
                await ctx.send(embed=embed)
                return

def setup(bot):
    bot.add_cog(lyrics(bot))
