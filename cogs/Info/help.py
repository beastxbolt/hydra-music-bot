import discord
from discord.ext import commands
from botprefix import prefix

class help(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.bot.remove_command('help')

	@commands.command()
	async def help(self, ctx):
			
		embed = discord.Embed(title="➡️ Help Commands List  ⬅️",colour=0x00ff00)
		embed.add_field(name=f"{prefix(self.bot, ctx)[0]}disconnect",value="Clears Queue And Disconnects The Bot From Voice Channel",inline=True)
		embed.add_field(name=f"{prefix(self.bot, ctx)[0]}join",value="Connects The Bot To A Voice Channel",inline=True)
		embed.add_field(name=f"{prefix(self.bot, ctx)[0]}loop",value="Loops The Current Playing Music",inline=True)
		embed.add_field(name=f"{prefix(self.bot, ctx)[0]}loopqueue",value="Loops The Whole Queue",inline=True)
		embed.add_field(name=f"{prefix(self.bot, ctx)[0]}lyrics",value="Gives The Lyrics Of The Query",inline=True)
		embed.add_field(name=f"{prefix(self.bot, ctx)[0]}nowplaying",value="Shows The Current Playing Music",inline=True)
		embed.add_field(name=f"{prefix(self.bot, ctx)[0]}pause",value="Pauses The Playing Music",inline=True)
		embed.add_field(name=f"{prefix(self.bot, ctx)[0]}play [Name/URL]",value="Plays Music With The Given Name or URL (Supports YT Playlist URL)",inline=True)
		embed.add_field(name=f"{prefix(self.bot, ctx)[0]}queue",value="Shows The Music Queue",inline=True)
		embed.add_field(name=f"{prefix(self.bot, ctx)[0]}radio [start|stop]",value="Plays Random Music From YouTube 24/7",inline=True)
		embed.add_field(name=f"{prefix(self.bot, ctx)[0]}remove [position]",value="Removes A Music From The Queue",inline=True)
		embed.add_field(name=f"{prefix(self.bot, ctx)[0]}resume",value="Resumes The Paused Music",inline=True)
		embed.add_field(name=f"{prefix(self.bot, ctx)[0]}seek [timestamp/seconds]",value="Jumps To Any Given Timestamp",inline=True)
		embed.add_field(name=f"{prefix(self.bot, ctx)[0]}setup",value="Creates A New Channel For Playing Music With Emote Controls",inline=True)
		embed.add_field(name=f"{prefix(self.bot, ctx)[0]}shuffle",value="Shuffles The Queue",inline=True)
		embed.add_field(name=f"{prefix(self.bot, ctx)[0]}skip",value="Skips The Current Playing Music",inline=True)
		embed.add_field(name=f"{prefix(self.bot, ctx)[0]}stop",value="Clears Queue And Stops Playing Music",inline=True)
		embed.add_field(name=f"{prefix(self.bot, ctx)[0]}volume [volume]",value="Changes The Volume Of The Current Playing Music",inline=True)
		embed.add_field(name=f"{prefix(self.bot, ctx)[0]}voteskip",value="Skips The Current Playing Music If Enough Users Vote",inline=True)
		embed.add_field(name=f"{prefix(self.bot, ctx)[0]}help",value="Shows This Help Message",inline=True)
		embed.add_field(name=f"{prefix(self.bot, ctx)[0]}ping",value="Shows The Bot's Latency In Milliseconds",inline=True)
		embed.add_field(name=f"{prefix(self.bot, ctx)[0]}prefix",value="Shows And Changes Bot's Server Prefix",inline=True)
		embed.add_field(name=f"{prefix(self.bot, ctx)[0]}uptime",value="Shows The Bot's Uptime",inline=True)
		await ctx.send(embed=embed)
		await ctx.message.add_reaction("✅")
		return


def setup(bot):
	bot.add_cog(help(bot))
