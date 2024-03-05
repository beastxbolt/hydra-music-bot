import discord
from discord.ext import commands
import json

class ping(commands.Cog):
	def __init__(self, bot):
		self.bot = bot


	@commands.command()
	async def ping(self, ctx):

		with open('./config.json', 'r+') as file:
			data = json.load(file)
			try:
				if ctx.author.id in data["blacklist"][str(ctx.guild.id)]:
					await ctx.message.delete()
					embed = discord.Embed(
						title=f":octagonal_sign: You Have Been Banned From Using `{self.bot.user.name}` Bot In `{ctx.guild.name}` Server. :octagonal_sign:", description="Contact Server Owner Or Admins For More Info...", colour=0xa300ff)
					await ctx.author.send(embed=embed)
					return
				else:
					pass
			except KeyError:
				pass

		await ctx.send(f"📡 Ping - {round(self.bot.latency * 1000)}ms")
		await ctx.message.add_reaction("✅")
		return


def setup(bot):
	bot.add_cog(ping(bot))
