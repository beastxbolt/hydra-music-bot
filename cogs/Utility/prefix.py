import discord
import asyncio
from discord.ext import commands
import json
from botprefix import prefix as p

class prefix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def prefix(self, ctx, *, new_prefix : str = None):

        if new_prefix is None:
            await ctx.send(f"{ctx.author.mention}, The command prefix is `{p(self.bot, ctx)[0]}`.\nTo run commands, use `{p(self.bot, ctx)[0]} command` or `@{self.bot.user} command`.")
            return

        if new_prefix is not None:
            with open("./prefix.json", "r") as f:
                prefixes = json.load(f)
                id = str(ctx.guild.id)
                jsonprefix = prefixes.get(id)

                if jsonprefix is None:
                    prefixes[str(ctx.guild.id)] = []
                    prefixes[str(ctx.guild.id)].append(new_prefix)
                    prefixes[str(ctx.guild.id)].append(f"<@!{self.bot.user.id}>")
                    with open("./prefix.json", "w") as f:
                        json.dump(prefixes, f)
                        f.close()
                        await ctx.send(f"{ctx.author.mention},  prefix has been set to `{new_prefix}`.\nTo run commands, use `{p(self.bot, ctx)[0]} command` or `@{self.bot.user} command`.")
                        return

                else:
                    prefixes[str(ctx.guild.id)] = []
                    prefixes[str(ctx.guild.id)].append(new_prefix)
                    prefixes[str(ctx.guild.id)].append(f"<@!{self.bot.user.id}>")
                    with open("./prefix.json", "w") as f:
                        json.dump(prefixes, f)
                        f.close()
                        await ctx.send(f"{ctx.author.mention},  prefix has been set to `{new_prefix}`.\nTo run commands, use `{p(self.bot, ctx)[0]} command` or `@{self.bot.user} command`.")
                        return
                        
def setup(bot):
	bot.add_cog(prefix(bot))