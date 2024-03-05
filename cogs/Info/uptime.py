import discord
import datetime
from discord.ext import commands

start_time = datetime.datetime.utcnow()

class uptime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def uptime(self, ctx):

        now = datetime.datetime.utcnow()
        delta = now - start_time
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)

        if days:
            time_format = "**{d}** days, **{h}** hours, **{m}** minutes, and **{s}** seconds"
            uptime_stamp = time_format.format(
                d=days, h=hours, m=minutes, s=seconds)

            embed = discord.Embed(
                title=f"Uptime - {uptime_stamp}", colour=0xCCCC00)
            await ctx.send(embed=embed)
            await ctx.message.add_reaction("✅")
            return

        if hours:
            time_format = "**{h}** hours, **{m}** minutes, and **{s}** seconds"
            uptime_stamp = time_format.format(
                d=days, h=hours, m=minutes, s=seconds)

            embed2 = discord.Embed(
                title=f"Uptime - {uptime_stamp}", colour=0xCCCC00)
            await ctx.send(embed=embed2)
            await ctx.message.add_reaction("✅")
            return

        if minutes:
            time_format = "**{m}** minutes, and **{s}** seconds"
            uptime_stamp = time_format.format(
                d=days, h=hours, m=minutes, s=seconds)

            embed3 = discord.Embed(
                title=f"Uptime - {uptime_stamp}", colour=0xCCCC00)
            await ctx.send(embed=embed3)
            await ctx.message.add_reaction("✅")
            return

        if seconds:
            time_format = "**{s}** seconds"
            uptime_stamp = time_format.format(
                d=days, h=hours, m=minutes, s=seconds)

            embed4 = discord.Embed(
                title=f"Uptime - {uptime_stamp}", colour=0xCCCC00)
            await ctx.send(embed=embed4)
            await ctx.message.add_reaction("✅")
            return


def setup(bot):
    bot.add_cog(uptime(bot))
